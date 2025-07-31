from datetime import date

from pyholos.components.animals.common import (Diet, HousingType,
                                               ManureStateType,
                                               ProductionStage)
from pyholos.farm import farm_inputs
from pyholos.farm.farm_inputs import WeatherSummary

global _WEATHER_SUMMARY


def _set_beef_bulls_data() -> list[farm_inputs.BeefManagementPeriod]:
    return [
        farm_inputs.BeefManagementPeriod(
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
            weather_summary=_WEATHER_SUMMARY),
        farm_inputs.BeefManagementPeriod(
            name='extended fall grazing',
            start_date=date(2024, 11, 1),
            days=60,
            group_pairing_number=0,
            number_of_animals=4,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            diet=Diet(
                crude_protein_percentage=12.44,
                forage_percentage=97,
                total_digestible_nutrient_percentage=54.572,
                ash_percentage=10.327,
                starch_percentage=7.081,
                fat_percentage=1.716,
                neutral_detergent_fiber_percentage=53.478,
                metabolizable_energy=1.965),
            housing_type=HousingType.pasture,
            manure_handling_system=ManureStateType.pasture,
            weather_summary=_WEATHER_SUMMARY),
        farm_inputs.BeefManagementPeriod(
            name='winter feeding',
            start_date=date(2024, 1, 1),
            days=121,
            group_pairing_number=0,
            number_of_animals=4,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            diet=Diet(
                crude_protein_percentage=15.35,
                forage_percentage=100,
                total_digestible_nutrient_percentage=57.7,
                ash_percentage=10.15,
                starch_percentage=4.35,
                fat_percentage=1.95,
                neutral_detergent_fiber_percentage=49.3,
                metabolizable_energy=2.1),
            housing_type=HousingType.confined_no_barn,
            manure_handling_system=ManureStateType.deep_bedding,
            weather_summary=_WEATHER_SUMMARY)
    ]


def _set_beef_cows_data() -> list[farm_inputs.BeefManagementPeriod]:
    return [
        farm_inputs.BeefManagementPeriod(
            name='summer grazing',
            start_date=date(2024, 5, 1),
            days=183,
            group_pairing_number=1,
            number_of_animals=150,
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
            weather_summary=_WEATHER_SUMMARY),
        farm_inputs.BeefManagementPeriod(
            name='extended fall grazing',
            start_date=date(2024, 11, 1),
            days=60,
            group_pairing_number=1,
            number_of_animals=150,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            diet=Diet(
                crude_protein_percentage=12.44,
                forage_percentage=97,
                total_digestible_nutrient_percentage=54.572,
                ash_percentage=10.327,
                starch_percentage=7.081,
                fat_percentage=1.716,
                neutral_detergent_fiber_percentage=53.478,
                metabolizable_energy=1.965),
            housing_type=HousingType.pasture,
            manure_handling_system=ManureStateType.pasture,
            weather_summary=_WEATHER_SUMMARY),
        farm_inputs.BeefManagementPeriod(
            name='winter feeding',
            start_date=date(2024, 1, 1),
            days=121,
            group_pairing_number=1,
            number_of_animals=150,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=False,
            diet=Diet(
                crude_protein_percentage=15.35,
                forage_percentage=100,
                total_digestible_nutrient_percentage=57.7,
                ash_percentage=10.15,
                starch_percentage=4.35,
                fat_percentage=1.95,
                neutral_detergent_fiber_percentage=49.3,
                metabolizable_energy=2.1),
            housing_type=HousingType.confined_no_barn,
            manure_handling_system=ManureStateType.deep_bedding,
            weather_summary=_WEATHER_SUMMARY)
    ]


def _set_beef_calf_data() -> list[farm_inputs.BeefManagementPeriod]:
    return [
        farm_inputs.BeefManagementPeriod(
            name='confinement',
            start_date=date(2024, 3, 1),
            days=60,
            group_pairing_number=1,
            number_of_animals=110,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=0,
            is_milk_fed_only=True,
            diet=Diet(
                crude_protein_percentage=12.44,
                forage_percentage=97,
                total_digestible_nutrient_percentage=54.572,
                ash_percentage=10.327,
                starch_percentage=7.081,
                fat_percentage=1.716,
                neutral_detergent_fiber_percentage=53.478,
                metabolizable_energy=1.965),
            housing_type=HousingType.confined_no_barn,
            manure_handling_system=ManureStateType.deep_bedding,
            weather_summary=_WEATHER_SUMMARY),
        farm_inputs.BeefManagementPeriod(
            name='grazing',
            start_date=date(2024, 5, 1),
            days=152,
            group_pairing_number=1,
            number_of_animals=110,
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
            weather_summary=_WEATHER_SUMMARY)
    ]


def _set_beef_finisher_data() -> list[farm_inputs.BeefManagementPeriod]:
    management_period = farm_inputs.BeefManagementPeriod(
        name='Management period #1',
        start_date=date(2024, 1, 19),
        days=170,
        group_pairing_number=0,
        number_of_animals=100,
        production_stage=ProductionStage.gestating,
        number_of_young_animals=0,
        is_milk_fed_only=False,
        diet=Diet(
            crude_protein_percentage=12.72,
            forage_percentage=10,
            total_digestible_nutrient_percentage=81.75,
            ash_percentage=3.38,
            starch_percentage=51.95,
            fat_percentage=2.33,
            neutral_detergent_fiber_percentage=21.95,
            metabolizable_energy=2.92),
        housing_type=HousingType.confined_no_barn,
        manure_handling_system=ManureStateType.deep_bedding,
        weather_summary=_WEATHER_SUMMARY)

    return [management_period]


def _set_beef_stocker_and_backgrounder_data() -> list[farm_inputs.BeefManagementPeriod]:
    management_period = farm_inputs.BeefManagementPeriod(
        name='Management period #1',
        start_date=date(2023, 10, 1),
        days=110,
        group_pairing_number=0,
        number_of_animals=100,
        production_stage=ProductionStage.gestating,
        number_of_young_animals=0,
        is_milk_fed_only=False,
        diet=Diet(
            crude_protein_percentage=12.28,
            forage_percentage=65,
            total_digestible_nutrient_percentage=68.825,
            ash_percentage=6.57,
            starch_percentage=25.825,
            fat_percentage=3.045,
            neutral_detergent_fiber_percentage=42.025,
            metabolizable_energy=2.48),
        housing_type=HousingType.confined_no_barn,
        manure_handling_system=ManureStateType.deep_bedding,
        weather_summary=_WEATHER_SUMMARY)
    return [management_period]


def set_beef_data(weather_summary: WeatherSummary):
    global _WEATHER_SUMMARY
    _WEATHER_SUMMARY = weather_summary
    return farm_inputs.BeefCattleInput(
        Bulls=_set_beef_bulls_data(),
        Cows=_set_beef_cows_data(),
        Calves=_set_beef_calf_data(),
        FinishingHeifers=_set_beef_finisher_data(),
        FinishingSteers=_set_beef_finisher_data(),
        BackgrounderHeifer=_set_beef_stocker_and_backgrounder_data(),
        BackgrounderSteer=_set_beef_stocker_and_backgrounder_data(),
    )
