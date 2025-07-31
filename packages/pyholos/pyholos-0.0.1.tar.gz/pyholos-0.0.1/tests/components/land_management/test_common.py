import unittest

from pyholos.components.land_management import common
from pyholos.components.land_management.common import TillageType
from pyholos.components.land_management.crop import CropType
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilFunctionalCategory


class TestConvertTillageTypeName(unittest.TestCase):
    def test_values_for_not_till(self):
        for s in ("notill", "nt"):
            self.assertEqual(
                common.TillageType.NoTill,
                common.convert_tillage_type_name(name=s))

    def test_values_for_reduced_tillage(self):
        for s in ("reduced", "rt"):
            self.assertEqual(
                common.TillageType.Reduced,
                common.convert_tillage_type_name(name=s))

    def test_values_for_intensive_tillage(self):
        for s in ("intensive", "it", "conventional"):
            self.assertEqual(
                common.TillageType.Intensive,
                common.convert_tillage_type_name(name=s))

    def test_values_for_unrecognisable_text(self):
        for s in ("some", "random", "name"):
            self.assertEqual(
                None,
                common.convert_tillage_type_name(name=s))


class TestGetFuelEnergyEstimate(unittest.TestCase):
    def test_existing_values(self):
        self.assertEqual(
            1.42,
            common.get_fuel_energy_estimate(
                province=CanadianProvince.Saskatchewan,
                soil_category=SoilFunctionalCategory.BrownChernozem,
                tillage_type=TillageType.NoTill,
                crop_type=CropType.SunflowerSeed))

        self.assertEqual(
            0,
            common.get_fuel_energy_estimate(
                province=CanadianProvince.Ontario,
                soil_category=SoilFunctionalCategory.Black,
                tillage_type=TillageType.Reduced,
                crop_type=CropType.Fallow))

    def test_non_existing_values(self):
        self.assertEqual(
            0,
            common.get_fuel_energy_estimate(
                province=CanadianProvince.Quebec,
                soil_category=SoilFunctionalCategory.BrownChernozem,
                tillage_type=TillageType.Intensive,
                crop_type=CropType.TimothyHay))

class TestGetHerbicideEnergyEstimate(unittest.TestCase):
    def test_existing_values(self):
        self.assertEqual(
            0.46,
            common.get_herbicide_energy_estimate(
                province=CanadianProvince.BritishColumbia,
                soil_category=SoilFunctionalCategory.DarkBrown,
                tillage_type=TillageType.NoTill,
                crop_type=CropType.Oilseeds))

        self.assertEqual(
            0,
            common.get_herbicide_energy_estimate(
                province=CanadianProvince.Quebec,
                soil_category=SoilFunctionalCategory.Black,
                tillage_type=TillageType.Reduced,
                crop_type=CropType.Fallow))

    def test_non_existing_values(self):
        self.assertEqual(
            0,
            common.get_herbicide_energy_estimate(
                province=CanadianProvince.Quebec,
                soil_category=SoilFunctionalCategory.BrownChernozem,
                tillage_type=TillageType.Intensive,
                crop_type=CropType.TimothyHay))


if __name__ == '__main__':
    unittest.main()
