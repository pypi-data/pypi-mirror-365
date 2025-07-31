import unittest
from itertools import product
from pathlib import Path
from uuid import UUID

from pyholos.components.land_management import field_system
from pyholos.components.land_management.carbon.relative_biomass_information import (
    get_relative_biomass_information_data, parse_table_7)
from pyholos.components.land_management.common import (FertilizerBlends,
                                                       HarvestMethod,
                                                       IrrigationType,
                                                       TillageType)
from pyholos.components.land_management.crop import CropType
from pyholos.defaults import Defaults
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilFunctionalCategory
from pyholos.utils import read_holos_resource_table
from tests.helpers.utils import CropTypePerCategory


class TestLandManagementBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.silage_crops = [
            CropType.SilageCorn,
            CropType.GrassSilage,
            CropType.BarleySilage,
            CropType.OatSilage,
            CropType.TriticaleSilage,
            CropType.WheatSilage
        ]

    def setUp(self):
        self.land_management_base = field_system.LandManagementBase()

    def test_get_default_harvest_method_for_silage_crops(self):
        for crop_type in CropTypePerCategory.silage_crop:
            self.land_management_base.crop_type.value = crop_type
            self.assertEqual(
                HarvestMethod.Silage,
                self.land_management_base.get_default_harvest_method())

    def test_get_default_harvest_method_for_non_silage_crops(self):
        for crop_type in CropType:
            if crop_type not in CropTypePerCategory.silage_crop:
                self.land_management_base.crop_type.value = crop_type
                self.assertEqual(
                    HarvestMethod.CashCrop,
                    self.land_management_base.get_default_harvest_method())

    def test_set_irrigation_type(self):
        for irrigation_amount, expected_result in [
            (0, IrrigationType.RainFed),
            (100, IrrigationType.Irrigated),
        ]:
            self.land_management_base.amount_of_irrigation.value = irrigation_amount
            self.land_management_base.set_irrigation_type()
            self.assertEqual(
                expected_result,
                self.land_management_base.irrigation_type.value)

    def test_set_moisture_content_fresh_crop_harvest(self):
        for crop, harvest_method in product(CropTypePerCategory.silage_crop, [
            HarvestMethod.GreenManure,
            HarvestMethod.Silage,
            HarvestMethod.Swathing
        ]):
            self.land_management_base.crop_type.value = crop
            self.land_management_base.harvest_method.value = harvest_method
            self.land_management_base.set_moisture_content()
            self.assertEqual(
                65,
                self.land_management_base.moisture_content_of_crop_percentage.value)

    def test_set_moisture_content_default_non_fresh_crop_harvest_methods(self):
        self.land_management_base.moisture_content_of_crop.value = .15

        for crop in CropType:
            if crop not in CropTypePerCategory.silage_crop:
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_moisture_content()
                        self.assertEqual(
                            self.land_management_base.moisture_content_of_crop.value * 100.,
                            self.land_management_base.moisture_content_of_crop_percentage.value)

    def test_set_moisture_content_default_value(self):
        self.land_management_base.moisture_content_of_crop.value = 0
        for crop in CropType:
            if crop not in CropTypePerCategory.silage_crop:
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_moisture_content()
                        self.assertEqual(
                            12,
                            self.land_management_base.moisture_content_of_crop_percentage.value)

    def run_test_set_percentage_returns(
            self,
            expected_percentage_of_product_yield_returned_to_soil,
            expected_percentage_of_straw_returned_to_soil,
            expected_percentage_of_roots_returned_to_soil
    ):
        self.assertEqual(
            expected_percentage_of_product_yield_returned_to_soil,
            self.land_management_base.percentage_of_product_yield_returned_to_soil.value)
        self.assertEqual(
            expected_percentage_of_straw_returned_to_soil,
            self.land_management_base.percentage_of_straw_returned_to_soil.value)
        self.assertEqual(
            expected_percentage_of_roots_returned_to_soil,
            self.land_management_base.percentage_of_roots_returned_to_soil.value)

    def test_set_percentage_returns_for_perennial_crops(self):
        for crop_type in CropType:
            if crop_type.is_perennial():
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop_type
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_percentage_returns()
                        self.run_test_set_percentage_returns(
                            expected_percentage_of_product_yield_returned_to_soil=Defaults.PercentageOfProductReturnedToSoilForPerennials,
                            expected_percentage_of_straw_returned_to_soil=0,
                            expected_percentage_of_roots_returned_to_soil=Defaults.PercentageOfRootsReturnedToSoilForPerennials)

    def test_set_percentage_returns_for_annual_crops(self):
        for crop_type in CropType:
            if all([
                crop_type.is_annual(),
                not crop_type.is_root_crop(),
                not crop_type.is_cover_crop(),
                not crop_type.is_silage_crop(),
            ]):
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop_type
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_percentage_returns()
                        self.run_test_set_percentage_returns(
                            expected_percentage_of_product_yield_returned_to_soil=Defaults.PercentageOfProductReturnedToSoilForAnnuals,
                            expected_percentage_of_straw_returned_to_soil=Defaults.PercentageOfStrawReturnedToSoilForAnnuals,
                            expected_percentage_of_roots_returned_to_soil=Defaults.PercentageOfRootsReturnedToSoilForAnnuals)

    def test_set_percentage_returns_for_root_crops(self):
        for crop_type in CropType:
            if crop_type.is_root_crop():
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop_type
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_percentage_returns()
                        self.run_test_set_percentage_returns(
                            expected_percentage_of_product_yield_returned_to_soil=Defaults.PercentageOfProductReturnedToSoilForRootCrops,
                            expected_percentage_of_straw_returned_to_soil=Defaults.PercentageOfStrawReturnedToSoilForRootCrops,
                            expected_percentage_of_roots_returned_to_soil=0)

    def test_set_percentage_returns_for_cover_crops(self):
        for crop_type in CropType:
            if crop_type.is_cover_crop():
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop_type
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_percentage_returns()
                        self.run_test_set_percentage_returns(
                            expected_percentage_of_product_yield_returned_to_soil=100,
                            expected_percentage_of_straw_returned_to_soil=100,
                            expected_percentage_of_roots_returned_to_soil=100)

    def test_set_percentage_returns_for_silage_crops(self):
        for crop_type in CropType:
            if crop_type.is_silage_crop():
                for harvest_method in HarvestMethod:
                    if harvest_method not in [
                        HarvestMethod.GreenManure,
                        HarvestMethod.Silage,
                        HarvestMethod.Swathing
                    ]:
                        self.land_management_base.crop_type.value = crop_type
                        self.land_management_base.harvest_method.value = harvest_method
                        self.land_management_base.set_percentage_returns()
                        self.run_test_set_percentage_returns(
                            expected_percentage_of_product_yield_returned_to_soil=2,
                            expected_percentage_of_straw_returned_to_soil=0,
                            expected_percentage_of_roots_returned_to_soil=100)

    def test_set_percentage_returns_for_silage_harvest_method(self):
        for crop_type in CropType:
            self.land_management_base.crop_type.value = crop_type
            self.land_management_base.harvest_method.value = HarvestMethod.Silage
            self.land_management_base.set_percentage_returns()
            self.run_test_set_percentage_returns(
                expected_percentage_of_product_yield_returned_to_soil=2,
                expected_percentage_of_straw_returned_to_soil=0,
                expected_percentage_of_roots_returned_to_soil=100)

    def test_set_percentage_returns_for_swathing_harvest_method(self):
        for crop_type in CropType:
            if not crop_type.is_silage_crop():
                self.land_management_base.crop_type.value = crop_type
                self.land_management_base.harvest_method.value = HarvestMethod.Swathing
                self.land_management_base.set_percentage_returns()
                self.run_test_set_percentage_returns(
                    expected_percentage_of_product_yield_returned_to_soil=30,
                    expected_percentage_of_straw_returned_to_soil=0,
                    expected_percentage_of_roots_returned_to_soil=100)

    def test_set_percentage_returns_for_green_manure_harvest_method(self):
        for crop_type in CropType:
            if not crop_type.is_silage_crop():
                self.land_management_base.crop_type.value = crop_type
                self.land_management_base.harvest_method.value = HarvestMethod.GreenManure
                self.land_management_base.set_percentage_returns()
                self.run_test_set_percentage_returns(
                    expected_percentage_of_product_yield_returned_to_soil=100,
                    expected_percentage_of_straw_returned_to_soil=0,
                    expected_percentage_of_roots_returned_to_soil=100)


class TestCropViewItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field_data = read_holos_resource_table(
            Path(__file__).parents[2] / r'sources/holos/non_regression_crop_view_item/field_data.csv')
        cls.weather_data = read_holos_resource_table(
            Path(__file__).parents[2] / r'sources/holos/non_regression_crop_view_item/daily_weather.csv',
            usecols=['Year', 'Mean Daily Air Temperature', 'Mean Daily Precipitation', 'Mean Daily Pet'])
        cls.year = 2025
        cls.crop_type = CropType.Wheat
        cls.irrigation_type = IrrigationType.RainFed
        cls.irrigation_amount = 0
        cls.province = CanadianProvince.Quebec
        nearest_year = (cls.weather_data['Year'][cls.weather_data['Year'] <= cls.year]).max()
        precipitation = (cls.weather_data[cls.weather_data['Year'] == nearest_year]['Mean Daily Precipitation']).sum()
        cls.relative_biomass_data = get_relative_biomass_information_data(
            table_7=parse_table_7(),
            crop_type=cls.crop_type,
            irrigation_type=cls.irrigation_type,
            irrigation_amount=cls.irrigation_amount + precipitation,
            province=cls.province
        )
        cls.excepted_columns = [
            "Above Ground Carbon Input",
            "Below Ground Carbon Input",
            "Total Carbon Inputs",
            "Above Ground Residue Dry Matter",
            "Below Ground Residue Dry Matter",
            "Climate Parameter",
            "Tillage Factor",
            "Management Factor"
        ]

    def test_values(self):
        for _, annual_data in self.field_data.iterrows():
            crop_view_item = field_system.CropViewItem(
                name='field_1',
                field_area=1,
                current_year=self.year,
                crop_year=annual_data['Crop Year'],
                year_in_perennial_stand=0,
                crop_type=self.crop_type,
                tillage_type=TillageType.Reduced,
                perennial_stand_id=UUID('00000000-0000-0000-0000-000000000000'),
                perennial_stand_length=1,
                relative_biomass_information_data=self.relative_biomass_data,
                crop_yield=annual_data['Yield'],
                harvest_method=HarvestMethod.CashCrop,
                nitrogen_fertilizer_rate=0,
                under_sown_crops_used=False,
                field_system_component_guid=UUID('21d4222f-fc6c-439f-b606-a896abc1c38f'),
                province=self.province,
                clay_content=0.26,
                sand_content=0.28,
                organic_carbon_percentage=3.2,
                soil_top_layer_thickness=230,
                soil_functional_category=SoilFunctionalCategory.EasternCanada,
                fertilizer_blend=FertilizerBlends.Custom,
                evapotranspiration=self.weather_data['Mean Daily Pet'],
                precipitation=self.weather_data['Mean Daily Precipitation'],
                temperature=self.weather_data['Mean Daily Air Temperature'],
                amount_of_irrigation=self.irrigation_amount
            )

            res = crop_view_item.to_dict()
            for k, v in annual_data.to_dict().items():
                if k not in self.excepted_columns:
                    actual = res[k]
                    if any([isinstance(v, bool), isinstance(actual, bool)]):
                        v = str(v)
                        actual = str(v)
                        self.assertEqual(
                            v,
                            actual
                        )


if __name__ == '__main__':
    unittest.main()
