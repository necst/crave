from crave.plugin import Plugin
import logging
import requests
from time import sleep


l = logging.getLogger('crave.scanner')


class Scanner(Plugin):

    VT_RES_URL = 'https://www.virustotal.com/vtapi/v2/file/report'
    VT_SCAN_URL = 'https://www.virustotal.com/vtapi/v2/file/scan'
    VT_RESCAN_URL = 'https://www.virustotal.com/vtapi/v2/file/rescan'
    MAX_QUERIES = 5
    QUERY_SLEEP = 10

    HEADERS = {
        "Accept-Encoding": "gzip, deflate",
        "User-Agent" : "gzip,  CRAVE framework"
    }

    def _init_plugin(self, *args, **kwargs):

        super(Scanner, self)._init_plugin(*args, **kwargs)

        self._vt_key = self.project._vt_key

        if self._vt_key is None:
            l.warning('No VirusTotal Key given, scanning won\'t work')

    def query(self, resources):
        params = {'apikey': self._vt_key, 'resource': ','.join(resources)}

        try:
            response = requests.get(Scanner.VT_RES_URL, params=params, headers=self.HEADERS)
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

            # queued for analysis
            self.project.db.put_scan(resp_json, sample)
        else:
            raise NotImplementedError('Rescan not yet implemented')

    def query(self, samples=[]):

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

        resources = []
        for s in samples:
            r = self.project.db.get_scan(s)
            if r:
                resources.append(r['resource'])
            else:
                l.debug('No scans present for %s', s.sha256)


        while len(resources) > 0:
            processed = 0
            queries = 0
            r = _query_vt(resources[:25])
            to_process = len(r)

            for res in r:
                queries += 1

                if res['response_code'] == 0:
                    continue

                processed += 1
                resources.remove(res['resource'])

                scan = self.project.db.get_scan(sha256=res['sha256'])
                scan.update(res)
                self.project.db.put_scan(scan, sha256=res['sha256'])
                l.debug('Updated scans for %s:', res['sha256'])


            if queries >= to_process * self.MAX_QUERIES:
                break       # until MAX_QUERIES hit
            if processed < to_process:
                    l.debug('Waiting for more scans to be completed')
                    sleep(self.QUERY_SLEEP)    # wait for more analysis to come
                    continue

    def scan_all(self):
        for s in self.project.db.all_samples:
            break
            self.submit(s)

    def query_all(self):
        # TODO batch request with X samples per request
        samples = self.project.db.all_samples
        res = self.query(samples)
        return res
