import unittest
from datetime import date
from pathlib import Path

from pyholos.components.animals import common, sheep
from pyholos.config import PathsHolosResources
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilTexture
from pyholos.utils import read_holos_resource_table


class TestGetAnimalCoefficientData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.animal_coefficients = read_holos_resource_table(
            path_file=PathsHolosResources.Table_22_Livestock_Coefficients_For_Sheep, index_col='Sheep Class')
        cls.animal_coefficients.rename(
            columns={
                "cf": "baseline_maintenance_coefficient",
                "a": "coefficient_a",
                "b": "coefficient_b",
                "Initial Weight": "initial_weight",
                "Final Weight": "final_weight",
                "Wool Production": "wool_production",
            },
            inplace=True)

    def setUp(self):
        self.sheep = sheep.SheepBase()

    def test_get_animal_coefficient_data_for_sheep_feedlot(self):
        self.sheep.group_name.value = sheep.GroupNames.sheep_feedlot.value
        self.assertEqual(
            self.animal_coefficients.loc['Ram'].to_dict(),
            self.sheep.get_animal_coefficient_data().__dict__)

    def test_get_animal_coefficient_data_for_rams(self):
        self.sheep.group_name.value = sheep.GroupNames.rams.value
        self.assertEqual(
            self.animal_coefficients.loc['Ram'].to_dict(),
            self.sheep.get_animal_coefficient_data().__dict__)

    def test_get_animal_coefficient_data_for_ewes(self):
        self.sheep.group_name.value = sheep.GroupNames.ewes.value
        self.assertEqual(
            self.animal_coefficients.loc['Ewe'].to_dict(),
            self.sheep.get_animal_coefficient_data().__dict__)

    def test_get_animal_coefficient_data_for_lambs(self):
        self.sheep.group_name.value = sheep.GroupNames.lambs.value
        self.assertEqual(
            self.animal_coefficients.loc['Weaned Lambs'].to_dict(),
            self.sheep.get_animal_coefficient_data().__dict__)


class TestGetFeedingActivityCoefficient(unittest.TestCase):

    def test_value_for_housed_ewes(self):
        self.assertEqual(
            0.0096,
            sheep.get_feeding_activity_coefficient(housing_type=common.HousingType.housed_ewes))

    def test_value_for_confined_animals(self):
        self.assertEqual(
            0.0067,
            sheep.get_feeding_activity_coefficient(housing_type=common.HousingType.confined))

    def test_value_for_pasture_and_flat_pasture(self):
        for housing_type in (common.HousingType.pasture,
                             common.HousingType.flat_pasture):
            self.assertEqual(
                0.0107,
                sheep.get_feeding_activity_coefficient(housing_type=housing_type))

    def test_value_for_hilly_pasture_or_open_range(self):
        self.assertEqual(
            0.024,
            sheep.get_feeding_activity_coefficient(housing_type=common.HousingType.hilly_pasture_or_open_range))

    def test_z_error(self):
        for housing_type in common.HousingType:
            if housing_type not in [
                common.HousingType.housed_ewes,
                common.HousingType.confined,
                common.HousingType.pasture,
                common.HousingType.flat_pasture,
                common.HousingType.hilly_pasture_or_open_range,
            ]:
                with self.assertRaises(ValueError):
                    sheep.get_feeding_activity_coefficient(housing_type=housing_type)


class TestSheepFeedlotNonRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_sheep_feedlot.csv',
            keep_default_na=False).loc[0].to_dict()

        cls.manure_state_type = common.ManureStateType.pasture
        cls.manure_emission_factors = common.get_manure_emission_factors(
            manure_state_type=cls.manure_state_type,
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            animal_type=common.AnimalType.sheep_feedlot,
            province=CanadianProvince.Alberta,
            year=2025,
            soil_texture=SoilTexture.Fine)

    def test_sheep_feedlot(self):
        sheep_feedlot = sheep.SheepFeedlot(
            management_period_name="Management period 1",
            group_pairing_number=0,
            management_period_start_date=date(2025, 1, 1),
            management_period_days=30,
            number_of_animals=100,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,

            diet=common.Diet(
                crude_protein_percentage=17.7,
                forage_percentage=0,
                total_digestible_nutrient_percentage=60,
                ash_percentage=8,
                starch_percentage=0,
                fat_percentage=0,
                neutral_detergent_fiber_percentage=0,
                metabolizable_energy=0),

            housing_type=common.HousingType.confined,  #########################
            manure_emission_factors=self.manure_emission_factors,
            manure_handling_system=self.manure_state_type,
            bedding_material_type=common.BeddingMaterialType.straw
        )
        res = sheep_feedlot.to_dict()
        for k, v in self.non_regression_data.items():
            self.assertAlmostEqual(
                v,
                res[k],
                places=3)


class TestRamsNonRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_sheep_rams.csv',
            keep_default_na=False).loc[0].to_dict()

        cls.manure_state_type = common.ManureStateType.pasture
        cls.manure_emission_factors = common.get_manure_emission_factors(
            manure_state_type=cls.manure_state_type,
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            animal_type=common.AnimalType.ram,
            province=CanadianProvince.Alberta,
            year=2025,
            soil_texture=SoilTexture.Fine)

    def test_rams(self):
        rams = sheep.Rams(
            management_period_name="Management period 1",
            group_pairing_number=0,
            management_period_start_date=date(2025, 1, 1),
            management_period_days=30,
            number_of_animals=100,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,

            diet=common.Diet(
                crude_protein_percentage=17.7,
                forage_percentage=0,
                total_digestible_nutrient_percentage=60,
                ash_percentage=8,
                starch_percentage=0,
                fat_percentage=0,
                neutral_detergent_fiber_percentage=0,
                metabolizable_energy=0),

            housing_type=common.HousingType.confined,  #########################
            manure_emission_factors=self.manure_emission_factors,
            manure_handling_system=self.manure_state_type,
            bedding_material_type=common.BeddingMaterialType.straw
        )
        res = rams.to_dict()
        for k, v in self.non_regression_data.items():
            self.assertAlmostEqual(
                v,
                res[k],
                places=3)


class TestEwesNonRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_sheep_lambs_and_ewes.csv',
            keep_default_na=False)

        cls.manure_state_type = common.ManureStateType.pasture
        cls.manure_emission_kwargs = dict(
            manure_state_type=cls.manure_state_type,
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            #            animal_type=common.AnimalType.ram,
            province=CanadianProvince.Alberta,
            #           year=2025,
            soil_texture=SoilTexture.Fine)

    def test_ewes(self):
        ewes = sheep.Ewes(
            management_period_name="Lactation",
            group_pairing_number=1,
            management_period_start_date=date(2024, 5, 28),
            management_period_days=218,
            number_of_animals=100,
            production_stage=common.ProductionStage.lactating,
            number_of_young_animals=0,

            diet=common.Diet(
                crude_protein_percentage=17.7,
                forage_percentage=0,
                total_digestible_nutrient_percentage=60,
                ash_percentage=8,
                starch_percentage=0,
                fat_percentage=0,
                neutral_detergent_fiber_percentage=0,
                metabolizable_energy=0),

            housing_type=common.HousingType.confined,  #########################
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.ewes,
                year=2024,
                **self.manure_emission_kwargs),
            manure_handling_system=self.manure_state_type,
            bedding_material_type=common.BeddingMaterialType.straw
        )
        res = ewes.to_dict()
        for k, v in self.non_regression_data.loc[0].to_dict().items():
            self.assertAlmostEqual(
                v,
                res[k],
                places=3)

    def test_lambs(self):
        ewes = sheep.Lambs(
            management_period_name="Management period 1",
            group_pairing_number=1,
            management_period_start_date=date(2025, 1, 1),
            management_period_days=30,
            number_of_animals=100,
            production_stage=common.ProductionStage.weaning,
            number_of_young_animals=0,

            diet=common.Diet(
                crude_protein_percentage=17.7,
                forage_percentage=0,
                total_digestible_nutrient_percentage=60,
                ash_percentage=8,
                starch_percentage=0,
                fat_percentage=0,
                neutral_detergent_fiber_percentage=0,
                metabolizable_energy=0),

            housing_type=common.HousingType.confined,  #########################
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.lambs,
                year=2025,
                **self.manure_emission_kwargs),
            manure_handling_system=self.manure_state_type,
            bedding_material_type=common.BeddingMaterialType.straw
        )
        res = ewes.to_dict()
        for k, v in self.non_regression_data.loc[1].to_dict().items():
            self.assertAlmostEqual(
                v,
                res[k],
                places=3)


if __name__ == '__main__':
    unittest.main()
