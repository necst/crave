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

    def __init__(self, **kwargs):
        '''constructor'''
        self.__dict__ = kwargs

    def __init__(self, **options):
        '''constructor passing a dictionary'''
        self.__dict__ = options

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
    def loadConf(path):
        c = Configuration()

        if not os.path.isfile(path):
            logging.warning('cannot load config: ' + path)
            return
        
        handle = file(path)
        
        try:
            c.__dict__ = json.load(handle)
        except ValueError as e:
            logging.warning('invalid config format in file: ' + path)
            raise e

        return c

    def saveConf(self,path):
        '''save config to a file'''
        json.dump(self.__dict__, file(path,'w'), ensure_ascii=False, indent=2)

    def __str__(self):
        return `self.__dict__`;
