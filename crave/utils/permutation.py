def permutate(arrays, i=0):
    if i == len(arrays):
        return [[]]

    res_next = permutate(arrays, i+1)
    res = []
    for n in arrays[i]:
        for arr in res_next:
            res.append([n] + arr)
    return res

