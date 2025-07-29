import unittest
import numpy as np

import saftig as sg

from .test_filters import TestFilter


class TestLMSFilter(unittest.TestCase, TestFilter):
    """tests for the LeastMeanSquares filter implementation"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        test_configurations = [
            {"normalized": True},
            {"normalized": True, "coefficient_clipping": 2},
            {"normalized": False, "step_scale": 0.001},
        ]
        self.set_target(sg.LMSFilter, test_configurations)

    def test_update_state_setting(self):
        """check that the filter reaches a WF-Like performance on a simple static test case"""
        witness, target = sg.TestDataGenerator([0.1] * 2).generate(int(2e4))

        for filt in self.instantiate_filters(n_filter=32, n_channel=2):
            # check for no changes when False
            filt.apply(witness, target, update_state=False)
            self.assertTrue(bool(np.all(filt.filter_state == 0)))

            # check for no changes when True
            filt.apply(witness, target, update_state=True)
            self.assertTrue(bool(np.any(filt.filter_state != 0)))
