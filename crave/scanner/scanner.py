from crave.plugin import Plugin
import logging

l = logging.getLogger('crave.scanner')

class Scanner(Plugin):

    VT_RES_URL = 'https://www.virustotal.com/vtapi/v2/file/report'
    VT_RESCAN_URL = 'https://www.virustotal.com/vtapi/v2/file/rescan'

    def _init_plugin(self, *args, **kwargs):

        super(Scanner, self)._init_plugin(*args, **kwargs)

        self._vt_key = self.project._vt_key

        if self._vt_key is None:
            l.warning('No VirusTotal Key given, scanning won\'t work')

    def query(self, resources):
        params = {'apikey': self._vt_key, 'resource': ','.join(resources)}

        try:
            response = requests.get(Scanner.VT_RES_URL, params=params)
            report = response.json()
        except Exception as e:
            l.exception('Cannot query VT for %s (%s)', sample.name, sample.sha256)
            return None

    def submit(self, sample):
        pass

    def query(self):
        print(self.project.all_samples)

    def scan_all(self):
        for s in self.project.db.all_samples:
            l.debug('Submitting %s for analysis', s.sha256)
            # self.submit(s)
            # raise Exception('Exceptlol')
