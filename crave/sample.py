class Sample(object):

    def __init__(project, filename):
        self.project = project
        self.filename = filename

        # XXX: should we move in the PE?
        # we might want to store stuff in a proper DB
        # with all the modifications in a parsable format
        # 'deserialize' PE?

    def put(self):
        self.project.db.put_sample()

    def get(self):
        self.project.db.get_sample()

    def craft(self, mutation=None):
        """ apply all possible mutations to the sample and store
        in the database, we'll be ready to go and scan these """
        if mutation is not None:
            pass

        for m in self.project.Crafter.mutations:
            self.c
