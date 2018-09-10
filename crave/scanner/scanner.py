from ..plugin import Plugin
import logging

l = logging.getLogger('crave.scanner')


class Scanner(Plugin):

    short_name = "scan_plugin"

    def _init_plugin(self, *args, **kwargs):

        super(Scanner, self)._init_plugin(*args, **kwargs)
        self.project.scanners[self.short_name] = self
        l.debug("Added %s to the list of available scanners", self.short_name)

    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

    def get_pending_scans(self):
        self.project.db.get_pending_scans(self)
