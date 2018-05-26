from collections import OrderedDict, defaultdict


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


def permutate(arrays, i=0):
    if i == len(arrays):
        return [[]]

    res_next = permutations(arrays, i+1)
    res = []
    for n in arrays[i]:
        for arr in res_next:
            res.append([n] + arr)
    return res

