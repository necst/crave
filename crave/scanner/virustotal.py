from .scanner import Scanner
import logging
import requests
from time import sleep

l = logging.getLogger('crave.scanner.virustotal')


class VirusTotal(Scanner):

    #TODO: support special upload URL for samples > 200MB

    short_name = "virustotal"

    VT_RES_URL = 'https://www.virustotal.com/vtapi/v2/file/report'
    VT_SCAN_URL = 'https://www.virustotal.com/vtapi/v2/file/scan'
    VT_RESCAN_URL = 'https://www.virustotal.com/vtapi/v2/file/rescan'
    MAX_QUERIES = 5
    QUERY_SLEEP = 10

    HEADERS = {
        "Accept-Encoding": "gzip, deflate",
        "User-Agent" : "gzip,  CRAVE framework"
    }

    def query(self, resources):
        params = {'apikey': self._vt_key, 'resource': ','.join(resources)}

        try:
            response = requests.get(
                    Scanner.VT_RES_URL, params=params, headers=self.HEADERS)
            report = response.json()
        except Exception as e:
            l.exception('Cannot query VT for %s (%s)',
                        sample.name, sample.sha256)
            return None

    def submit(self, sample, rescan=False):

        l.debug('Submitting %s for analysis', sample.sha256)
        params = {'apikey': self._vt_key}
        files = {'file': (sample.file, open(sample.file, 'rb'))}

        if not rescan:
            try:
                response = requests.post(
                    self.VT_SCAN_URL,
                    files=files,
                    params=params,
                    headers=self.HEADERS)
                resp_json = response.json()

            except Exception as e:
                l.exception('Cannot submit sample %s', sample.file)
                return None

            if resp_json['response_code'] == 0:
                l.error('Failed submission of %s (%s)!',
                        sample.file, sample.sha256)
                return resp_json

            s = Scan(sample, uuid=resp_json['scan_id'], pending=True)
            # queued for analysis
            return self.project.db.put_scan(resp_json, sample)

            # return a Scan object
            return s
        else:
            raise NotImplementedError('Rescan not yet implemented')

    def query(self, samples=[], no_submit=False):

        def _query_vt(resources):
            try:
                l.debug('Querying resources %s', resources)
                params = {'apikey': self._vt_key, 'resource': ','.join(resources)}
                response = requests.post(self.VT_RES_URL, params=params, headers=self.HEADERS)
                res = response.json()

                if not isinstance(res, (tuple, list)):
                    res = [res, ]
                return res

            except Exception as e:
                l.exception('Error querying VT!')
                return None

        # get pending scans submitted with submit()

        scans = self.get_pending_scans()

        resources = {}
        for s in scans:
            resources[s.extra["resource"]] = s

        while len(resources) > 0:
            processed = 0
            queries = 0
            r = _query_vt(resources.keys()[:25])
            to_process = len(r)

            for res in r:
                queries += 1

                if res['response_code'] == 0:
                    continue

                processed += 1
                scan_results = []

                for av, r in res['scans']:
                    scans_results.append(
                        self.project.ScanResult(
                            sample=res['sha256'], scanner=self,
                            uuid=None, av=av,
                            label=None if r['detected'] is False else r['result'],
                            version=r['version'], update=r['update']))

                scan = resources.pop(res['resource'])
                scan.scan_results = scan_results
                scan.pending = False

                self.project.db.put_scan(scan) # this will also update scan_results accordingly

            l.debug('Updated scans for %s', res['sha256'])

            if queries >= to_process * self.MAX_QUERIES:
                break       # until MAX_QUERIES hit
            if processed < to_process:
                    l.debug('Waiting for more scans to be completed')
                    sleep(self.QUERY_SLEEP)    # wait for more analysis to come
                    continue


    def scan_all(self):
        for s in self.project.db.all_samples:
            self.submit(s)

    def query_all(self):
        samples = self.project.db.all_samples
        res = self.query(samples)
        return res

    def set_key(self, vt_key):
        self._vt_key = vt_key

        if self._vt_key is None:
            l.warning('No VirusTotal Key given, scanning won\'t work')
