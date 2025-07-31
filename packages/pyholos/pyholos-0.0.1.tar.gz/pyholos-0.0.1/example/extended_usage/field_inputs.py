from pyholos.components.animals.common import (ManureAnimalSourceTypes,
                                               ManureLocationSourceType,
                                               ManureStateType)
from pyholos.components.land_management.common import (FertilizerBlends,
                                                       HarvestMethod,
                                                       IrrigationType,
                                                       ManureApplicationTypes,
                                                       TillageType)
from pyholos.components.land_management.crop import CropType
from pyholos.farm.farm_inputs import FieldAnnualData, FieldsInput, WeatherData


def set_field_data(weather_data: WeatherData) -> FieldsInput:
    field_annual_data = FieldAnnualData(
        name='field_1',
        field_area=1,
        weather_data=weather_data,
        crop_type=CropType.Wheat,
        crop_yield=2700,
        crop_year=2024,
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
    return FieldsInput(
        fields=field_annual_data
    )
