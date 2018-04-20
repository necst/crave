import re
from soundex import mapper

AGGRESSIVE_LABELIZER = True


def filter(label):
    label = label.lower()

    if 'malicious (high confidence)' in label:
        label = ''
    if 'static engine - malicious' in label:
        label = ''
    if 'generic.ml' in label:
        label = ''
    if 'malware (ai score=' in label:
        label = ''
    if 'malware.highconfidence' in label:
        label = ''
    if 'malicious_confidence_' in label:
        label = ''

    label = re.sub('(?i)heuristic', '', label, 1)
    label = re.sub('(?i)generic', '', label, 1)
    label = re.sub('(?i)malicious', '', label, 1)
    label = re.sub('(?i)unsafe', '', label, 1)
    label = re.sub('(?i)a variant of', '', label, 1)
    label = re.sub('(?i)behaveslike', '', label, 1)

    # TODO integrate AVClass aliases
    label = label.replace('allaple', 'virut')

    return label


def comparelabels(label1, label2):
    label1 = filter(label1)
    label2 = filter(label2)

    # If empty, they are not meaningful labels
    if not label1 or not label2:
        return False

    if label1 in label2:
        return True

    if label2 in label1:
        return True

    if AGGRESSIVE_LABELIZER:
        if 'virut' in label1 and 'virut' in label2:
            return True
        if 'virut' in label2:
            return True

    if mapper(label1) == mapper(label2):
        return True
