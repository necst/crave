"""
    crafter module
"""
import logging
import string
import sys
from hashlib import sha256
import itertools
import tempfile
from collections import OrderedDict, defaultdict
import os
import shutil
from vedis import Vedis
from pe import PE

l = logging.getLogger("crave.crafter")

class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


def permutations(arrays, i=0):
    if i == len(arrays):
        return [[]]

    res_next = permutations(arrays, i+1)
    res = []
    for n in arrays[i]:
        for arr in res_next:
            res.append([n] + arr)
    return res


class Crafter(object):
    """ this class craft the objects and store them in the database returning
    dicts (or db entries) """

    def __init__(self, sample, db = None):
        self.input_file = sample
        self.pe = PE(sample)

        self.filename = os.path.basename(infile)

        name = os.path.join('results',  self.filename)
        if os.path.exists(name):
            shutil.rmtree(name)
        os.mkdir(name)
        self.outdir = name

        self.load_sections()

    def mutation_sectionchar_rwx(self):
        return self.modify_section_characteristics_rwx()

    def mutation_sectionname_random(self):
        return self.modify_section_names(rand=True)

    def mutation_sectionname_randomdot(self):
        return self.modify_section_names(rand=True, with_dot=True)

    def mutation_sectionname_infer(self):
        return self.modify_section_names()

    def mutation_code_entryret(self):
        return self.patch_code(va=self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)

    def craft_all(self):
        """ makes all the possibly interesting mutations of the embedded
        goodware and malware sample(s) """

        mutations = [
                f for n, f in Crave.__dict__.iteritems() if n.startswith('mutation_')]
        mutations_dict = OrderedDefaultDict(list)

        for f in mutations:
            category, mutation = f.__name__.lstrip('mutation_').split('_')
            mutations_dict[category].append((mutation,f))

        # last entry is to fix checksum or not
        mutations_dict['checksum'] = [('checksum', Crave.update_checksum),]

        # append None to all categories to exclude the mutation and easily get all the permutations
        for v in mutations_dict.itervalues():
            v.append(('None', None))

        self.mutations = permutations(list(mutations_dict.itervalues()))

        # TODO: fix how we process the given sample!
        # dictionary containing sample hash, filename, and characteristics
        # generate samples:
        results = {}
        for mutate_funcs in self.mutations:

            name = os.path.join(self.outdir, self.filename)
            mut_names = '_'.join([n for n,f in mutate_funcs if f is not None])
            if mut_names:
                name += '_' + mut_names

            self.pe.write(name)
            self.workpe = pefile.PE(name)

            for n, f in mutate_funcs:
                if f is not None:
                    f(self)

            #verify if checksum is called it should be last
            if 'checksum' in name and name.index('checksum') != len(name)-len('checksum'):
                raise Exception("Checksum was not the last mutation called")

            self.workpe.write(name)
            with open(name) as fin:
                sha = sha256(fin.read()).hexdigest()
            results[sha] = [n for n,f in mutate_funcs] # data about mutation!

        return results

def CraftFactory(object):

    def crafter(self, *args, **kwargs):
        return Crafter(self._project, *args, **kwargs)
