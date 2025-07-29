import unittest

import saftig as sg

from .test_filters import TestFilter


class TestWienerFilter(unittest.TestCase, TestFilter):
    """Tests for the WF"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_target(sg.WienerFilter)

    def test_conditioning_warning(self):
        """check that a warning is thrown if the autocorrelation array does not have full rank"""
        n_filter = 128
        witness, target = sg.TestDataGenerator([0.1]).generate(int(1e4))

        # using two identical input datasets produces non-full-rank autocorrelation matrices
        witness = [witness[0], witness[0]]

        for filt in self.instantiate_filters(n_filter, n_channel=2):
            self.assertWarns(RuntimeWarning, filt.condition, witness, target)

    def test_no_target_for_apply(self):
        """check that the filter can be applied without a target signal"""
        n_filter = 128
        witness, target = sg.TestDataGenerator(0.1).generate(n_filter * 2)

        for filt in self.instantiate_filters(n_filter):
            filt.condition(witness, target)
            filt.apply(witness)
