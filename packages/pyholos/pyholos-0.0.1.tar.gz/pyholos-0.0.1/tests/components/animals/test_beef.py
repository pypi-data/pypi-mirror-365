import unittest
from datetime import date
from pathlib import Path

from pyholos.components.animals import beef, common
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilTexture
from pyholos.utils import read_holos_resource_table


class TestBeef(unittest.TestCase):
    def setUp(self):
        self.beef = beef.BeefBase()

    def test_update_name(self):
        old_name = self.beef.name.value
        new_name = 'test_name'
        self.beef.update_name(name=new_name)
        self.assertEqual(
            ' '.join((old_name, new_name)),
            self.beef.name.value)

    def test_update_component_type(self):
        old_name = self.beef.component_type.value
        new_name = 'test_name'
        self.beef.update_component_type(component_type=new_name)
        self.assertEqual(
            '.'.join((old_name, new_name)),
            self.beef.component_type.value)


class TestBeefCowCalfNonRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_beef_cow_calf.csv',
            keep_default_na=False)
        cls.non_regression_data.set_index("Group Name", inplace=True)

        cls.animal_type = common.AnimalType.beef_bulls
        cls.manure_emission_kwargs = dict(
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            province=CanadianProvince.Alberta,
            soil_texture=SoilTexture.Fine)

    def run_test(
            self,
            group_name: str,
            res: dict
    ):
        for k, v in self.non_regression_data.loc[group_name].to_dict().items():
            actual = res[k]

            if all([isinstance(v, (int, float)), isinstance(actual, (int, float))]):
                self.assertAlmostEqual(
                    v,
                    res[k],
                    places=3)
            else:
                self.assertEqual(
                    str(v),
                    str(res[k]))

    def test_bulls(self):
        manure_state_type = common.ManureStateType.deep_bedding

        bulls = beef.Bulls(
            management_period_name='Winter feeding',
            group_pairing_number=0,
            management_period_start_date=date(2024, 1, 1),
            management_period_days=119,
            number_of_animals=4,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.44,
                forage_percentage=97,
                total_digestible_nutrient_percentage=54.572,
                ash_percentage=10.327,
                starch_percentage=7.081,
                fat_percentage=1.716,
                neutral_detergent_fiber_percentage=53.478,
                metabolizable_energy=1.965),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=self.animal_type,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Bulls",
            res=bulls.to_dict()
        )

    def test_replacement_heifers(self):
        manure_state_type = common.ManureStateType.pasture

        replacement_heifers = beef.ReplacementHeifers(
            management_period_name='Management period 1',
            group_pairing_number=0,
            management_period_start_date=date(2024, 1, 1),
            management_period_days=365,
            number_of_animals=20,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=6.8,
                forage_percentage=100,
                total_digestible_nutrient_percentage=48.4,
                ash_percentage=10.3,
                starch_percentage=4.2,
                fat_percentage=1.8,
                neutral_detergent_fiber_percentage=66.6,
                metabolizable_energy=1.8),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=self.animal_type,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Replacement heifers",
            res=replacement_heifers.to_dict()
        )

    def test_cows(self):
        manure_state_type = common.ManureStateType.deep_bedding

        cows = beef.Cows(
            management_period_name='Winter feeding - lactating',
            group_pairing_number=1,
            management_period_start_date=date(2024, 3, 1),
            management_period_days=61,
            number_of_animals=120,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.44,
                forage_percentage=97,
                total_digestible_nutrient_percentage=54.572,
                ash_percentage=10.327,
                starch_percentage=7.081,
                fat_percentage=1.716,
                neutral_detergent_fiber_percentage=53.478,
                metabolizable_energy=1.965),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=self.animal_type,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Cows",
            res=cows.to_dict()
        )

    def test_calves(self):
        manure_state_type = common.ManureStateType.deep_bedding

        calves = beef.Calves(
            management_period_name='Management period 1',
            group_pairing_number=1,
            management_period_start_date=date(2024, 3, 1),
            management_period_days=60,
            number_of_animals=102,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=True,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.44,
                forage_percentage=97,
                total_digestible_nutrient_percentage=54.572,
                ash_percentage=10.327,
                starch_percentage=7.081,
                fat_percentage=1.716,
                neutral_detergent_fiber_percentage=53.478,
                metabolizable_energy=1.965),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=self.animal_type,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Calves",
            res=calves.to_dict()
        )


class TestBeefFinisherNonRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_beef_finisher.csv',
            keep_default_na=False)
        cls.non_regression_data.set_index("Group Name", inplace=True)

        cls.manure_emission_kwargs = dict(
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            province=CanadianProvince.Manitoba,
            soil_texture=SoilTexture.Fine)

    def run_test(
            self,
            group_name: str,
            res: dict
    ):
        for k, v in self.non_regression_data.loc[group_name].to_dict().items():
            actual = res[k]

            if all([isinstance(v, (int, float)), isinstance(actual, (int, float))]):
                self.assertAlmostEqual(
                    v,
                    res[k],
                    places=3)
            else:
                self.assertEqual(
                    str(v),
                    str(res[k]))


    def test_heifers(self):
        manure_state_type = common.ManureStateType.deep_bedding

        finishing_heifers = beef.FinishingHeifers(
            management_period_name='Management period 1',
            group_pairing_number=0,
            management_period_start_date=date(2024, 1, 19),
            management_period_days=170,
            number_of_animals=100,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.72,
                forage_percentage=10,
                total_digestible_nutrient_percentage=81.75,
                ash_percentage=3.38,
                starch_percentage=51.95,
                fat_percentage=2.33,
                neutral_detergent_fiber_percentage=21.95,
                metabolizable_energy=2.92),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.beef_finishing_heifer,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Heifers",
            res=finishing_heifers.to_dict()
        )

    def test_steers(self):
        manure_state_type = common.ManureStateType.deep_bedding

        finishing_steers = beef.FinishingSteers(
            management_period_name='Management period 1',
            group_pairing_number=0,
            management_period_start_date=date(2024, 1, 19),
            management_period_days=170,
            number_of_animals=100,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.72,
                forage_percentage=10,
                total_digestible_nutrient_percentage=81.75,
                ash_percentage=3.38,
                starch_percentage=51.95,
                fat_percentage=2.33,
                neutral_detergent_fiber_percentage=21.95,
                metabolizable_energy=2.92),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.beef_finishing_steer,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Steers",
            res=finishing_steers.to_dict()
        )


class TestBeefBackgrounderNonRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_beef_stockers_and_backgrounders.csv',
            keep_default_na=False)

        cls.non_regression_data.set_index("Group Name", inplace=True)

        cls.manure_emission_kwargs = dict(
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            province=CanadianProvince.Manitoba,
            soil_texture=SoilTexture.Fine)

    def run_test(
            self,
            group_name: str,
            res: dict
    ):
        for k, v in self.non_regression_data.loc[group_name].to_dict().items():
            actual = res[k]

            if all([isinstance(v, (int, float)), isinstance(actual, (int, float))]):
                self.assertAlmostEqual(
                    v,
                    res[k],
                    places=3)
            else:
                self.assertEqual(
                    str(v),
                    str(res[k]))

    def test_heifers(self):
        manure_state_type = common.ManureStateType.deep_bedding

        backgrounder_heifer = beef.BackgrounderHeifer(
            management_period_name='Management period 1',
            group_pairing_number=0,
            management_period_start_date=date(2023, 10, 1),
            management_period_days=110,
            number_of_animals=100,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.28,
                forage_percentage=65,
                total_digestible_nutrient_percentage=68.825,
                ash_percentage=6.57,
                starch_percentage=25.825,
                fat_percentage=3.045,
                neutral_detergent_fiber_percentage=42.025,
                metabolizable_energy=2.48),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.beef_backgrounder_heifer,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Heifers",
            res=backgrounder_heifer.to_dict()
        )

    def test_steers(self):
        manure_state_type = common.ManureStateType.deep_bedding

        backgrounder_heifer = beef.BackgrounderSteer(
            management_period_name='Management period 1',
            group_pairing_number=0,
            management_period_start_date=date(2023, 10, 1),
            management_period_days=110,
            number_of_animals=100,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            milk_data=common.Milk(),
            diet=common.Diet(
                crude_protein_percentage=12.28,
                forage_percentage=65,
                total_digestible_nutrient_percentage=68.825,
                ash_percentage=6.57,
                starch_percentage=25.825,
                fat_percentage=3.045,
                neutral_detergent_fiber_percentage=42.025,
                metabolizable_energy=2.48),
            housing_type=common.HousingType.confined_no_barn,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.beef_backgrounder_steer,
                year=2024,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=common.BeddingMaterialType.straw
        )
        self.run_test(
            group_name="Steers",
            res=backgrounder_heifer.to_dict()
        )


if __name__ == '__main__':
    unittest.main()
