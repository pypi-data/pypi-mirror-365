import unittest
from datetime import date
from pathlib import Path

from pyholos.components.animals import common, dairy
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilTexture
from pyholos.utils import read_holos_resource_table


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.non_regression_data = read_holos_resource_table(
            path_file=Path(__file__).parents[2] / 'sources/holos/non_regression_dairy.csv',
            keep_default_na=False)
        cls.non_regression_data.set_index("Group Name", inplace=True)

        cls.province = CanadianProvince.Manitoba
        cls.manure_emission_kwargs = dict(
            mean_annual_precipitation=541.5,
            mean_annual_temperature=3.6,
            mean_annual_evapotranspiration=625.7,
            growing_season_precipitation=383,
            growing_season_evapotranspiration=568,
            province=cls.province,
            soil_texture=SoilTexture.Fine)

        cls.housing_type = common.HousingType.free_stall_barn_solid_litter
        cls.bedding_material_type = common.BeddingMaterialType.sand

        cls.diet = common.Diet(
            crude_protein_percentage=16.146,
            forage_percentage=77.8,
            total_digestible_nutrient_percentage=69.516,
            ash_percentage=6.323,
            starch_percentage=0,
            fat_percentage=0,
            neutral_detergent_fiber_percentage=35.289,
            metabolizable_energy=2.4459)

    def run_test(
            self,
            group_name: str,
            res: dict
    ):
        for k, v in self.non_regression_data.loc[group_name].to_dict().items():
            self.assertAlmostEqual(
                v,
                res[k],
                places=3)

    def test_dairy_heifers(self):
        manure_state_type = common.ManureStateType.daily_spread

        dairy_heifers = dairy.DairyHeifers(
            management_period_name='Management period 1',
            group_pairing_number=0,
            management_period_start_date=date(2025, 1, 1),
            management_period_days=30,
            number_of_animals=20,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            milk_data=common.Milk(),
            diet=self.diet,
            housing_type=self.housing_type,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.dairy_heifers,
                year=2025,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=self.bedding_material_type
        )

        self.run_test(
            group_name=dairy_heifers.group_name.value,
            res=dairy_heifers.to_dict()
        )

    def test_dairy_lactating_cow(self):
        manure_state_type = common.ManureStateType.pasture

        dairy_lactating_cow = dairy.DairyLactatingCow(
            management_period_name='Early lactation',
            group_pairing_number=1,
            management_period_start_date=date(2024, 1, 1),
            management_period_days=150,
            number_of_animals=20,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            milk_data=common.Milk(
                production_amount=common.get_average_milk_production_for_dairy_cows_value(
                    year=2025,
                    province=self.province),
                fat_content=3.71,
            ),
            diet=self.diet,
            housing_type=self.housing_type,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.dairy_lactating_cow,
                year=2025,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=self.bedding_material_type
        )

        self.run_test(
            group_name=dairy_lactating_cow.group_name.value,
            res=dairy_lactating_cow.to_dict()
        )

    def test_dairy_calves(self):
        manure_state_type = common.ManureStateType.solid_storage

        dairy_calves = dairy.DairyCalves(
            management_period_name='Milk-fed dairy calves. A period of no enteric methane emissions',
            group_pairing_number=1,
            management_period_start_date=date(2024, 1, 1),
            management_period_days=30,
            number_of_animals=20,
            production_stage=common.ProductionStage.weaning,
            number_of_young_animals=0,
            milk_data=common.Milk(),
            diet=self.diet,
            housing_type=self.housing_type,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.dairy_calves,
                year=2025,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=self.bedding_material_type
        )

        self.run_test(
            group_name=dairy_calves.group_name.value,
            res=dairy_calves.to_dict()
        )

    def test_dairy_dry_cow(self):
        manure_state_type = common.ManureStateType.solid_storage

        dairy_dry_cow = dairy.DairyDryCow(
            management_period_name='Dry period',
            group_pairing_number=0,
            management_period_start_date=date(2024, 11, 5),
            management_period_days=60,
            number_of_animals=20,
            production_stage=common.ProductionStage.gestating,
            number_of_young_animals=0,
            milk_data=common.Milk(),
            diet=self.diet,
            housing_type=self.housing_type,
            manure_handling_system=manure_state_type,
            manure_emission_factors=common.get_manure_emission_factors(
                animal_type=common.AnimalType.dairy_dry_cow,
                year=2025,
                manure_state_type=manure_state_type,
                **self.manure_emission_kwargs),
            bedding_material_type=self.bedding_material_type
        )

        self.run_test(
            group_name=dairy_dry_cow.group_name.value,
            res=dairy_dry_cow.to_dict()
        )


if __name__ == '__main__':
    unittest.main()
