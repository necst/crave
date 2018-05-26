import vedis
import tempfile

def mktempDB():
    import tempfile
    t = tempfile.NamedTemporaryFile()
    fname = t.name
    t.close()
    # small race here, who cares :/
    return Vedis(fname)
