from crave.plugin import Plugin
import logging

l = logging.getLogger('crave.scanner')

class Scanner(Plugin):
    
    def _init_plugin(self, *args, **kwargs):

        super(Scanner, self)._init_plugin(*args, **kwargs)
        self._vt_key = self.project._vt_key

        if self._vt_key is None:
            l.warning('No VirusTotal Key given, scanning won\'t work')
