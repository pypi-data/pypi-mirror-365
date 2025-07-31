import unittest

from pyholos.components.land_management import utils
from pyholos.components.land_management.crop import CropType
from pyholos.common2 import CanadianProvince


class TestLoadData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = utils.LoadedData()

    def test_read_small_yield_area_data(self):
        self.assertNotIn(
            CropType.NotSelected,
            self.data.table_small_yield_area.columns)

    def test_values_for_perennial_crops_and_grass_silage(self):
        for crop in [
            CropType.Forage,
            CropType.TameGrass,
            CropType.TameLegume,
            CropType.TameMixed,
            CropType.PerennialForages,
            CropType.ForageForSeed,
            CropType.SeededGrassland,
            CropType.RangelandNative,
            CropType.GrassSilage
        ]:
            self.assertEqual(
                3000,
                self.data.get_yield(
                    year=1998,
                    polygon_id=1001002,
                    crop_type=crop,
                    province=CanadianProvince.BritishColumbia))

    def test_values_for_flax(self):
        self.assertEqual(
            self.data.get_yield(
                year=1991,
                polygon_id=541064,
                crop_type=CropType.Flax,
                province=CanadianProvince.Quebec),
            self.data.get_yield(
                year=1991,
                polygon_id=541064,
                crop_type=CropType.FlaxSeed,
                province=CanadianProvince.Quebec))

    def test_values_for_field_peas(self):
        self.assertEqual(
            self.data.get_yield(
                year=2006,
                polygon_id=780004,
                crop_type=CropType.FieldPeas,
                province=CanadianProvince.Saskatchewan),
            self.data.get_yield(
                year=2006,
                polygon_id=780004,
                crop_type=CropType.DryPeas,
                province=CanadianProvince.Saskatchewan))

    def test_values_other_crops(self):
        self.assertEqual(
            900,
            self.data.get_yield(
                year=1971,
                polygon_id=625001,
                crop_type=CropType.Canola,
                province=CanadianProvince.Alberta))

        self.assertEqual(
            1390,
            self.data.get_yield(
                year=2018,
                polygon_id=536001,
                crop_type=CropType.CanarySeed,
                province=CanadianProvince.PrinceEdwardIsland))

    def test_values_outside_index(self):
        self.assertIsNone(
            self.data.get_yield(
                year=2025,
                polygon_id=536001,
                crop_type=CropType.CanarySeed,
                province=CanadianProvince.PrinceEdwardIsland))


if __name__ == '__main__':
    unittest.main()
