import unittest
from datetime import date
from math import inf
from pathlib import Path
from random import uniform
from typing import Any
from uuid import UUID

from pandas import read_csv
from pydantic import ValidationError

from pyholos.components.animals.common import (BeddingMaterialType, Diet,
                                               DietAdditiveType, HousingType,
                                               ManureAnimalSourceTypes,
                                               ManureLocationSourceType,
                                               ManureStateType, Milk,
                                               ProductionStage)
from pyholos.components.land_management.common import (FertilizerBlends,
                                                       HarvestMethod,
                                                       IrrigationType,
                                                       ManureApplicationTypes,
                                                       TillageType)
from pyholos.components.land_management.crop import CropType
from pyholos.farm import farm_inputs
from pyholos.farm.farm_inputs import WeatherData


def get_weather_summary_example() -> farm_inputs.WeatherSummary:
    return farm_inputs.WeatherSummary(
        year=2025,
        mean_annual_precipitation=uniform(0, 1000),
        mean_annual_temperature=uniform(-5, 5),
        mean_annual_evapotranspiration=uniform(0, 1000),
        growing_season_precipitation=uniform(0, 1000),
        growing_season_evapotranspiration=uniform(0, 1000),
        monthly_precipitation=[uniform(0, 100) for _ in range(12)],
        monthly_potential_evapotranspiration=[uniform(0, 100) for _ in range(12)],
        monthly_temperature=[uniform(-30, 30) for _ in range(12)]
    )


class TestCalcYearInPerennialStand(unittest.TestCase):
    @staticmethod
    def calc_year_in_perennial_stand(**kwargs):
        return farm_inputs.FieldsInput.calc_year_in_perennial_stand(**kwargs)

    def test_all_annual(self):
        crops = [
            CropType.Wheat,
            CropType.Corn,
            CropType.Barley
        ]
        self.assertEqual(
            [0] * len(crops),
            self.calc_year_in_perennial_stand(crops=crops))

    def test_all_perennial(self):
        crops = [
            CropType.TameMixed,
            CropType.TameMixed,
            CropType.TameMixed
        ]
        self.assertEqual(
            [v + 1 for v in range(len(crops))],
            self.calc_year_in_perennial_stand(crops=crops))

    def test_mixed_annual_and_perennial(self):
        crops, expected = zip(*[
            (CropType.Wheat, 0),
            (CropType.Barley, 0),
            (CropType.TameMixed, 1),
            (CropType.TameMixed, 2),
            (CropType.TameMixed, 3),
            (CropType.Corn, 0)
        ])
        self.assertEqual(
            list(expected),
            self.calc_year_in_perennial_stand(crops=crops))


class TestCalcPerennialStandLengths(unittest.TestCase):
    @staticmethod
    def calc_perennial_stand_lengths(**kwargs):
        return farm_inputs.FieldsInput.calc_perennial_stand_lengths(**kwargs)

    def run_test(
            self,
            years_data: list[int] | tuple[int, ...],
            expected: list[int] | tuple[int, ...],
    ):
        self.assertEqual(
            list(expected),
            self.calc_perennial_stand_lengths(years_in_perennial_stand=years_data))

    def test_all_annual(self):
        years_data, expected = zip(*[
            (0, 1),
            (0, 1),
            (0, 1)
        ])
        self.run_test(
            expected=expected,
            years_data=years_data)

    def test_all_perennial(self):
        years_data, expected = zip(*[
            (1, 4),
            (2, 4),
            (3, 4),
            (4, 4),
        ])
        self.run_test(
            expected=expected,
            years_data=years_data)

    def test_mixed_annual_and_perennial(self):
        years_data, expected = zip(*[
            (0, 1),
            (1, 1),
            (0, 1),
            (1, 3),
            (2, 3),
            (3, 3),
            (0, 1),
        ])
        self.run_test(
            expected=expected,
            years_data=years_data)


