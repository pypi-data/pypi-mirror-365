import unittest
from itertools import product
from random import choice

from pyholos.components.land_management.carbon import tillage
from pyholos.components.land_management.common import TillageType
from pyholos.components.land_management.crop import CropType
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilFunctionalCategory

_PRAIRIE_PROVINCES = [
    CanadianProvince.Alberta,
    CanadianProvince.Saskatchewan,
    CanadianProvince.Manitoba]


class TestCalculateCropTillageFactor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.considered_soil_functional_categories = []

    def test_existing_values(self):
        for soil_functional_category, tillage_type, expected_result in [
            (SoilFunctionalCategory.Brown, TillageType.Intensive, 1.0),
            (SoilFunctionalCategory.Brown, TillageType.Reduced, 0.9),
            (SoilFunctionalCategory.Brown, TillageType.NoTill, 0.8),
            (SoilFunctionalCategory.DarkBrown, TillageType.Intensive, 1.0),
            (SoilFunctionalCategory.DarkBrown, TillageType.Reduced, 0.85),
            (SoilFunctionalCategory.DarkBrown, TillageType.NoTill, 0.7),
            (SoilFunctionalCategory.Black, TillageType.Intensive, 1.0),
            (SoilFunctionalCategory.Black, TillageType.Reduced, 0.8),
            (SoilFunctionalCategory.Black, TillageType.NoTill, 0.6),
        ]:
            self.assertEqual(
                expected_result,
                tillage.calculate_crop_tillage_factor(
                    soil_functional_category=soil_functional_category,
                    tillage_type=tillage_type))
            self.considered_soil_functional_categories.append(soil_functional_category)

    def test_values_from_outside_table(self):
        for soil_functional_category in SoilFunctionalCategory:
            if soil_functional_category not in [
                SoilFunctionalCategory.Brown,
                SoilFunctionalCategory.DarkBrown,
                SoilFunctionalCategory.Black
            ]:
                self.assertEqual(
                    1,
                    tillage.calculate_crop_tillage_factor(
                        soil_functional_category=soil_functional_category,
                        tillage_type=choice(list(TillageType))
                    )
                )


class TestCalculateTillageFactorForPerennials(unittest.TestCase):
    def test_value_for_prairie_provinces(self):
        for province in _PRAIRIE_PROVINCES:
            for soil_functional_category, expected_value in [
                (SoilFunctionalCategory.Brown, 0.8),
                (SoilFunctionalCategory.DarkBrown, 0.7),
                (SoilFunctionalCategory.Black, 0.6),
            ]:
                self.assertEqual(
                    expected_value,
                    tillage.calculate_tillage_factor_for_perennials(
                        soil_functional_category=soil_functional_category,
                        province=province))

    def test_value_for_non_prairie_provinces(self):
        for province in CanadianProvince:
            if province not in _PRAIRIE_PROVINCES:
                self.assertEqual(
                    0.9,
                    tillage.calculate_tillage_factor_for_perennials(
                        soil_functional_category=choice(list(SoilFunctionalCategory)),
                        province=province))


class TestCalculateTillageFactor(unittest.TestCase):
    def test_values_for_root_crops(self):
        for crop in CropType:
            if crop.is_root_crop():
                self.assertEqual(
                    1.13,
                    tillage.calculate_tillage_factor(
                        province=choice(list(CanadianProvince)),
                        soil_functional_category=choice(list(SoilFunctionalCategory)),
                        tillage_type=choice(list(TillageType)),
                        crop_type=crop))

    def test_values_for_annual_crops_in_non_prairie_provinces(self):
        for crop, province in product(CropType, CanadianProvince):
            if all([
                crop.is_annual(),
                not crop.is_root_crop(),
                province not in _PRAIRIE_PROVINCES
            ]):
                self.assertEqual(
                    1,
                    tillage.calculate_tillage_factor(
                        province=province,
                        soil_functional_category=choice(list(SoilFunctionalCategory)),
                        tillage_type=choice(list(TillageType)),
                        crop_type=crop))

    def test_values_for_annual_crops_in_prairie_provinces(self):
        for crop, province, soil_functional_category, tillage_type in product(
                CropType, _PRAIRIE_PROVINCES, SoilFunctionalCategory, TillageType):
            if all([
                crop.is_annual(),
                not crop.is_root_crop(),
            ]):
                self.assertEqual(
                    tillage.calculate_crop_tillage_factor(
                        soil_functional_category=soil_functional_category.get_simplified_soil_category(),
                        tillage_type=tillage_type),
                    tillage.calculate_tillage_factor(
                        province=province,
                        soil_functional_category=soil_functional_category,
                        tillage_type=tillage_type,
                        crop_type=crop))

    def test_values_for_perennial_crops(self):
        for crop, province, soil_functional_category in product(CropType, CanadianProvince, SoilFunctionalCategory):
            if crop.is_perennial():
                self.assertEqual(
                    tillage.calculate_tillage_factor_for_perennials(
                        soil_functional_category=soil_functional_category.get_simplified_soil_category(),
                        province=province),
                    tillage.calculate_tillage_factor(
                        province=province,
                        soil_functional_category=soil_functional_category,
                        tillage_type=choice(list(TillageType)),
                        crop_type=crop))


if __name__ == '__main__':
    unittest.main()
