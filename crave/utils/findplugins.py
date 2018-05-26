import os
import logging

"""def _do_import():
    '''Does the dirty stuff with __import__'''
    old_syspath = sys.path[:]
    try:
        sys.path += ['.', self.base_dir]
        self.module = __import__(self.name, globals(), None, ['plugin'])
        if hasattr(self.module, 'plugin'):
            self.module = self.module.plugin
    except Exception, reason:
        log.warning('error importing "%s": %s' % (self.name, reason))
        self.module = None
    finally:
        sys.path = old_syspath"""

def find_subclasses(path, cls):
    """
    Find all subclass of cls in py files located below path
    (does look in sub directories)

    @param path: the path to the top level folder to walk
    @type path: str
    @param cls: the base class that all subclasses should inherit from
    @type cls: class
    @rtype: list
    @return: a list if classes that are subclasses of cls
    """

    subclasses=[]

    def look_for_subclass(modulename):
        logging.debug("searching %s" % (modulename))
        module=__import__(modulename)

        #walk the dictionaries to get to the last one
        d=module.__dict__
        for m in modulename.split('.')[1:]:
            d=d[m].__dict__

        #look through this dictionary for things
        #that are subclass of Job
        #but are not Job itself
        for key, entry in d.items():
            if key == cls.__name__:
                continue

            try:
                if issubclass(entry, cls):
                    logging.debug("Found subclass: "+key)
                    subclasses.append(entry)
            except TypeError:
                #this happens when a non-type is passed in to issubclass. We
                #don't care as it can't be a subclass of Job if it isn't a
                #type
                continue

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".py") and not name.startswith("__"):
                path = os.path.join(root, name)
                modulename = path.rsplit('.', 1)[0].replace('/', '.')
                look_for_subclass(modulename)

    return subclasses
