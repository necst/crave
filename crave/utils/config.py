import os
try:
    import json
except ImportError:
    import simplejson as json

import logging

class Configuration():
    '''class that defines the methods for reading/writing a config file,
    the configuration strings are saved into the config variable
    the configuration is saved in the local data dictionary'''

    def __init__(self, d):
        '''constructor'''

        self.__dict__ = d
        for k, v in self.__dict__.iteritems():
            if v.__class__ is dict:
                self.__dict__[k] = Configuration(v)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return None

    def get_or_set(self,name,default):
        ''' return the value, if not set then set it to default and return'''
        if name not in self.__dict__:
            self.__dict__[name] = default

        return self.__dict__[name]

    @staticmethod
    def load(path):

        if not os.path.isfile(path):
            logging.warning("cannot load config: "+path)
            return
        handle = open(path, 'r')

        try:
            d = json.load(handle)
            c = Configuration(d)
        except ValueError as e:
            logging.warning("invalid config format in file: "+path)
            raise e

        return c

    def save(self,path):
        '''save config to a file'''
        json.dump(self.__dict__, file(path,"w"), ensure_ascii=False, indent=2)

    def __str__(self):
        return str(self.__dict__);
