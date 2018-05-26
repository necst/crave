"""
    crafter module
"""
import logging
from hashlib import sha256
import os
import shutil
from pe import PE
from crave.utils.permutation import OrderedDefaultDict, permutate

l = logging.getLogger("crave.crafter")


class Crafter(object):
    """ this class craft the objects and store them in the database returning
    dicts (or db entries) """

    def __init__(self, project, sample):
        self.project = project
        self.sample = sample

    def mutation_sectionchar_rwx(self):
        return self.pe.modify_section_characteristics_rwx()

    def mutation_sectionname_random(self):
        return self.pe.modify_section_names(rand=True)

    def mutation_sectionname_randomdot(self):
        return self.pe.modify_section_names(rand=True, with_dot=True)

    def mutation_sectionname_infer(self):
        return self.pe.modify_section_names()

    def mutation_code_entryret(self):
        return self.pe.patch_code(va=self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)

    def update_checksum(self):
        return self.pe.update_checksum()

    def _craft_all(self):
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


class CraftFactory(object):

    def __init__(self, project):
        self.project = project
        self._prepare_mutations()

    def _prepare_mutations(self, permutations=False):
        """ makes all the possibly interesting mutations of the embedded
        goodware and malware sample(s)
        permutations: Bool that tells if we should use simple mutations
        or prepare all possible combinations ..."""

        mutations = [
                f for n, f in Crafter.__dict__.iteritems() if n.startswith('mutation_')]

        # last entry is to fix checksum or not
        if permutations is False:
            self.mutations = mutations + [Crafter.update_checksum]
            print self.mutations
            return

        # permutate all the things! \o/
        mutations_dict = OrderedDefaultDict(list)

        for f in mutations:
            category, mutation = f.__name__.lstrip('mutation_').split('_')
            mutations_dict[category].append((mutation,f))

        mutations_dict['checksum'] = [('checksum', Crafter.update_checksum),]

        # append None to all categories to exclude the mutation and easily get all the permutations
        for v in mutations_dict.itervalues():
            v.append(('None', None))

        self.mutations = permutate(list(mutations_dict.itervalues()))

    def __call__(self, sample):
        return Crafter(self.project, sample)
