import re
import math
from types import NoneType, StringType, UnicodeType, FloatType


def mapper(word):
    if (word != "NO_THREAT_FOUND" and
            word is not None and
            word != "" and
            word != "THREAT_FOUND" and
            not re.match("(?:^.*not.a.virus.*$)", word, re.IGNORECASE) and
            word != "SCAN_TIMEOUT"):
        workKey = word

        splitted = re.split("[^a-zA-Z]", workKey)
        maxIndex = 0
        maxIndexElems = []
        for i, elem in enumerate(splitted):
            if len(elem) > len(splitted[maxIndex]):
                maxIndex = i
                maxIndexElems = []
            if elem == splitted[maxIndex]:
                maxIndexElems.append(i)

        buffer = ""
        for i in maxIndexElems:
            buffer = buffer + splitted[i]

        return soundex(buffer, 50)


def soundex(word, max_phonemes):
    #  discuss at: http://phpjs.org/functions/metaphone/
    # original by: Greg Frazier
    # improved by: Brett Zamir (http://brett-zamir.me)
    # improved by: Rafal Kukawski (http://kukawski.pl)
    #   example 1: metaphone('Gnu')
    #   returns 1: 'N'
    #   example 2: metaphone('bigger')
    #   returns 2: 'BKR'
    #   example 3: metaphone('accuracy')
    #   returns 3: 'AKKRS'
    #   example 4: metaphone('batch batcher')
    #   returns 4: 'BXBXR'

    w_type = type(word)
    # Handle unconsidered types
    if (w_type == NoneType or (w_type != StringType and
                               w_type != FloatType and w_type != UnicodeType)):
        # Weird!
        return None
    # Infinite and NaN values are treated as strings
    if (w_type == FloatType):
        if (math.isnan(word)):
            word = "NAN"
        elif (not math.isFinite(word)):
            word = "INF"
    # Empty string if not a string, encode if unicode
    if (w_type == UnicodeType):
        word = word.encode("ascii", "ignore")
    elif (w_type != StringType):
        word = ""

    if (max_phonemes < 0):
        return False

    max_phonemes = math.floor(+max_phonemes) or 0

    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    vowel = "AEIOU"
    soft = "EIY"

    # To uppercase and replace leading non alpha
    leadingNonAlpha = "^[^" + alpha + "]+"
    word = re.sub(leadingNonAlpha, "", word.upper())
    if (not word):
        return ""

    def _is(p, c):
        return c and p.find(c) != -1

    i = 0
    l = len(word)
    cc = word[0]  # Current char
    nc = word[1] if (l > 1) else ""  # Next char
    meta = ""

    if cc == 'A':
        meta += nc if (nc == 'E') else cc
        i += 1
    elif cc == 'G' or cc == 'K' or cc == 'P':
        if (nc == 'N'):
            meta += nc
            i += 2
    elif cc == 'W':
        if (nc == 'R'):
            meta += nc
            i += 2
        elif (nc == 'H' or _is(vowel, nc)):
            meta += 'W'
            i += 2
    elif cc == 'X':
        meta += 'S'
        i += 1
    elif cc == 'E' or cc == 'I' or cc == 'O' or cc == 'U':
        meta += cc
        i += 1

    traditional = True
    while (i < l and ((max_phonemes == 0) or (len(meta) < max_phonemes))):
        cc = word[i]
        nc = word[i + 1] if (i + 1 < l) else ""
        pc = word[i - 1] if (i > 0) else ""
        nnc = word[i + 2] if (i + 2 < l) else ""

        if (cc == pc and cc != 'C'):
            i += 1
            continue

        if cc == 'B':
            if (pc != 'M'):
                meta += cc
        elif cc == 'C':
            if (_is(soft, nc)):
                if (nc == 'I' and nnc == 'A'):
                    meta += 'X'
                elif (pc != 'S'):
                    meta += 'S'
            elif (nc == 'H'):
                condition = (nnc == 'R' or pc == 'S') and not traditional
                meta += 'K' if (condition) else 'X'
                i += 1
            else:
                meta += 'K'
        elif cc == 'D':
            if (nc == 'G' and _is(soft, nnc)):
                meta += 'J'
                i += 1
            else:
                meta += 'T'
        elif cc == 'G':
            if (nc == 'H'):
                p3c = word[i - 3] if (i > 2) else ""
                p4c = word[i - 4] if (i > 3) else ""
                if ((not (_is('BDH', p3c) or p4c == 'H'))):
                    meta += 'F'
                    i += 1
            elif (nc == 'N'):
                if (_is(alpha, nnc) and word[i + 1:i + 4] != 'NED'):
                    meta += 'K'
            elif (_is(soft, nc) and pc != 'G'):
                meta += 'J'
            else:
                meta += 'K'
        elif cc == 'H':
            if (_is(vowel, nc) and not _is('CGPST', pc)):
                meta += cc
        elif cc == 'K':
            if (pc != 'C'):
                meta += 'K'
        elif cc == 'P':
            meta += 'F' if(nc == 'H') else cc
        elif cc == 'Q':
            meta += 'K'
        elif cc == 'S':
            if (nc == 'I' and _is('AO', nnc)):
                meta += 'X'
            elif (nc == 'H'):
                meta += 'X'
                i += 1
            elif (not traditional and word[i + 1:i + 4] == 'CHW'):
                meta += 'X'
                i += 2
            else:
                meta += 'S'
        elif cc == 'T':
            if (nc == 'I' and _is('AO', nnc)):
                meta += 'X'
            elif (nc == 'H'):
                meta += '0'
                i += 1
            elif (word[i + 1:i + 3] != 'CH'):
                meta += 'T'
        elif cc == 'V':
            meta += 'F'
        elif cc == 'W' or cc == 'Y':
            if (_is(vowel, nc)):
                meta += cc
        elif cc == 'X':
            meta += 'KS'
        elif cc == 'Z':
            meta += 'S'
        elif (cc == 'F' or cc == 'J' or cc == 'L' or
              cc == 'M' or cc == 'N' or cc == 'R'):
            meta += cc
        # Increment counter before next iteration
        i += 1

    return meta