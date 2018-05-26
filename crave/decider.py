class Decider:

    def test_emu(self, goodware, malware):
        # we need to query
        # goodware -> dropper
        # malware -> dropper
        # if it recognize the malicious dropper
        # as original sample variant, we have a
        # av that is able to emulate the shit
        goodware = self.project.get_sample(goodware)
        malware = self.project.get_sample(malware)

        gw_dropper = goodware.get_dropper()
        mw_dropper = malware.get_dropper()

        # look at scan results and infer
        return {}

    def test_heuristics(self, sample):
        _sample = self.project.get_sample(sample)
        heur = _sample.get_heuristics()

        for s in heur:
            pass
        # infer if it gets more detections or less

    def test_static_unpack(self, malware):
        sample = malware.get_sample() # (?) o gli passiamo un sample direttamente
        packed = sample.get_packed()
        broke_oep = packed.get_heur('retoep')

        # and here infer if it does static unpacking
        return {}
