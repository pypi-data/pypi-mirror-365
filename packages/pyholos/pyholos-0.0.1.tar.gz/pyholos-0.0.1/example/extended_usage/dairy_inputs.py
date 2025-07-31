from datetime import date

from pyholos.components.animals.common import (BeddingMaterialType, Diet,
                                               HousingType, ManureStateType,
                                               Milk, ProductionStage)
from pyholos.farm import farm_inputs
from pyholos.farm.farm_inputs import WeatherSummary

global _WEATHER_SUMMARY
_DIET = Diet(
    crude_protein_percentage=16.146,
    forage_percentage=77.8,
    total_digestible_nutrient_percentage=69.516,
    ash_percentage=6.323,
    starch_percentage=0,
    fat_percentage=0,
    neutral_detergent_fiber_percentage=35.289,
    metabolizable_energy=2.4459)

_HOUSING_TYPE = HousingType.free_stall_barn_solid_litter
_BEDDING_MATERIAL_TYPE = BeddingMaterialType.sand
_NUMBER_ANIMALS = 20
_NUMBER_YOUNG_ANIMALS = 0


def _set_dairy_heifers_data() -> list[farm_inputs.DairyManagementPeriod]:
    return [
        farm_inputs.DairyManagementPeriod(
            name='Management period #1',
            start_date=date(2025, 1, 1),
            days=30,
            group_pairing_number=0,
            number_of_animals=_NUMBER_ANIMALS,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=_NUMBER_YOUNG_ANIMALS,
            milk_data=Milk(),
            diet=_DIET,
            housing_type=_HOUSING_TYPE,
            manure_handling_system=ManureStateType.daily_spread,
            weather_summary=_WEATHER_SUMMARY,
            bedding_material_type=_BEDDING_MATERIAL_TYPE
        )
    ]


def _set_dairy_lactating_cow_data() -> list[farm_inputs.DairyManagementPeriod]:
    kwargs = dict(
        group_pairing_number=1,
        number_of_animals=_NUMBER_ANIMALS,
        production_stage=ProductionStage.gestating,
        number_of_young_animals=_NUMBER_YOUNG_ANIMALS,
        milk_data=Milk(),
        diet=_DIET,
        housing_type=_HOUSING_TYPE,
        manure_handling_system=ManureStateType.pasture,
        weather_summary=_WEATHER_SUMMARY,
        bedding_material_type=_BEDDING_MATERIAL_TYPE)

    return [
        farm_inputs.DairyManagementPeriod(
            name='Early lactation',
            start_date=date(2024, 1, 1),
            days=150,
            **kwargs),
        farm_inputs.DairyManagementPeriod(
            name='Mid lactation',
            start_date=date(2024, 5, 31),
            days=60,
            **kwargs),
        farm_inputs.DairyManagementPeriod(
            name='Late lactation',
            start_date=date(2024, 7, 31),
            days=95,
            **kwargs),
    ]


def _set_dairy_calves_data() -> list[farm_inputs.DairyManagementPeriod]:
    return [
        farm_inputs.DairyManagementPeriod(
            name='Milk-fed dairy calves. A period of no enteric methane emissions',
            start_date=date(2024, 1, 1),
            days=30,
            group_pairing_number=1,
            number_of_animals=_NUMBER_ANIMALS,
            production_stage=ProductionStage.weaning,
            number_of_young_animals=_NUMBER_YOUNG_ANIMALS,
            milk_data=Milk(),
            diet=_DIET,
            housing_type=_HOUSING_TYPE,
            manure_handling_system=ManureStateType.solid_storage,
            weather_summary=_WEATHER_SUMMARY,
            bedding_material_type=_BEDDING_MATERIAL_TYPE
        )
    ]


def _set_dairy_dry_cow_data() -> list[farm_inputs.DairyManagementPeriod]:
    return [
        farm_inputs.DairyManagementPeriod(
            name='Dry period',
            start_date=date(2024, 11, 5),
            days=60,
            group_pairing_number=0,
            number_of_animals=_NUMBER_ANIMALS,
            production_stage=ProductionStage.gestating,
            number_of_young_animals=_NUMBER_YOUNG_ANIMALS,
            milk_data=Milk(),
            diet=_DIET,
            housing_type=_HOUSING_TYPE,
            manure_handling_system=ManureStateType.solid_storage,
            weather_summary=_WEATHER_SUMMARY,
            bedding_material_type=_BEDDING_MATERIAL_TYPE
        )
    ]


def set_dairy_data(weather_summary: WeatherSummary):
    global _WEATHER_SUMMARY
    _WEATHER_SUMMARY = weather_summary

    return farm_inputs.DairyCattleInput(
        Heifers=_set_dairy_heifers_data(),
        LactatingCow=_set_dairy_lactating_cow_data(),
        Calves=_set_dairy_calves_data(),
        DryCow=_set_dairy_dry_cow_data()
    )
