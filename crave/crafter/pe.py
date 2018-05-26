import logging
import pefile
import angr
import keystone as ks
import random

l = logging.getLogger('crave.crafter.pe')

IMAGE_SIZEOF_SHORT_NAME = 8


class PE(object):
    """ this class builds on pefile, enables a set of pre-defined mutations
    to be applied on a sample PE file
    """

    def __init__(sample):
        self.sample = sample
        self.pe = pefile.PE(sample)
        # temporary file to mutate the original sample
        self.workpe = None
        self.angr_pj = angr.Project(infile)
        self.angr_sections = []
        self.sections_arch = []

    def load_sections(self):
        """ load section as shellcode so we can
        use capstone+keystone to add stuff to the loader
        we will need a custom made sample
        for the emulation test
        """

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

    def update_checksum(self):
        self.workpe.OPTIONAL_HEADER.CheckSum = self.workpe.generate_checksum()

