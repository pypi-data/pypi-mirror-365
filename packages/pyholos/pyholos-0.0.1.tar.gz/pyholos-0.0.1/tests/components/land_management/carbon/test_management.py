import unittest
from random import random, uniform

from pyholos.components.land_management.carbon import management


class TestCalculateManagementFactor(unittest.TestCase):
    def test_values(self):
        self.assertEqual(
            0,
            management.calculate_management_factor(
                climate_parameter=0,
                tillage_factor=random()))

        self.assertEqual(
            0,
            management.calculate_management_factor(
                climate_parameter=random(),
                tillage_factor=0))

        for _ in range(5):
            climate_param = uniform(0, 3)
            tillage_param = random()
            self.assertAlmostEqual(
                climate_param * tillage_param,
                management.calculate_management_factor(
                    climate_parameter=climate_param,
                    tillage_factor=tillage_param),
                places=3)


if __name__ == '__main__':
    unittest.main()
