""" for now it implements a quick db backend with Vedis, potentially can be
expanded later to support other databases """
import os
import logging

l = logging.getLogger('crave.plugin')


class Plugin(object):

    def _init_plugin(self, project, opts):
        self.project = project
        self.opts = opts


# TODO: make all components a plugin


class PluginFactory(object):

    plugins = []

    def __new__(cls, plugin, *args, **kwargs):

        project = kwargs.get('project', None) or args[0]
        opts = kwargs.get('opts', None) or args[1]

        inst = plugin()

        inst._init_plugin(project, opts)

        if plugin not in cls.plugins:
            cls.plugins.append(inst)
        return inst
