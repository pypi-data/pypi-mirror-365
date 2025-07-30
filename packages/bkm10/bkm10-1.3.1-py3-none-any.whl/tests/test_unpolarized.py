"""
A testing suite for proving that the functions computing the coefficients for the unpolarized
target are returning real, finite, and accurate values.
"""

# (X): Native Library | unittest:
import unittest

# (X): External Library | NumPy:
import numpy as np

# (X): Self-Import | BKM10Inputs:
from bkm10_lib.inputs import BKM10Inputs

# (X): Self-Import | CFFInputs:
from bkm10_lib.cff_inputs import CFFInputs

# (X): Self-Import | DifferentialCrossSection
from bkm10_lib.core import DifferentialCrossSection

# (X): Self-Import | BKMFormalism
from bkm10_lib.formalism import BKMFormalism


# (X): Define a class that inherits unittest's TestCase:
class TestUnpolarizedCoefficients(unittest.TestCase):

    TEST_LAB_K = 5.75
    TEST_Q_SQUARED = 1.82
    TEST_X_BJORKEN = 0.343
    TEST_T = -0.172

    @classmethod
    def setUpClass(cls):

        # (X): Provide the BKM10 inputs to the dataclass:
        cls.test_kinematics = BKM10Inputs(
            lab_kinematics_k = cls.TEST_LAB_K,
            squared_Q_momentum_transfer = cls.TEST_Q_SQUARED,
            x_Bjorken = cls.TEST_X_BJORKEN,
            squared_hadronic_momentum_transfer_t = cls.TEST_T)

        # (X): Provide the CFF inputs to the dataclass:
        cls.test_cff_inputs = CFFInputs(
            compton_form_factor_h = complex(-0.897, 2.421),
            compton_form_factor_h_tilde = complex(2.444, 1.131),
            compton_form_factor_e = complex(-0.541, 0.903),
            compton_form_factor_e_tilde = complex(2.207, 5.383))
        
        # (X): Specify the target polarization *as a float*:
        cls.target_polarization = 0.

        # (X): Specify the beam polarization *as a float*:
        cls.lepton_polarization = 0.0

        # (X): We are using the WW relations in this computation:
        cls.ww_setting = True

        # (X): Using the setting we wrote earlier, we now need to construct
        cls.configuration = {
            "kinematics": cls.test_kinematics,
            "cff_inputs": cls.test_cff_inputs,
            "target_polarization": cls.target_polarization,
            "lepton_beam_polarization": cls.lepton_polarization,
            "using_ww": cls.ww_setting
        }
        
        cls.cross_section = DifferentialCrossSection(configuration = cls.configuration)

        cls.phi_values = np.linspace(0, 2 * np.pi, 10)
    
    def assert_is_finite(self, value):
        """
        ## Description:
        A general test in the suite that verifies that all the
        numbers in an array are *finite* (as opposed to Inf.-type or NaN)

        ## Notes:
        "NaN" means "not a number." Having NaN values in an array causes problems in
        functions that are designed to perform arithmetic.
        """
        self.assertTrue(
            expr = np.isfinite(value).all(),
            msg = "Value contains NaNs or infinities/Inf.")

    def assert_no_nans(self, value):
        """
        ## Description:
        A general test in the suite that determines if an array has NaNs.
        
        ## Notes:
        "NaN" means "not a number." Having NaN values in an array causes problems in
        functions that are designed to perform arithmetic.
        """
        self.assertFalse(
            expr = np.isnan(value).any(),
            msg = "> [ERROR]: Value contains NaNs")

    def assert_no_negatives(self, value):
        """
        ## Description:
        A general test in the suite that determines if an array has negative values
        in it.

        ## Notes:
        There *are* important negative quantities, and several coefficients are indeed
        negative. But cross-sections, for example, should be positive.
        """
        self.assertTrue(
            expr = (value >= 0).all(),
            msg = "> [ERROR]: Value contains negative values")

    def assert_is_real(self, value):
        """
        ## Description:
        A general test in the suite that determines that an array has
        all real values.
        """
        self.assertTrue(
            expr = np.isreal(value).all(),
            msg = "> [ERROR]: Value contains complex components")

    def assert_approximately_equal(self, value, expected, tolerance = 1e-8):
        """
        ## Description:
        A general test in the suite that determines if a *number* (`value`) is approximately
        equal to what is expected (`expected`). "Approximately equal" is quantified with the 
        parameter `tolerance`.
        """
        self.assertTrue(
            np.allclose(value, expected, rtol = tolerance, atol = tolerance),
            f"> [ERROR]: Expected {expected}, got {value}")
        
    def test_c0_coefficient(self):
        """
        ## Description:
        Test one of the highest-level coefficients in the BKM10 formalism:
        c_{0}^{I} in the mode expansion.
        """

        # (X): Calculate c_{0}^{I}:
        c0 = self.cross_section.compute_c0_coefficient(self.phi_values)[0]

        # (X): Verify that c_{0}^{I} is a *finite* number:
        self.assert_is_finite(c0)
        
        # (X); Verify that c_{0}^{I} is not a NaN:
        self.assert_no_nans(c0)

        # (X): Verify that c_{0}^{I} is real:
        self.assert_is_real(c0)

        # (X): IMPORTANT ONE: Verify that c_{0}^{I} is what we expect:
        _MATHEMATICA_RESULT = 4.196441097163937 + 29.512298473681934 - 0.4548568231402324
        self.assert_approximately_equal(c0, expected = _MATHEMATICA_RESULT)

    def test_c1_coefficient(self):
        """
        ## Description:
        Test one of the highest-level coefficients in the BKM10 formalism:
        c_{1}^{I} in the mode expansion.
        """

        # (X): Calculate c_{1}^{I}:
        c1 = self.cross_section.compute_c1_coefficient(self.phi_values)[0]

        # (X): Verify that c_{1}^{I} is a *finite* number:
        self.assert_is_finite(c1)
        
        # (X); Verify that c_{1}^{I} is not a NaN:
        self.assert_no_nans(c1)

        # (X): Verify that c_{1}^{I} is real:
        self.assert_is_real(c1)

        # (X): IMPORTANT ONE: Verify that c_{1}^{I} is what we expect:
        _MATHEMATICA_RESULT = -0.3460689391000681
        self.assert_approximately_equal(c1, expected = _MATHEMATICA_RESULT)

    def test_c2_coefficient(self):
        """
        ## Description:
        Test one of the highest-level coefficients in the BKM10 formalism:
        c_{2}^{I} in the mode expansion.
        """

        # (X): Calculate c_{2}^{I}:
        c2 = self.cross_section.compute_c2_coefficient(self.phi_values)[0]

        # (X): Verify that c_{2}^{I} is a *finite* number:
        self.assert_is_finite(c2)
        
        # (X); Verify that c_{2}^{I} is not a NaN:
        self.assert_no_nans(c2)

        # (X): Verify that c_{2}^{I} is real:
        self.assert_is_real(c2)

        # (X): IMPORTANT ONE: Verify that c_{2}^{I} is what we expect:
        _MATHEMATICA_RESULT = -0.03259012849881058
        self.assert_approximately_equal(c2, expected = _MATHEMATICA_RESULT)

    def test_c3_coefficient(self):
        """
        ## Description:
        Test one of the highest-level coefficients in the BKM10 formalism:
        c_{3}^{I} in the mode expansion.
        """

        # (X): Calculate c_{3}^{I}:
        c3 = self.cross_section.compute_c3_coefficient(self.phi_values)[0]

        # (X): Verify that c_{2}^{I} is a *finite* number:
        self.assert_is_finite(c3)
        
        # (X); Verify that c_{2}^{I} is not a NaN:
        self.assert_no_nans(c3)

        # (X): Verify that c_{2}^{I} is real:
        self.assert_is_real(c3)

        # (X): IMPORTANT ONE: Verify that c_{2}^{I} is what we expect:
        _MATHEMATICA_RESULT = 0.0003562823963322977
        self.assert_approximately_equal(c3, expected = _MATHEMATICA_RESULT)


if __name__ == "__main__":
    unittest.main()