class TestSetPerennialStandId(unittest.TestCase):
    @staticmethod
    def set_perennial_stand_id(**kwargs):
        return farm_inputs.FieldsInput.set_perennial_stand_id(**kwargs)

    @classmethod
    def setUpClass(cls):
        cls.id_for_annual = UUID("00000000-0000-0000-0000-000000000000")

    def test_all_annual(self):
        crops = [
            CropType.Wheat,
            CropType.Wheat,
            CropType.Wheat,
        ]
        self.assertEqual(
            [self.id_for_annual] * len(crops),
            self.set_perennial_stand_id(crops=crops))

    def test_all_perennial(self):
        crops = [
            CropType.TameMixed,
            CropType.TameMixed,
            CropType.TameMixed
        ]

        ids_perennial = self.set_perennial_stand_id(crops=crops)
        for id_result in ids_perennial:
            self.assertNotEqual(
                self.id_for_annual,
                id_result)
        self.assertEqual(
            list(set(ids_perennial))[0],
            ids_perennial[0])

    def test_mixed_annual_and_perennial(self):
        crops = [
            CropType.Wheat,
            CropType.Barley,
            CropType.TameMixed,
            CropType.TameMixed,
            CropType.TameMixed,
            CropType.Corn,
        ]

        ids_perennial = self.set_perennial_stand_id(crops=crops)
        for crop, id_result in zip(crops, ids_perennial):
            if crop.is_perennial():
                self.assertNotEqual(
                    self.id_for_annual,
                    id_result)
            else:
                self.assertEqual(
                    self.id_for_annual,
                    id_result)
        self.assertEqual(
            2,
            len(set(ids_perennial)))

    def test_mixed_perennial_crops(self):
        crops = [
            CropType.TameMixed,
            CropType.TameMixed,
            CropType.TameMixed,
            CropType.Forage,
            CropType.Forage,
            CropType.Forage,
        ]

        ids_perennial = self.set_perennial_stand_id(crops=crops)
        unique_ids = set(ids_perennial)
        for id_result in unique_ids:
            self.assertNotEqual(
                self.id_for_annual,
                id_result)

        self.assertEqual(
            2,
            len(unique_ids))


