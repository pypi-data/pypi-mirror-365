from datetime import date

from pyholos.components.animals.common import (BeddingMaterialType, Diet,
                                               HousingType, ManureStateType,
                                               ProductionStage)
from pyholos.farm import farm_inputs
from pyholos.farm.farm_inputs import WeatherSummary

global kwargs
_NUMBER_ANIMALS = 100
_NUMBER_YOUNG_ANIMALS = 0
_GROUP_PAIRING_NUMBER = 1
_DIET = Diet(
    crude_protein_percentage=17.7,
    forage_percentage=0,
    total_digestible_nutrient_percentage=60,
    ash_percentage=8,
    starch_percentage=0,
    fat_percentage=0,
    neutral_detergent_fiber_percentage=0,
    metabolizable_energy=0)
_MANURE_HANDLING_SYSTEM = ManureStateType.pasture
_HOUSING_TYPE = HousingType.confined


def _set_ewes_data() -> list[farm_inputs.SheepManagementPeriod]:
    return [
        farm_inputs.SheepManagementPeriod(
            name='Pregnancy',
            start_date=date(2024, 1, 1),
            days=147,
            production_stage=ProductionStage.gestating,
            **kwargs),
        farm_inputs.SheepManagementPeriod(
            name='Lactation',
            start_date=date(2024, 5, 28),
            days=218,
            production_stage=ProductionStage.lactating,
            **kwargs)
    ]


def _set_lambs_data() -> list[farm_inputs.SheepManagementPeriod]:
    return [
        farm_inputs.SheepManagementPeriod(
            name='Management period #1',
            start_date=date(2025, 1, 1),
            days=30,
            production_stage=ProductionStage.weaning,
            **kwargs)
    ]


def _set_rams_data() -> list[farm_inputs.SheepManagementPeriod]:
    return [
        farm_inputs.SheepManagementPeriod(
            name='Management period #1',
            start_date=date(2025, 1, 1),
            days=30,
            group_pairing_number=0,
            production_stage=ProductionStage.gestating,
            **{k: v for k, v in kwargs.items() if k != 'group_pairing_number'})
    ]


def _set_feedlot_data() -> list[farm_inputs.SheepManagementPeriod]:
    return [
        farm_inputs.SheepManagementPeriod(
            name='Management period #1',
            start_date=date(2025, 1, 1),
            days=30,
            group_pairing_number=0,
            production_stage=ProductionStage.gestating,
            **{k: v for k, v in kwargs.items() if k != 'group_pairing_number'})
    ]


def set_sheep_data(weather_summary: WeatherSummary):
    global kwargs
    kwargs = dict(
        group_pairing_number=_GROUP_PAIRING_NUMBER,
        number_of_animals=_NUMBER_ANIMALS,
        number_of_young_animals=_NUMBER_YOUNG_ANIMALS,
        diet=_DIET,
        housing_type=_HOUSING_TYPE,
        manure_handling_system=_MANURE_HANDLING_SYSTEM,
        bedding_material_type=BeddingMaterialType.straw,
        weather_summary=weather_summary
    )

    return farm_inputs.SheepFlockInput(
        SheepFeedlot=_set_feedlot_data(),
        Rams=_set_rams_data(),
        Ewes=_set_ewes_data(),
        Lambs=_set_lambs_data()
    )
