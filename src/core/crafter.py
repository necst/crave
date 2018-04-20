import pefile
import angr
from copy import copy
import random
import string
import sys
from hashlib import sha256
import itertools
import tempfile
from collections import OrderedDict, defaultdict
import os
import keystone as ks
import shutil

IMAGE_SIZEOF_SHORT_NAME = 8

# might want to fuzz and use heuristics for filtering samples + testing
# we get a file like sample_other_characteristics_packer

# packer can be: upx, mew, aspack, none
# sample is: malware, dropper, benign, 
# the characteristics in the middle are the other added tests


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

    def __init__(self, infile):
        self.input_file = infile
        self.pe = pefile.PE(infile)
        self.filename = os.path.basename(infile)
        # temporary file to mutate the original sample
        self.workpe = None
        self.angr_pj = angr.Project(infile)
        self.angr_sections = []
        self.sections_arch = []
        self.mutations = [f for n, f in Crave.__dict__.iteritems() if n.startswith('mutation_')]
        self.mutations_dict = OrderedDefaultDict(list)

        name = os.path.join('results',  self.filename)
        if os.path.exists(name):
            shutil.rmtree(name)
        os.mkdir(name)
        self.outdir = name

        for f in self.mutations:
            category, mutation = f.__name__.lstrip('mutation_').split('_')
            self.mutations_dict[category].append((mutation,f))

        # last entry is to fix checksum or not
        self.mutations_dict['checksum'] = [('checksum', Crave.update_checksum),]

        # append None to all categories to exclude the mutation and easily get all the permutations
        for v in self.mutations_dict.itervalues():
            v.append(('None', None))

        self.mutations = permutations(list(self.mutations_dict.itervalues()))

        self.load_sections()



    def modify_section_characteristics_rwx(self):
        for s in self.workpe.sections:
            s.IMAGE_SCN_MEM_READ = True
            s.IMAGE_SCN_MEM_WRITE = True
            s.IMAGE_SCN_MEM_EXECUTE = True

    # modify sections names
    def modify_section_names(self, rand=False, with_dot=False, seed=0):
        """ with_dot, let's see if some AV modify label by having a section abiding by
            https://stackoverflow.com/questions/44022429/is-there-really-a-limit-to-sections-name-in-pe-binaries
            (see COFF specs) """

        def random_name(with_dot, seed=0):
            # eventualmente modifica alfabeto anche

            random.seed(seed)
            name = ''.join(random.choice(string.ascii_letters)
                     for i in range(0, IMAGE_SIZEOF_SHORT_NAME-1)) + '\x00'
            if with_dot:
                name = '.' + name[1:]
            return name

        sections = self.workpe.sections

        for s, i in zip(sections, range(0, len(sections))):
            # random
            if rand:
                s.Name = random_name(with_dot)
                continue

            arch = self.sections_arch[i]
            if arch == 'X86' or s.IMAGE_SCN_MEM_EXECUTE:
                s.Name = '.text'.ljust(len(s.Name), '\x00')
            elif s.IMAGE_SCN_MEM_READ:
                s.Name = '.rdata'.ljust(len(s.Name), '\x00')
            else:    #  elif s.IMAGE_SCN_MEM_WRITE:
                s.Name = '.data'.ljust(len(s.Name), '\x00')

    def mutation_sectionchar_rwx(self):
        return self.modify_section_characteristics_rwx()

    def mutation_sectionname_random(self):
        return self.modify_section_names(rand=True)

    def mutation_sectionname_randomdot(self):
        return self.modify_section_names(rand=True, with_dot=True)

    def mutation_sectionname_infer(self):
        return self.modify_section_names()


    def patch_code(self, instructions='ret;',va=0):
        """ put instruction(s), at the end of the basic block specified"""
        # get capstone instruction at the end of the basic_block
        try:
            k = ks.Ks(ks.KS_ARCH_X86, ks.KS_MODE_32)
            encoding, count = k.asm(instructions)
        except ks.KsError as e:
            print "Error! %s", e
            raise

        if not self.workpe.set_bytes_at_rva(va, ''.join(map(chr, encoding))):
            raise Exception('Cannot patch bytes at %x!', va)

    def mutation_code_entryret(self):
        return self.patch_code(va=self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)


    def update_checksum(self):
        self.workpe.OPTIONAL_HEADER.CheckSum = self.workpe.generate_checksum()

    # load section as shellcode so we can
    # use capstone+keystone to add stuff to the loader
    # we will need a custom made sample
    # for the emulation test
    def load_sections(self):
        for s, i in zip(self.pe.sections, range(0, len(self.pe.sections))):
            dd = s.get_data(s.VirtualAddress, s.SizeOfRawData)
            try:
                a = angr.project.load_shellcode(dd, 'x86')
            except:
                a = None
            self.angr_sections.append(a)
            if a is not None:
                bb = a.analyses.BoyScout()
                self.sections_arch.append(bb.arch)
            else:
                self.sections_arch.append('DATA')

    def mutate(self):
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


if __name__ == '__main__':
    import json
    crave = Crafter(sys.argv[1])
    results = crave.mutate()

    with open(os.path.join(crave.outdir, 'results.json'), 'w') as resf:
        json.dump(results, resf)