class TestInputWeatherData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.WeatherData = farm_inputs.WeatherData
        cls.year = 2025
        cls.precipitation = [uniform(0, 100) for _ in range(366)]
        cls.potential_evapotranspiration = [uniform(0, 100) for _ in range(366)]
        cls.temperature = [uniform(-30, 35) for _ in range(366)]

    def test_works_with_correct_types_and_values(self):
        self.WeatherData(
            year=self.year,
            precipitation=self.precipitation,
            potential_evapotranspiration=self.potential_evapotranspiration,
            temperature=self.temperature)

    def test_erroneous_year_input(self):
        kwargs = dict(
            precipitation=self.precipitation,
            potential_evapotranspiration=self.potential_evapotranspiration,
            temperature=self.temperature)

        for year, expected_message in [
            (-1, 'Input should be greater than 1970'),
            (None, 'Input should be a valid integer'),
            (inf, 'Input should be a finite number'),
            (-inf, 'Input should be a finite number'),
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
        ]:
            try:
                self.WeatherData(year=year, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_precipitation_input(self):
        kwargs = dict(
            year=self.year,
            potential_evapotranspiration=self.potential_evapotranspiration,
            temperature=self.temperature)

        for precipitation, expected_message in [
            (self.precipitation[10:], 'List should have at least 365 items after validation, not 356'),
            (self.precipitation[:-1] + [-1], 'Input should be greater than or equal to 0'),
            (self.precipitation[:-1] + [None], 'Input should be a valid number'),
            (self.precipitation[:-1] + [inf], 'Input should be a finite number'),
            (self.precipitation[:-1] + [-inf], 'Input should be a finite number'),
            (self.precipitation[:-1] + [''], 'Input should be a valid number')
        ]:
            try:
                self.WeatherData(precipitation=precipitation, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_potential_evapotranspiration_input(self):
        kwargs = dict(
            year=self.year,
            precipitation=self.precipitation,
            temperature=self.temperature)

        for potential_evapotranspiration, expected_message in [
            (self.potential_evapotranspiration[10:], 'List should have at least 365 items after validation, not 356'),
            (self.potential_evapotranspiration[:-1] + [-1], 'Input should be greater than or equal to 0'),
            (self.potential_evapotranspiration[:-1] + [None], 'Input should be a valid number'),
            (self.potential_evapotranspiration[:-1] + [inf], 'Input should be a finite number'),
            (self.potential_evapotranspiration[:-1] + [-inf], 'Input should be a finite number'),
            (self.potential_evapotranspiration[:-1] + [''], 'Input should be a valid number')
        ]:
            try:
                self.WeatherData(potential_evapotranspiration=potential_evapotranspiration, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_temperature_input(self):
        kwargs = dict(
            year=self.year,
            precipitation=self.precipitation,
            potential_evapotranspiration=self.potential_evapotranspiration)

        for temperature, expected_message in [
            (self.temperature[10:], 'List should have at least 365 items after validation, not 356'),
            (self.temperature[:-1] + [None], 'Input should be a valid number'),
            (self.temperature[:-1] + [inf], 'Input should be a finite number'),
            (self.temperature[:-1] + [''], 'Input should be a valid number')
        ]:
            try:
                self.WeatherData(temperature=temperature, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])


class TestInputWeatherSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.WeatherSummary = farm_inputs.WeatherSummary

    @staticmethod
    def get_kwargs() -> dict:
        return dict(
            year=2025,
            mean_annual_precipitation=uniform(0, 1000),
            mean_annual_temperature=uniform(-5, 5),
            mean_annual_evapotranspiration=uniform(0, 1000),
            growing_season_precipitation=uniform(0, 1000),
            growing_season_evapotranspiration=uniform(0, 1000),
            monthly_precipitation=[uniform(0, 100) for _ in range(12)],
            monthly_potential_evapotranspiration=[uniform(0, 100) for _ in range(12)],
            monthly_temperature=[uniform(-30, 30) for _ in range(12)],
        )

    def test_works_with_correct_types_and_values(self):
        self.WeatherSummary(**self.get_kwargs())

    def test_erroneous_year_input(self):
        kwargs = self.get_kwargs()
        kwargs.pop('year')

        for year, expected_message in [
            (-1, 'Input should be greater than 1970'),
            (None, 'Input should be a valid integer'),
            (inf, 'Input should be a finite number'),
            (-inf, 'Input should be a finite number'),
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
        ]:
            try:
                self.WeatherSummary(year=year, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_scalar_water_inputs(self):
        for name in [
            "mean_annual_precipitation",
            "mean_annual_evapotranspiration",
            "growing_season_precipitation",
            "growing_season_evapotranspiration"
        ]:
            kwargs = self.get_kwargs()
            kwargs.pop(name)

            for v, expected_message in [
                (-1, 'Input should be greater than or equal to 0'),
                (None, 'Input should be a valid number'),
                (inf, 'Input should be a finite number'),
                (-inf, 'Input should be a finite number'),
                ('', 'Input should be a valid number')
            ]:
                try:
                    self.WeatherSummary(**{name: v}, **kwargs)
                except ValidationError as e:
                    self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_vector_water_inputs(self):
        for name in [
            "monthly_precipitation",
            "monthly_potential_evapotranspiration"
        ]:
            kwargs = self.get_kwargs()
            values = kwargs[name]
            kwargs.pop(name)

            for v, expected_message in [
                (values[10:], 'List should have at least 12 items after validation, not 2'),
                (values[:-1] + [-1], 'Input should be greater than or equal to 0'),
                (values[:-1] + [None], 'Input should be a valid number'),
                (values[:-1] + [inf], 'Input should be a finite number'),
                (values[:-1] + [-inf], 'Input should be a finite number'),
                (values[:-1] + [''], 'Input should be a valid number')
            ]:
                try:
                    self.WeatherSummary(**{name: v}, **kwargs)
                except ValidationError as e:
                    self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_mean_annual_temperature_input(self):
        kwargs = self.get_kwargs()
        kwargs.pop("mean_annual_temperature")

        for temperature, expected_message in [
            (None, 'Input should be a valid number'),
            (inf, 'Input should be a finite number'),
            ('', 'Input should be a valid number')
        ]:
            try:
                self.WeatherSummary(mean_annual_temperature=temperature, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])

    def test_erroneous_monthly_temperature_input(self):
        kwargs = self.get_kwargs()
        values = kwargs["monthly_temperature"]
        kwargs.pop("monthly_temperature")

        for v, expected_message in [
            (values[10:], 'List should have at least 12 items after validation, not 2'),
            (values[:-1] + [None], 'Input should be a valid number'),
            (values[:-1] + [inf], 'Input should be a finite number'),
            (values[:-1] + [''], 'Input should be a valid number')
        ]:
            try:
                self.WeatherSummary(monthly_temperature=v, **kwargs)
            except ValidationError as e:
                self.assertEqual(expected_message, e.errors()[0]['msg'])


class TestInputBeefManagementPeriod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BeefManagementPeriod = farm_inputs.BeefManagementPeriod

        cls.weather_summary = get_weather_summary_example()

    def get_kwargs(self) -> dict:
        return dict(
            name='summer grazing',
            start_date=date(2024, 5, 1),
            days=183,
            group_pairing_number=0,
            number_of_animals=4,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            diet=Diet(
                crude_protein_percentage=14.8,
                forage_percentage=80,
                total_digestible_nutrient_percentage=61.58,
                ash_percentage=9.24,
                starch_percentage=16.2,
                fat_percentage=2.12,
                neutral_detergent_fiber_percentage=46.44,
                metabolizable_energy=2.2),
            housing_type=HousingType.pasture,
            manure_handling_system=ManureStateType.pasture,
            weather_summary=self.weather_summary,
            start_weight=100,
            end_weight=200,
            diet_additive_type=DietAdditiveType.NONE,
            bedding_material_type=BeddingMaterialType.straw,
        )

    def run_test(
            self,
            name: str,
            value: Any,
            expected_message: str,
            is_startswith: bool = False
    ):
        kwargs = self.get_kwargs()
        kwargs[name] = value

        try:
            self.BeefManagementPeriod(**kwargs)
        except ValidationError as e:
            if is_startswith:
                self.assertTrue(e.errors()[0]['msg'].startswith(expected_message))
            else:
                self.assertEqual(
                    expected_message,
                    e.errors()[0]['msg'])

    def test_works_with_correct_types_and_values(self):
        self.BeefManagementPeriod(**self.get_kwargs())

    def test_erroneous_name(self):
        self.run_test(
            name='name',
            value='',
            expected_message='String should have at least 1 character')

    def test_erroneous_start_date(self):
        for value, message in [
            ('19901231', 'Datetimes provided to dates should have zero time - e.g. be exact dates'),
            ('1492-01-02',
             "Assertion failed, Input 'start_date' should be greater than 1970-01-01, actual is 1492-01-02")
        ]:
            self.run_test(
                name='start_date',
                value=value,
                expected_message=message)

    def test_erroneous_days(self):
        for value, message in [
            ('1', 'Input should be a valid integer, unable to parse string as an integer'),
            (0, 'Input should be greater than 0'),
            (-1, 'Input should be greater than 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='days',
                value=value,
                expected_message=message)

    def test_erroneous_group_pairing_number(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='group_pairing_number',
                value=value,
                expected_message=message)

    def test_erroneous_number_of_animals(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='number_of_animals',
                value=value,
                expected_message=message)

    def test_erroneous_production_stage(self):
        for value in ["gestating", 0]:
            self.run_test(
                name='production_stage',
                value=value,
                expected_message="Input should be 'Gestating', 'Lactating', 'Open', 'Weaning', 'GrowingAndFinishing', 'BreedingStock' or 'Weaned'")

    def test_erroneous_number_of_young_animals(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='number_of_young_animals',
                value=value,
                expected_message=message)

    def test_erroneous_is_milk_fed_only(self):
        for value in ["", 0, 1]:
            self.run_test(
                name='is_milk_fed_only',
                value=value,
                expected_message="Input should be a valid boolean, unable to interpret input")

    def test_erroneous_diet(self):
        for value in ["", 0]:
            self.run_test(
                name='diet',
                value=value,
                expected_message="Input should be a valid dictionary or instance of Diet")

        try:
            Diet(**{k: -1 for k in Diet.__signature__.parameters.keys()})
        except ValidationError as e:
            for error_output in e.errors():
                self.assertEqual(
                    "Input should be greater than or equal to 0",
                    error_output['msg'])

    def test_erroneous_housing_type(self):
        for value in ["", 0]:
            self.run_test(
                name='housing_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'ConfinedNoBarn'",
                is_startswith=True)

    def test_erroneous_manure_handling_system(self):
        for value in ["", 0]:
            self.run_test(
                name='manure_handling_system',
                value=value,
                expected_message="Input should be 'NotSelected', 'AnaerobicDigester'",
                is_startswith=True)

    def test_erroneous_weather_summary(self):
        for value in ["", 0]:
            self.run_test(
                name='weather_summary',
                value=value,
                expected_message="Input should be a valid dictionary or instance of WeatherSummary")

    def test_erroneous_start_weight(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='start_weight',
                value=value,
                expected_message=message)

    def test_erroneous_end_weight(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='end_weight',
                value=value,
                expected_message=message)

    def test_erroneous_diet_additive_type(self):
        for value in ["", 0]:
            self.run_test(
                name='diet_additive_type',
                value=value,
                expected_message="Input should be 'TwoPercentFat', 'FourPercentFat'",
                is_startswith=True)

    def test_erroneous_bedding_material_type(self):
        for value in ["", 0]:
            self.run_test(
                name='bedding_material_type',
                value=value,
                expected_message="Input should be 'Straw', 'WoodChip'",
                is_startswith=True)


class TestInputDairyManagementPeriod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.DairyManagementPeriod = farm_inputs.DairyManagementPeriod

        cls.weather_summary = get_weather_summary_example()

    def get_kwargs(self) -> dict:
        return dict(
            name='summer grazing',
            start_date=date(2024, 5, 1),
            days=183,
            group_pairing_number=0,
            number_of_animals=4,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            milk_data=Milk(),
            diet=Diet(
                crude_protein_percentage=16.146,
                forage_percentage=77.8,
                total_digestible_nutrient_percentage=69.516,
                ash_percentage=6.323,
                starch_percentage=0,
                fat_percentage=0,
                neutral_detergent_fiber_percentage=35.289,
                metabolizable_energy=2.4459),
            housing_type=HousingType.pasture,
            manure_handling_system=ManureStateType.pasture,
            weather_summary=self.weather_summary,
            start_weight=100,
            end_weight=200,
            diet_additive_type=DietAdditiveType.NONE,
            bedding_material_type=BeddingMaterialType.straw,
        )

    def run_test(
            self,
            name: str,
            value: Any,
            expected_message: str,
            is_startswith: bool = False
    ):
        kwargs = self.get_kwargs()
        kwargs[name] = value

        try:
            self.DairyManagementPeriod(**kwargs)
        except ValidationError as e:
            if is_startswith:
                self.assertTrue(e.errors()[0]['msg'].startswith(expected_message))
            else:
                self.assertEqual(
                    expected_message,
                    e.errors()[0]['msg'])

    def test_works_with_correct_types_and_values(self):
        self.DairyManagementPeriod(**self.get_kwargs())

    def test_erroneous_name(self):
        self.run_test(
            name='name',
            value='',
            expected_message='String should have at least 1 character')

    def test_erroneous_start_date(self):
        for value, message in [
            ('19901231', 'Datetimes provided to dates should have zero time - e.g. be exact dates'),
            ('1492-01-02',
             "Assertion failed, Input 'start_date' should be greater than 1970-01-01, actual is 1492-01-02")
        ]:
            self.run_test(
                name='start_date',
                value=value,
                expected_message=message)

    def test_erroneous_days(self):
        for value, message in [
            ('1', 'Input should be a valid integer, unable to parse string as an integer'),
            (0, 'Input should be greater than 0'),
            (-1, 'Input should be greater than 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='days',
                value=value,
                expected_message=message)

    def test_erroneous_group_pairing_number(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='group_pairing_number',
                value=value,
                expected_message=message)

    def test_erroneous_number_of_animals(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='number_of_animals',
                value=value,
                expected_message=message)

    def test_erroneous_production_stage(self):
        for value in ["gestating", 0]:
            self.run_test(
                name='production_stage',
                value=value,
                expected_message="Input should be 'Gestating', 'Lactating', 'Open', 'Weaning', 'GrowingAndFinishing', 'BreedingStock' or 'Weaned'")

    def test_erroneous_number_of_young_animals(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='number_of_young_animals',
                value=value,
                expected_message=message)

    def test_erroneous_milk_data(self):
        for value in ["", 0, 1]:
            self.run_test(
                name='milk_data',
                value=value,
                expected_message="Input should be a valid dictionary or instance of Milk")

    def test_erroneous_diet(self):
        for value in ["", 0]:
            self.run_test(
                name='diet',
                value=value,
                expected_message="Input should be a valid dictionary or instance of Diet")

        try:
            Diet(**{k: -1 for k in Diet.__signature__.parameters.keys()})
        except ValidationError as e:
            for error_output in e.errors():
                self.assertEqual(
                    "Input should be greater than or equal to 0",
                    error_output['msg'])

    def test_erroneous_housing_type(self):
        for value in ["", 0]:
            self.run_test(
                name='housing_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'ConfinedNoBarn'",
                is_startswith=True)

    def test_erroneous_manure_handling_system(self):
        for value in ["", 0]:
            self.run_test(
                name='manure_handling_system',
                value=value,
                expected_message="Input should be 'NotSelected', 'AnaerobicDigester'",
                is_startswith=True)

    def test_erroneous_weather_summary(self):
        for value in ["", 0]:
            self.run_test(
                name='weather_summary',
                value=value,
                expected_message="Input should be a valid dictionary or instance of WeatherSummary")

    def test_erroneous_start_weight(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='start_weight',
                value=value,
                expected_message=message)

    def test_erroneous_end_weight(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='end_weight',
                value=value,
                expected_message=message)

    def test_erroneous_diet_additive_type(self):
        for value in ["", 0]:
            self.run_test(
                name='diet_additive_type',
                value=value,
                expected_message="Input should be 'TwoPercentFat', 'FourPercentFat'",
                is_startswith=True)

    def test_erroneous_bedding_material_type(self):
        for value in ["", 0]:
            self.run_test(
                name='bedding_material_type',
                value=value,
                expected_message="Input should be 'Straw', 'WoodChip'",
                is_startswith=True)


class TestInputSheepManagementPeriod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.SheepManagementPeriod = farm_inputs.SheepManagementPeriod

        cls.weather_summary = get_weather_summary_example()

    def get_kwargs(self) -> dict:
        return dict(
            name='summer grazing',
            start_date=date(2024, 5, 1),
            days=183,
            group_pairing_number=0,
            number_of_animals=4,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            diet=Diet(
                crude_protein_percentage=17.7,
                forage_percentage=0,
                total_digestible_nutrient_percentage=60,
                ash_percentage=8,
                starch_percentage=0,
                fat_percentage=0,
                neutral_detergent_fiber_percentage=0,
                metabolizable_energy=0),
            housing_type=HousingType.pasture,
            manure_handling_system=ManureStateType.pasture,
            weather_summary=self.weather_summary,
            start_weight=100,
            end_weight=200,
            diet_additive_type=DietAdditiveType.NONE,
            bedding_material_type=BeddingMaterialType.straw,
        )

    def run_test(
            self,
            name: str,
            value: Any,
            expected_message: str,
            is_startswith: bool = False
    ):
        kwargs = self.get_kwargs()
        kwargs[name] = value

        try:
            self.SheepManagementPeriod(**kwargs)
        except ValidationError as e:
            if is_startswith:
                self.assertTrue(e.errors()[0]['msg'].startswith(expected_message))
            else:
                self.assertEqual(
                    expected_message,
                    e.errors()[0]['msg'])

    def test_works_with_correct_types_and_values(self):
        self.SheepManagementPeriod(**self.get_kwargs())

    def test_erroneous_name(self):
        self.run_test(
            name='name',
            value='',
            expected_message='String should have at least 1 character')

    def test_erroneous_start_date(self):
        for value, message in [
            ('19901231', 'Datetimes provided to dates should have zero time - e.g. be exact dates'),
            ('1492-01-02',
             "Assertion failed, Input 'start_date' should be greater than 1970-01-01, actual is 1492-01-02")
        ]:
            self.run_test(
                name='start_date',
                value=value,
                expected_message=message)

    def test_erroneous_days(self):
        for value, message in [
            ('1', 'Input should be a valid integer, unable to parse string as an integer'),
            (0, 'Input should be greater than 0'),
            (-1, 'Input should be greater than 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='days',
                value=value,
                expected_message=message)

    def test_erroneous_group_pairing_number(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='group_pairing_number',
                value=value,
                expected_message=message)

    def test_erroneous_number_of_animals(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='number_of_animals',
                value=value,
                expected_message=message)

    def test_erroneous_production_stage(self):
        for value in ["gestating", 0]:
            self.run_test(
                name='production_stage',
                value=value,
                expected_message="Input should be 'Gestating', 'Lactating', 'Open', 'Weaning', 'GrowingAndFinishing', 'BreedingStock' or 'Weaned'")

    def test_erroneous_number_of_young_animals(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='number_of_young_animals',
                value=value,
                expected_message=message)

    def test_erroneous_milk_data(self):
        for value in ["", 0, 1]:
            self.run_test(
                name='milk_data',
                value=value,
                expected_message="Input should be a valid dictionary or instance of Milk")

    def test_erroneous_diet(self):
        for value in ["", 0]:
            self.run_test(
                name='diet',
                value=value,
                expected_message="Input should be a valid dictionary or instance of Diet")

        try:
            Diet(**{k: -1 for k in Diet.__signature__.parameters.keys()})
        except ValidationError as e:
            for error_output in e.errors():
                self.assertEqual(
                    "Input should be greater than or equal to 0",
                    error_output['msg'])

    def test_erroneous_housing_type(self):
        for value in ["", 0]:
            self.run_test(
                name='housing_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'ConfinedNoBarn'",
                is_startswith=True)

    def test_erroneous_manure_handling_system(self):
        for value in ["", 0]:
            self.run_test(
                name='manure_handling_system',
                value=value,
                expected_message="Input should be 'NotSelected', 'AnaerobicDigester'",
                is_startswith=True)

    def test_erroneous_weather_summary(self):
        for value in ["", 0]:
            self.run_test(
                name='weather_summary',
                value=value,
                expected_message="Input should be a valid dictionary or instance of WeatherSummary")

    def test_erroneous_start_weight(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='start_weight',
                value=value,
                expected_message=message)

    def test_erroneous_end_weight(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
            (inf, 'Input should be a finite number'),
        ]:
            self.run_test(
                name='end_weight',
                value=value,
                expected_message=message)

    def test_erroneous_diet_additive_type(self):
        for value in ["", 0]:
            self.run_test(
                name='diet_additive_type',
                value=value,
                expected_message="Input should be 'TwoPercentFat', 'FourPercentFat'",
                is_startswith=True)

    def test_erroneous_bedding_material_type(self):
        for value in ["", 0]:
            self.run_test(
                name='bedding_material_type',
                value=value,
                expected_message="Input should be 'Straw', 'WoodChip'",
                is_startswith=True)


class TestInputFieldAnnualData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.FieldAnnualData = farm_inputs.FieldAnnualData
        cls.year = 2024

        df = read_csv(Path(__file__).parents[1] / 'sources/holos/daily_weather_data_example.csv',
                      sep=',', decimal='.', comment='#',
                      usecols=['Year', 'Mean Daily Air Temperature', 'Mean Daily Precipitation', 'Mean Daily Pet'])
        df = df[df['Year'] == cls.year]
        cls.weather_data = WeatherData(
            year=cls.year,
            precipitation=df['Mean Daily Precipitation'].to_list(),
            potential_evapotranspiration=df['Mean Daily Pet'].to_list(),
            temperature=df['Mean Daily Air Temperature'].to_list())

    def get_kwargs(self) -> dict:
        return dict(
            name='field_1',
            field_area=1,
            weather_data=self.weather_data,
            crop_type=CropType.Wheat,
            crop_yield=2700,
            crop_year=self.year,
            under_sown_crops_used=False,
            tillage_type=TillageType.Reduced,
            harvest_method=HarvestMethod.CashCrop,
            nitrogen_fertilizer_rate=100,
            fertilizer_blend=FertilizerBlends.Custom,
            irrigation_type=IrrigationType.Irrigated,
            amount_of_irrigation=0,
            number_of_pesticide_passes=0,
            amount_of_manure_applied=0,
            manure_application_type=ManureApplicationTypes.NotSelected,
            manure_animal_source_type=ManureAnimalSourceTypes.NotSelected,
            manure_state_type=ManureStateType.not_selected,
            manure_location_source_type=ManureLocationSourceType.NotSelected
        )

    def run_test(
            self,
            name: str,
            value: Any,
            expected_message: str,
            is_startswith: bool = False
    ):
        kwargs = self.get_kwargs()
        kwargs[name] = value

        try:
            self.FieldAnnualData(**kwargs)
        except ValidationError as e:
            if is_startswith:
                self.assertTrue(e.errors()[0]['msg'].startswith(expected_message))
            else:
                self.assertEqual(
                    expected_message,
                    e.errors()[0]['msg'])

    def test_works_with_correct_types_and_values(self):
        self.FieldAnnualData(**self.get_kwargs())

    def test_erroneous_name(self):
        self.run_test(
            name='name',
            value='',
            expected_message='String should have at least 1 character')

    def test_erroneous_field_area(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than 0'),
        ]:
            self.run_test(
                name='field_area',
                value=value,
                expected_message=message)

    def test_erroneous_weather_data(self):
        for k in ('precipitation', 'potential_evapotranspiration', 'temperature'):
            weather_data = WeatherData(**self.weather_data.model_dump())
            setattr(weather_data, k, 1)
            self.run_test(
                name='weather_data',
                value=weather_data,
                expected_message="Input should be a valid list")

    def test_erroneous_crop_type(self):
        for value in ('Canola', 0):
            self.run_test(
                name='crop_type',
                value=value,
                expected_message="Input should be 'AlfalfaMedicagoSativaL', 'AlfalfaSeed'",
                is_startswith=True)

    def test_erroneous_crop_yield(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
        ]:
            self.run_test(
                name='crop_yield',
                value=value,
                expected_message=message)

    def test_erroneous_crop_year(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than 0'),
        ]:
            self.run_test(
                name='crop_year',
                value=value,
                expected_message=message)

    def test_erroneous_under_sown_crops_used(self):
        for value, message in [
            ('', 'Input should be a valid boolean, unable to interpret input'),
            (-1, 'Input should be a valid boolean, unable to interpret input'),
        ]:
            self.run_test(
                name='under_sown_crops_used',
                value=value,
                expected_message=message)

    def test_erroneous_tillage_type(self):
        for value in ('Canola', 0):
            self.run_test(
                name='tillage_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'Reduced'",
                is_startswith=True)

    def test_erroneous_harvest_method(self):
        for value in ('GreenManure', 0):
            self.run_test(
                name='harvest_method',
                value=value,
                expected_message="Input should be 'Silage', 'Swathing'",
                is_startswith=True)

    def test_erroneous_nitrogen_fertilizer_rate(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
        ]:
            self.run_test(
                name='nitrogen_fertilizer_rate',
                value=value,
                expected_message=message)

    def test_erroneous_fertilizer_blend(self):
        for value in ('Urea', 0):
            self.run_test(
                name='fertilizer_blend',
                value=value,
                expected_message="Input should be 'Urea', 'Ammonia'",
                is_startswith=True)

    def test_erroneous_irrigation_type(self):
        for value in ('Rain Fed', 0):
            self.run_test(
                name='irrigation_type',
                value=value,
                expected_message="Input should be 'Irrigated' or 'RainFed'",
                is_startswith=True)

    def test_erroneous_amount_of_irrigation(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
        ]:
            self.run_test(
                name='amount_of_irrigation',
                value=value,
                expected_message=message)

    def test_erroneous_number_of_pesticide_passes(self):
        for value, message in [
            ('', 'Input should be a valid integer, unable to parse string as an integer'),
            (-1, 'Input should be greater than or equal to 0'),
        ]:
            self.run_test(
                name='number_of_pesticide_passes',
                value=value,
                expected_message=message)

    def test_erroneous_amount_of_manure_applied(self):
        for value, message in [
            ('', 'Input should be a valid number, unable to parse string as a number'),
            (-1, 'Input should be greater than or equal to 0'),
        ]:
            self.run_test(
                name='amount_of_irrigation',
                value=value,
                expected_message=message)

    def test_erroneous_manure_application_type(self):
        for value in ('Not Selected', 0):
            self.run_test(
                name='manure_application_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'OptionA'",
                is_startswith=True)

    def test_erroneous_manure_animal_source_type(self):
        for value in ('Not Selected', 0):
            self.run_test(
                name='manure_animal_source_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'BeefManure'",
                is_startswith=True)

    def test_erroneous_manure_state_type(self):
        for value in ('not selected', 0):
            self.run_test(
                name='manure_state_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'AnaerobicDigester'",
                is_startswith=True)

    def test_erroneous_manure_location_source_type(self):
        for value in ('On Farm Anaerobic Digestor', 0):
            self.run_test(
                name='manure_location_source_type',
                value=value,
                expected_message="Input should be 'NotSelected', 'Livestock'",
                is_startswith=True)


if __name__ == '__main__':
    unittest.main()
