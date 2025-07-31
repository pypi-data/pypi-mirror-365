import random
import unittest
from itertools import product
from unittest.mock import patch

from pyholos.common import ClimateZones
from pyholos.components.animals import common
from pyholos.components.common import ComponentCategory
from pyholos.config import PathsHolosResources
from pyholos.core_constants import CoreConstants
from pyholos.defaults import Defaults
from pyholos.common2 import CanadianProvince
from pyholos.soil import SoilTexture
from pyholos.utils import read_holos_resource_table
from tests.helpers import utils


class _AnimalGroups:
    young_type: list[common.AnimalType] = [
        common.AnimalType.beef_calf,
        common.AnimalType.dairy_calves,
        common.AnimalType.swine_piglets,
        common.AnimalType.weaned_lamb,
        common.AnimalType.lambs]

    beef_cattle_type: list[common.AnimalType] = [
        common.AnimalType.beef,
        common.AnimalType.beef_backgrounder,
        common.AnimalType.beef_bulls,
        common.AnimalType.beef_backgrounder_heifer,
        common.AnimalType.beef_finishing_steer,
        common.AnimalType.beef_finishing_heifer,
        common.AnimalType.beef_replacement_heifers,
        common.AnimalType.beef_finisher,
        common.AnimalType.beef_backgrounder_steer,
        common.AnimalType.beef_calf,
        common.AnimalType.stockers,
        common.AnimalType.stocker_heifers,
        common.AnimalType.stocker_steers,
        common.AnimalType.beef_cow_lactating,
        common.AnimalType.beef_cow,
        common.AnimalType.beef_cow_dry]

    dairy_cattle_type: list[common.AnimalType] = [
        common.AnimalType.dairy,
        common.AnimalType.dairy_lactating_cow,
        common.AnimalType.dairy_bulls,
        common.AnimalType.dairy_calves,
        common.AnimalType.dairy_dry_cow,
        common.AnimalType.dairy_heifers]

    swine_type: list[common.AnimalType] = [
        common.AnimalType.swine,
        common.AnimalType.swine_finisher,
        common.AnimalType.swine_starter,
        common.AnimalType.swine_lactating_sow,
        common.AnimalType.swine_dry_sow,
        common.AnimalType.swine_grower,
        common.AnimalType.swine_sows,
        common.AnimalType.swine_boar,
        common.AnimalType.swine_gilts,
        common.AnimalType.swine_piglets]

    sheep_type: list[common.AnimalType] = [
        common.AnimalType.sheep,
        common.AnimalType.lambs_and_ewes,
        common.AnimalType.ram,
        common.AnimalType.weaned_lamb,
        common.AnimalType.lambs,
        common.AnimalType.ewes,
        common.AnimalType.sheep_feedlot]

    poultry_type: list[common.AnimalType] = [
        common.AnimalType.poultry,
        common.AnimalType.layers_wet_poultry,
        common.AnimalType.layers_dry_poultry,
        common.AnimalType.layers,
        common.AnimalType.broilers,
        common.AnimalType.turkeys,
        common.AnimalType.ducks,
        common.AnimalType.geese,
        common.AnimalType.chicken_pullets,
        common.AnimalType.chicken_cockerels,
        common.AnimalType.chicken_roosters,
        common.AnimalType.chicken_hens,
        common.AnimalType.young_tom,
        common.AnimalType.tom,
        common.AnimalType.young_turkey_hen,
        common.AnimalType.turkey_hen,
        common.AnimalType.chicken_eggs,
        common.AnimalType.turkey_eggs,
        common.AnimalType.chicks,
        common.AnimalType.poults]

    other_animal_type: list[common.AnimalType] = [
        common.AnimalType.other_livestock,
        common.AnimalType.goats,
        common.AnimalType.alpacas,
        common.AnimalType.deer,
        common.AnimalType.elk,
        common.AnimalType.llamas,
        common.AnimalType.horses,
        common.AnimalType.mules,
        common.AnimalType.bison]

    chicken_type: list[common.AnimalType] = [
        common.AnimalType.chicken,
        common.AnimalType.chicken_hens,
        common.AnimalType.layers,
        common.AnimalType.broilers,
        common.AnimalType.chicken_roosters,
        common.AnimalType.chicken_pullets,
        common.AnimalType.chicken_cockerels,
        common.AnimalType.chicken_eggs,
        common.AnimalType.chicks]

    turkey_type: list[common.AnimalType] = [
        common.AnimalType.turkey_hen,
        common.AnimalType.young_turkey_hen,
        common.AnimalType.tom,
        common.AnimalType.turkey_eggs,
        common.AnimalType.young_tom,
        common.AnimalType.poults]

    layers_type: list[common.AnimalType] = [
        common.AnimalType.layers,
        common.AnimalType.layers_dry_poultry,
        common.AnimalType.layers_wet_poultry]

    lactating_type: list[common.AnimalType] = [
        common.AnimalType.beef_cow_lactating,
        common.AnimalType.beef_cow,
        common.AnimalType.dairy_lactating_cow,
        common.AnimalType.ewes]

    eggs_type: list[common.AnimalType] = [
        common.AnimalType.chicken_eggs,
        common.AnimalType.turkey_eggs]

    newly_hatched_type: list[common.AnimalType] = [
        common.AnimalType.poults,
        common.AnimalType.chicks]

    pregnant_type: list[common.AnimalType] = [
        common.AnimalType.beef_cow,
        common.AnimalType.beef_cow_lactating,
        common.AnimalType.dairy_lactating_cow,
        common.AnimalType.dairy_dry_cow,
        common.AnimalType.ewes]


class TestAnimalTypeExtensions(unittest.TestCase):
    def setUp(self):
        self.animal_groups = _AnimalGroups

    def test_is_young_type(self):
        for animal_type in self.animal_groups.young_type:
            self.assertTrue(animal_type.is_young_type)

    def test_is_beef_cattle_type(self):
        for animal_type in self.animal_groups.beef_cattle_type:
            self.assertTrue(animal_type.is_beef_cattle_type())

    def test_is_dairy_cattle_type(self):
        for animal_type in self.animal_groups.dairy_cattle_type:
            self.assertTrue(animal_type.is_dairy_cattle_type())

    def test_is_swine_type(self):
        for animal_type in self.animal_groups.swine_type:
            self.assertTrue(animal_type.is_swine_type())

    def test_is_sheep_type(self):
        for animal_type in self.animal_groups.sheep_type:
            self.assertTrue(animal_type.is_sheep_type())

    def test_is_poultry_type(self):
        for animal_type in self.animal_groups.poultry_type:
            self.assertTrue(animal_type.is_poultry_type())

    def test_is_other_animal_type(self):
        for animal_type in self.animal_groups.other_animal_type:
            self.assertTrue(animal_type.is_other_animal_type())

    def test_is_chicken_type(self):
        for animal_type in self.animal_groups.chicken_type:
            self.assertTrue(animal_type.is_chicken_type())

    def test_is_turkey_type(self):
        for animal_type in self.animal_groups.turkey_type:
            self.assertTrue(animal_type.is_turkey_type())

    def test_is_layers_type(self):
        for animal_type in self.animal_groups.layers_type:
            self.assertTrue(animal_type.is_layers_type())

    def test_is_lactating_type(self):
        for animal_type in self.animal_groups.lactating_type:
            self.assertTrue(animal_type.is_lactating_type())

    def test_is_eggs(self):
        for animal_type in self.animal_groups.eggs_type:
            self.assertTrue(animal_type.is_eggs())

    def test_is_newly_hatched_eggs(self):
        for animal_type in self.animal_groups.newly_hatched_type:
            self.assertTrue(animal_type.is_newly_hatched_eggs())

    def test_is_pregnant_type(self):
        for animal_type in self.animal_groups.pregnant_type:
            self.assertTrue(animal_type.is_pregnant_type())

    def test_get_category_returns_expected_result_when_is_other_animal_type(self):
        self.assertEqual(
            common.AnimalType.other_livestock,
            common.AnimalType.other_livestock.get_category())

    def test_get_category_returns_expected_result_when_is_poultry_type(self):
        self.assertEqual(
            common.AnimalType.poultry,
            common.AnimalType.poultry.get_category())

    def test_get_category_returns_expected_result_when_is_sheep_type(self):
        self.assertEqual(
            common.AnimalType.sheep,
            common.AnimalType.sheep.get_category())

    def test_get_category_returns_expected_result_when_is_swine_type(self):
        self.assertEqual(
            common.AnimalType.swine,
            common.AnimalType.swine.get_category())

    def test_get_category_returns_expected_result_when_is_dairy_cattle_type(self):
        self.assertEqual(
            common.AnimalType.dairy,
            common.AnimalType.dairy.get_category())

    def test_get_category_returns_expected_result_when_is_beef_cattle_type(self):
        for animal_type in [
            common.AnimalType.calf,
            common.AnimalType.cattle,
            common.AnimalType.chicken,
            common.AnimalType.cow_calf,
            common.AnimalType.not_selected,
            common.AnimalType.young_bulls
        ]:
            self.assertEqual(
                common.AnimalType.not_selected,
                animal_type.get_category())

    def test_get_component_category_from_animal_type_when_is_beef_cattle_type(self):
        for animal_type in self.animal_groups.beef_cattle_type:
            self.assertEqual(
                common.ComponentCategory.BeefProduction,
                animal_type.get_component_category_from_animal_type())

    def test_get_component_category_from_animal_type_when_is_dairy_cattle_type(self):
        for animal_type in self.animal_groups.dairy_cattle_type:
            self.assertEqual(
                common.ComponentCategory.Dairy,
                animal_type.get_component_category_from_animal_type())

    def test_get_component_category_from_animal_type_when_is_swine_type(self):
        for animal_type in self.animal_groups.swine_type:
            self.assertEqual(
                common.ComponentCategory.Swine,
                animal_type.get_component_category_from_animal_type())

    def test_get_component_category_from_animal_type_when_is_poultry_type(self):
        for animal_type in self.animal_groups.poultry_type:
            self.assertEqual(
                common.ComponentCategory.Poultry,
                animal_type.get_component_category_from_animal_type())

    def test_get_component_category_from_animal_type_when_is_sheep_type(self):
        for animal_type in self.animal_groups.sheep_type:
            self.assertEqual(
                common.ComponentCategory.Sheep,
                animal_type.get_component_category_from_animal_type())

    def test_get_component_category_from_animal_type_default_values(self):
        for animal_type in common.AnimalType:
            if not any([
                animal_type.is_beef_cattle_type(),
                animal_type.is_dairy_cattle_type(),
                animal_type.is_swine_type(),
                animal_type.is_poultry_type(),
                animal_type.is_sheep_type()
            ]):
                self.assertEqual(
                    common.ComponentCategory.OtherLivestock,
                    animal_type.get_component_category_from_animal_type())


class TestConvertAnimalTypeName(unittest.TestCase):
    def test_beef_cattle_names(self):
        self.assertEqual(
            common.convert_animal_type_name(name="backgrounding"),
            common.AnimalType.beef_backgrounder)
        self.assertEqual(
            common.convert_animal_type_name(name="backgrounder"),
            common.AnimalType.beef_backgrounder)
        self.assertEqual(
            common.convert_animal_type_name(name="backgroundingsteers"),
            common.AnimalType.beef_backgrounder_steer)
        self.assertEqual(
            common.convert_animal_type_name(name="backgroundingheifers"),
            common.AnimalType.beef_backgrounder_heifer)
        self.assertEqual(
            common.convert_animal_type_name(name="beef"),
            common.AnimalType.beef)
        self.assertEqual(
            common.convert_animal_type_name(name="nondairycattle"),
            common.AnimalType.beef)
        self.assertEqual(
            common.convert_animal_type_name(name="beefcattle"),
            common.AnimalType.beef)
        self.assertEqual(
            common.convert_animal_type_name(name="beeffinisher"),
            common.AnimalType.beef_finisher)
        self.assertEqual(
            common.convert_animal_type_name(name="finisher"),
            common.AnimalType.beef_finisher)
        self.assertEqual(
            common.convert_animal_type_name(name="cowcalf"),
            common.AnimalType.cow_calf)
        self.assertEqual(
            common.convert_animal_type_name(name="stockers"),
            common.AnimalType.stockers)
        self.assertEqual(
            common.convert_animal_type_name(name="beefcalves"),
            common.AnimalType.beef_calf)
        self.assertEqual(
            common.convert_animal_type_name(name="beefcalf"),
            common.AnimalType.beef_calf)

    def test_dairy_names(self):
        self.assertEqual(
            common.convert_animal_type_name(name="dairy"),
            common.AnimalType.dairy)
        self.assertEqual(
            common.convert_animal_type_name(name="dairycattle"),
            common.AnimalType.dairy)
        self.assertEqual(
            common.convert_animal_type_name(name="dairybulls"),
            common.AnimalType.dairy_bulls)
        self.assertEqual(
            common.convert_animal_type_name(name="dairydry"),
            common.AnimalType.dairy_dry_cow)
        self.assertEqual(
            common.convert_animal_type_name(name="dairydrycow"),
            common.AnimalType.dairy_dry_cow)
        self.assertEqual(
            common.convert_animal_type_name(name="dairyheifers"),
            common.AnimalType.dairy_heifers)
        self.assertEqual(
            common.convert_animal_type_name(name="dairylactating"),
            common.AnimalType.dairy_lactating_cow)

    def test_swine_names(self):
        self.assertEqual(
            common.convert_animal_type_name(name="boar"),
            common.AnimalType.swine_boar)
        self.assertEqual(
            common.convert_animal_type_name(name="swineboar"),
            common.AnimalType.swine_boar)
        self.assertEqual(
            common.convert_animal_type_name(name="weaners"),
            common.AnimalType.swine_piglets)
        self.assertEqual(
            common.convert_animal_type_name(name="piglets"),
            common.AnimalType.swine_piglets)
        self.assertEqual(
            common.convert_animal_type_name(name="drysow"),
            common.AnimalType.swine_dry_sow)
        self.assertEqual(
            common.convert_animal_type_name(name="sow"),
            common.AnimalType.swine_sows)
        self.assertEqual(
            common.convert_animal_type_name(name="sows"),
            common.AnimalType.swine_sows)
        self.assertEqual(
            common.convert_animal_type_name(name="grower"),
            common.AnimalType.swine_grower)
        self.assertEqual(
            common.convert_animal_type_name(name="hogs"),
            common.AnimalType.swine_grower)
        self.assertEqual(
            common.convert_animal_type_name(name="swinegrower"),
            common.AnimalType.swine_grower)
        self.assertEqual(
            common.convert_animal_type_name(name="lactatingsow"),
            common.AnimalType.swine_lactating_sow)
        self.assertEqual(
            common.convert_animal_type_name(name="swine"),
            common.AnimalType.swine)
        self.assertEqual(
            common.convert_animal_type_name(name="swinefinisher"),
            common.AnimalType.swine_finisher)

    def test_sheep_names(self):
        self.assertEqual(
            common.convert_animal_type_name(name="ewe"),
            common.AnimalType.ewes)
        self.assertEqual(
            common.convert_animal_type_name(name="ewes"),
            common.AnimalType.ewes)
        self.assertEqual(
            common.convert_animal_type_name(name="ram"),
            common.AnimalType.ram)
        self.assertEqual(
            common.convert_animal_type_name(name="sheep"),
            common.AnimalType.sheep)
        self.assertEqual(
            common.convert_animal_type_name(name="sheepandlambs"),
            common.AnimalType.sheep)
        self.assertEqual(
            common.convert_animal_type_name(name="weanedlambs"),
            common.AnimalType.lambs)

    def test_other_livestock_names(self):
        self.assertEqual(
            common.convert_animal_type_name(name="horse"),
            common.AnimalType.horses)
        self.assertEqual(
            common.convert_animal_type_name(name="horses"),
            common.AnimalType.horses)
        self.assertEqual(
            common.convert_animal_type_name(name="goat"),
            common.AnimalType.goats)
        self.assertEqual(
            common.convert_animal_type_name(name="goats"),
            common.AnimalType.goats)
        self.assertEqual(
            common.convert_animal_type_name(name="mules"),
            common.AnimalType.mules)
        self.assertEqual(
            common.convert_animal_type_name(name="mule"),
            common.AnimalType.mules)
        self.assertEqual(
            common.convert_animal_type_name(name="bull"),
            common.AnimalType.beef_bulls)
        self.assertEqual(
            common.convert_animal_type_name(name="llamas"),
            common.AnimalType.llamas)
        self.assertEqual(
            common.convert_animal_type_name(name="alpacas"),
            common.AnimalType.alpacas)
        self.assertEqual(
            common.convert_animal_type_name(name="deer"),
            common.AnimalType.deer)
        self.assertEqual(
            common.convert_animal_type_name(name="elk"),
            common.AnimalType.elk)
        self.assertEqual(
            common.convert_animal_type_name(name="bison"),
            common.AnimalType.bison)

    def test_poultry_names(self):
        self.assertEqual(
            common.convert_animal_type_name(name="poultry"),
            common.AnimalType.poultry)
        self.assertEqual(
            common.convert_animal_type_name(name="poultrypulletsbroilers"),
            common.AnimalType.broilers)
        self.assertEqual(
            common.convert_animal_type_name(name="chickenbroilers"),
            common.AnimalType.broilers)
        self.assertEqual(
            common.convert_animal_type_name(name="broilers"),
            common.AnimalType.broilers)
        self.assertEqual(
            common.convert_animal_type_name(name="chickenpullets"),
            common.AnimalType.chicken_pullets)
        self.assertEqual(
            common.convert_animal_type_name(name="pullets"),
            common.AnimalType.chicken_pullets)
        self.assertEqual(
            common.convert_animal_type_name(name="chicken"),
            common.AnimalType.chicken)
        self.assertEqual(
            common.convert_animal_type_name(name="chickencockerels"),
            common.AnimalType.chicken_cockerels)
        self.assertEqual(
            common.convert_animal_type_name(name="cockerels"),
            common.AnimalType.chicken_cockerels)
        self.assertEqual(
            common.convert_animal_type_name(name="roasters"),
            common.AnimalType.chicken_roosters)
        self.assertEqual(
            common.convert_animal_type_name(name="hens"),
            common.AnimalType.chicken_hens)
        self.assertEqual(
            common.convert_animal_type_name(name="poultryturkeys"),
            common.AnimalType.ducks)
        self.assertEqual(
            common.convert_animal_type_name(name="turkey"),
            common.AnimalType.ducks)
        self.assertEqual(
            common.convert_animal_type_name(name="ducks"),
            common.AnimalType.ducks)
        self.assertEqual(
            common.convert_animal_type_name(name="geese"),
            common.AnimalType.geese)
        self.assertEqual(
            common.convert_animal_type_name(name="turkeys"),
            common.AnimalType.turkeys)
        self.assertEqual(
            common.convert_animal_type_name(name="layersdry"),
            common.AnimalType.layers_dry_poultry)
        self.assertEqual(
            common.convert_animal_type_name(name="layerswet"),
            common.AnimalType.layers_wet_poultry)
        self.assertEqual(
            common.convert_animal_type_name(name="poultrylayers"),
            common.AnimalType.layers)
        self.assertEqual(
            common.convert_animal_type_name(name="chickenlayers"),
            common.AnimalType.layers)
        self.assertEqual(
            common.convert_animal_type_name(name="layers"),
            common.AnimalType.layers)


class TestHousingTypeExtensions(unittest.TestCase):
    def test_is_free_stall(self):
        housing_type = common.HousingType.small_free_stall

        self.assertTrue(housing_type.is_free_stall())
        self.assertTrue(housing_type.is_electrical_consuming_housing_type())

        self.assertFalse(housing_type.is_tie_stall())
        self.assertFalse(housing_type.is_barn())
        self.assertFalse(housing_type.is_feed_lot())
        self.assertFalse(housing_type.is_indoor_housing())
        self.assertFalse(housing_type.is_pasture())

    def test_is_tie_stall(self):
        housing_type = common.HousingType.tie_stall

        self.assertTrue(housing_type.is_tie_stall())
        self.assertTrue(housing_type.is_electrical_consuming_housing_type())

        self.assertFalse(housing_type.is_free_stall())
        self.assertFalse(housing_type.is_barn())
        self.assertFalse(housing_type.is_feed_lot())
        self.assertFalse(housing_type.is_indoor_housing())
        self.assertFalse(housing_type.is_pasture())

    def test_is_barn(self):
        housing_type = common.HousingType.housed_in_barn

        self.assertTrue(housing_type.is_barn())
        self.assertTrue(housing_type.is_indoor_housing())
        self.assertTrue(housing_type.is_electrical_consuming_housing_type())

        self.assertFalse(housing_type.is_free_stall())
        self.assertFalse(housing_type.is_tie_stall())
        self.assertFalse(housing_type.is_feed_lot())
        self.assertFalse(housing_type.is_pasture())

    def test_is_feed_lot(self):
        housing_type = common.HousingType.confined

        self.assertTrue(housing_type.is_feed_lot())
        self.assertTrue(housing_type.is_electrical_consuming_housing_type())

        self.assertFalse(housing_type.is_free_stall())
        self.assertFalse(housing_type.is_tie_stall())
        self.assertFalse(housing_type.is_barn())
        self.assertFalse(housing_type.is_indoor_housing())
        self.assertFalse(housing_type.is_pasture())

    def test_is_pasture(self):
        housing_type = common.HousingType.pasture

        self.assertTrue(housing_type.is_pasture())

        self.assertFalse(housing_type.is_free_stall())
        self.assertFalse(housing_type.is_tie_stall())
        self.assertFalse(housing_type.is_barn())
        self.assertFalse(housing_type.is_feed_lot())
        self.assertFalse(housing_type.is_electrical_consuming_housing_type())
        self.assertFalse(housing_type.is_indoor_housing())


class TestBedding(unittest.TestCase):
    def setUp(self):
        self.animal_groups = _AnimalGroups

    def test_get_default_bedding_rate_for_pasture_rate_is_always_zero(self):
        for bedding_material_type, animal_type in product(common.BeddingMaterialType, common.AnimalType):
            bedding = common.Bedding(
                housing_type=common.HousingType.pasture,
                bedding_material_type=bedding_material_type,
                animal_type=animal_type)

            self.assertEqual(
                0,
                bedding.user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_young_animals_is_always_zero(self):
        for housing_type, bedding_material_type, animal_type in product(
                common.HousingType,
                common.BeddingMaterialType,
                self.animal_groups.young_type):
            bedding = common.Bedding(
                housing_type=housing_type,
                bedding_material_type=bedding_material_type,
                animal_type=animal_type)

            self.assertEqual(
                0,
                bedding.user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_beef_cattle_returns_expected_result(self):
        for animal_type in [v for v in self.animal_groups.beef_cattle_type if not v.is_young_type()]:
            for housing_type in (
                    common.HousingType.confined,
                    common.HousingType.confined_no_barn):
                self.assertEqual(
                    1.5,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.straw,
                        animal_type=animal_type).user_defined_bedding_rate.value)
                self.assertEqual(
                    3.6,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.wood_chip,
                        animal_type=animal_type).user_defined_bedding_rate.value)

            for housing_type in (
                    common.HousingType.housed_in_barn,
                    common.HousingType.housed_in_barn_slurry,
                    common.HousingType.housed_in_barn_solid):
                self.assertEqual(
                    3.5,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.straw,
                        animal_type=animal_type).user_defined_bedding_rate.value)
                self.assertEqual(
                    5,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.wood_chip,
                        animal_type=animal_type).user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_dairy_cattle_returns_expected_result(self):
        for animal_type in [v for v in self.animal_groups.dairy_cattle_type if not v.is_young_type()]:

            for housing_type in (
                    common.HousingType.tie_stall,
                    common.HousingType.tie_stall_slurry,
                    common.HousingType.tie_stall_solid_litter,
                    common.HousingType.small_free_stall,
                    common.HousingType.large_free_stall,
                    common.HousingType.free_stall_barn_flushing,
                    common.HousingType.free_stall_barn_milk_parlour_slurry_flushing,
                    common.HousingType.free_stall_barn_slurry_scraping,
                    common.HousingType.free_stall_barn_solid_litter,
                    common.HousingType.dry_lot):
                self.assertEqual(
                    24.3,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.sand,
                        animal_type=animal_type).user_defined_bedding_rate.value)

                self.assertEqual(
                    0,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.separated_manure_solid,
                        animal_type=animal_type).user_defined_bedding_rate.value)

                self.assertEqual(
                    0.7,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.straw_long,
                        animal_type=animal_type).user_defined_bedding_rate.value)

                self.assertEqual(
                    0.7,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.straw_chopped,
                        animal_type=animal_type).user_defined_bedding_rate.value)

                self.assertEqual(
                    2.1,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.shavings,
                        animal_type=animal_type).user_defined_bedding_rate.value)

                self.assertEqual(
                    2.1,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=common.BeddingMaterialType.sawdust,
                        animal_type=animal_type).user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_sheep_returns_expected_result(self):
        housing_types = [v for v in common.HousingType if not v.is_pasture()]
        for animal_type in [v for v in self.animal_groups.sheep_type if not v.is_young_type()]:
            for bedding_material_type, housing_type in product(
                    common.BeddingMaterialType,
                    housing_types):
                self.assertEqual(
                    0.57,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=bedding_material_type,
                        animal_type=animal_type).user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_swine_returns_expected_result(self):
        housing_types = [v for v in common.HousingType if not v.is_pasture()]
        bedding_material_types = [v for v in common.BeddingMaterialType
                                  if not v == common.BeddingMaterialType.straw_long]
        animal_types = [v for v in self.animal_groups.swine_type if not v.is_young_type()]

        for housing_type, animal_type in product(
                housing_types,
                animal_types):

            self.assertEqual(
                0.7,
                common.Bedding(
                    housing_type=housing_type,
                    bedding_material_type=common.BeddingMaterialType.straw_long,
                    animal_type=animal_type).user_defined_bedding_rate.value)

            for bedding_material_type in bedding_material_types:
                self.assertEqual(
                    0.79,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=bedding_material_type,
                        animal_type=animal_type).user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_poultry_returns_expected_result(self):
        housing_types = [v for v in common.HousingType if not v.is_pasture()]
        bedding_material_types = list(common.BeddingMaterialType)
        animal_types = [v for v in self.animal_groups.poultry_type if not v.is_young_type()]

        animal_types_to_exclude = []
        for housing_type in housing_types:
            for bedding_material_type in (
                    common.BeddingMaterialType.sawdust,
                    common.BeddingMaterialType.straw,
                    common.BeddingMaterialType.shavings):
                for animal_type, expected_value in (
                        (common.AnimalType.broilers, 0.0014),
                        (common.AnimalType.chicken_pullets, 0.0014),
                        (common.AnimalType.layers, 0.0028),
                        (common.AnimalType.chicken_hens, 0.0028),
                        (common.AnimalType.turkey_hen, 0.011),
                        (common.AnimalType.young_turkey_hen, 0.011),
                        (common.AnimalType.tom, 0.011),
                        (common.AnimalType.turkey_eggs, 0.011),
                        (common.AnimalType.young_tom, 0.011),
                        (common.AnimalType.poults, 0.011),
                ):
                    animal_types_to_exclude.append(animal_type)
                    self.assertEqual(
                        expected_value,
                        common.Bedding(
                            housing_type=housing_type,
                            bedding_material_type=bedding_material_type,
                            animal_type=animal_type).user_defined_bedding_rate.value)
        for animal_type, bedding_material_type, housing_type in product(
                [v for v in animal_types if v not in set(animal_types_to_exclude)],
                bedding_material_types,
                housing_types):
            self.assertEqual(
                0,
                common.Bedding(
                    housing_type=housing_type,
                    bedding_material_type=bedding_material_type,
                    animal_type=animal_type).user_defined_bedding_rate.value)

    def test_get_default_bedding_rate_for_other_animal_returns_expected_result(self):
        for housing_type, bedding_material_type in product(
                [v for v in common.HousingType if not v.is_pasture()],
                common.BeddingMaterialType):
            animal_types_to_exclude = []
            for animal_type, expected_value in (
                    (common.AnimalType.llamas, 0.57),
                    (common.AnimalType.alpacas, 0.57),
                    (common.AnimalType.deer, 1.5),
                    (common.AnimalType.elk, 1.5),
                    (common.AnimalType.goats, 0.57),
                    (common.AnimalType.horses, 1.5),
                    (common.AnimalType.mules, 1.5),
                    (common.AnimalType.bison, 1.5)):
                self.assertEqual(
                    expected_value,
                    common.Bedding(
                        housing_type=housing_type,
                        bedding_material_type=bedding_material_type,
                        animal_type=animal_type).user_defined_bedding_rate.value)

                animal_types_to_exclude.append(animal_type)

            for animal_type in self.animal_groups.other_animal_type:
                if all([
                    animal_type not in animal_types_to_exclude,
                    not animal_type.is_young_type()]):
                    self.assertEqual(
                        1,
                        common.Bedding(
                            housing_type=housing_type,
                            bedding_material_type=bedding_material_type,
                            animal_type=animal_type).user_defined_bedding_rate.value)

    def test_get_bedding_material_composition_for_beef_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.beef.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.beef,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_beef_and_wood_chip_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.beef.value,
                BeddingMaterial=common.BeddingMaterialType.wood_chip.value,
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=12.82
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.beef,
                bedding_material_type=common.BeddingMaterialType.wood_chip))

    def test_get_bedding_material_composition_for_dairy_and_sand_returns_expected_results(self):

        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.dairy.value,
                BeddingMaterial=common.BeddingMaterialType.sand.value,
                TotalNitrogenKilogramsDryMatter=0,
                TotalCarbonKilogramsDryMatter=0,
                TotalPhosphorusKilogramsDryMatter=0,
                CarbonToNitrogenRatio=0,
                MoistureContent=0
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.dairy,
                bedding_material_type=common.BeddingMaterialType.sand))

    def test_get_bedding_material_composition_for_dairy_and_separated_manure_solid_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.dairy.value,
                BeddingMaterial=common.BeddingMaterialType.separated_manure_solid.value,
                TotalNitrogenKilogramsDryMatter=0.033,
                TotalCarbonKilogramsDryMatter=0.395,
                TotalPhosphorusKilogramsDryMatter=0,
                CarbonToNitrogenRatio=12,
                MoistureContent=0
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.dairy,
                bedding_material_type=common.BeddingMaterialType.separated_manure_solid))

    def test_get_bedding_material_composition_for_dairy_and_straw_long_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.dairy.value,
                BeddingMaterial=common.BeddingMaterialType.straw_long.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.dairy,
                bedding_material_type=common.BeddingMaterialType.straw_long))

    def test_get_bedding_material_composition_for_dairy_and_straw_chopped_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.dairy.value,
                BeddingMaterial=common.BeddingMaterialType.straw_chopped.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.dairy,
                bedding_material_type=common.BeddingMaterialType.straw_chopped))

    def test_get_bedding_material_composition_for_dairy_and_shavings_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.dairy.value,
                BeddingMaterial=common.BeddingMaterialType.shavings.value,
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.09
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.dairy,
                bedding_material_type=common.BeddingMaterialType.shavings))

    def test_get_bedding_material_composition_for_dairy_and_sawdust_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.dairy.value,
                BeddingMaterial=common.BeddingMaterialType.sawdust.value,
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.99
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.dairy,
                bedding_material_type=common.BeddingMaterialType.sawdust))

    def test_get_bedding_material_composition_for_swine_and_straw_long_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.swine.value,
                BeddingMaterial=common.BeddingMaterialType.straw_long.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.swine,
                bedding_material_type=common.BeddingMaterialType.straw_long))

    def test_get_bedding_material_composition_for_swine_and_straw_chopped_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.swine.value,
                BeddingMaterial=common.BeddingMaterialType.straw_chopped.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.swine,
                bedding_material_type=common.BeddingMaterialType.straw_chopped))

    def test_get_bedding_material_composition_for_sheep_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.sheep.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.sheep,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_sheep_and_shavings_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.sheep.value,
                BeddingMaterial=common.BeddingMaterialType.shavings.value,
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.09
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.sheep,
                bedding_material_type=common.BeddingMaterialType.shavings))

    def test_get_bedding_material_composition_for_poultry_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.poultry.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.poultry,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_poultry_and_shavings_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.poultry.value,
                BeddingMaterial=common.BeddingMaterialType.shavings.value,
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.09
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.poultry,
                bedding_material_type=common.BeddingMaterialType.shavings))

    def test_get_bedding_material_composition_for_poultry_and_sawdust_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.poultry.value,
                BeddingMaterial=common.BeddingMaterialType.sawdust.value,
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.99
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.poultry,
                bedding_material_type=common.BeddingMaterialType.sawdust))

    def test_get_bedding_material_composition_for_llamas_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.llamas.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.llamas,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_alpacas_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.alpacas.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.alpacas,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_deer_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.deer.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.deer,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_elk_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.elk.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.elk,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_goats_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.goats.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.goats,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_horses_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.horses.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.horses,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_mules_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.mules.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.mules,
                bedding_material_type=common.BeddingMaterialType.straw))

    def test_get_bedding_material_composition_for_bison_and_straw_returns_expected_results(self):
        self.assertEqual(
            dict(
                AnimalType=common.AnimalType.bison.value,
                BeddingMaterial=common.BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5
            ),
            common.Bedding.get_bedding_material_composition(
                animal_type=common.AnimalType.bison,
                bedding_material_type=common.BeddingMaterialType.straw))


class TestGetMethaneProducingCapacityOfManure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.animal_types_all = list(common.AnimalType)

    def setUp(self):
        self.animal_types = _AnimalGroups

    def run_test(
            self,
            animal_type: common.AnimalType,
            expected_value: float
    ):
        self.assertEqual(
            expected_value,
            common.get_methane_producing_capacity_of_manure(animal_type=animal_type))

        self.animal_types_all.pop(self.animal_types_all.index(animal_type))
        pass

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_when_is_beef_cattle_type(self):
        for animal_type in self.animal_types.beef_cattle_type:
            self.run_test(animal_type=animal_type, expected_value=0.19)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_when_is_dairy_cattle_type(self):
        for animal_type in self.animal_types.dairy_cattle_type:
            self.run_test(animal_type=animal_type, expected_value=0.24)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_when_is_swine_type(self):
        for animal_type in self.animal_types.swine_type:
            self.run_test(animal_type=animal_type, expected_value=0.48)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_when_is_sheep_type(self):
        for animal_type in self.animal_types.sheep_type:
            self.run_test(animal_type=animal_type, expected_value=0.19)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_chicken_roosters_and_broilers(self):
        for animal_type in [
            common.AnimalType.chicken_roosters,
            common.AnimalType.broilers
        ]:
            self.run_test(animal_type=animal_type, expected_value=0.36)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_chicken_hens_pullets_cockerels_layers(
            self):
        for animal_type in [
            common.AnimalType.chicken_hens,
            common.AnimalType.chicken_pullets,
            common.AnimalType.chicken_cockerels,
            common.AnimalType.layers
        ]:
            self.run_test(animal_type=animal_type, expected_value=0.39)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_goats(self):
        self.run_test(animal_type=common.AnimalType.goats, expected_value=0.18)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_horses(self):
        self.run_test(animal_type=common.AnimalType.horses, expected_value=0.30)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_mules(self):
        self.run_test(animal_type=common.AnimalType.mules, expected_value=0.33)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_llamas_and_alpacas(self):
        for animal_type in [
            common.AnimalType.llamas,
            common.AnimalType.alpacas
        ]:
            self.run_test(animal_type=animal_type, expected_value=0.19)

    def test_get_methane_producing_capacity_of_manure_returns_expected_values_for_bison(self):
        self.run_test(animal_type=common.AnimalType.bison, expected_value=0.1)

    def test_z_get_methane_producing_capacity_of_manure_returns_expected_default_value(self):
        for animal_type in self.animal_types_all:
            self.run_test(animal_type=animal_type, expected_value=0)


class TestGetDefaultMethaneProducingCapacityOfManure(unittest.TestCase):
    def test_get_default_methane_producing_capacity_of_manure_is_constant_for_pasture(self):
        for animal_type in common.AnimalType:
            self.assertEqual(
                0.19,
                common.get_default_methane_producing_capacity_of_manure(is_pasture=True, animal_type=animal_type))


class TestFractionOfOrganicNitrogenMineralizedData(unittest.TestCase):
    def testDefaultValues(self):
        self.assertEqual(
            {0},
            set(common.FractionOfOrganicNitrogenMineralizedData().__dict__.values())
        )


class TestGetFractionOfOrganicNitrogenMineralizedData(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.animal_types = _AnimalGroups
        cls.animal_types_not_beef_or_dairy = [v for v in common.AnimalType if
                                              not any([v.is_beef_cattle_type(), v.is_dairy_cattle_type()])]
        cls.manure_state_type_for_default_values = [v for v in common.ManureStateType if v not in (
            common.ManureStateType.liquid_with_natural_crust,
            common.ManureStateType.liquid_with_solid_cover,
            common.ManureStateType.deep_pit,
            common.ManureStateType.liquid_no_crust)]

    def test_values_when_is_beef_cattle_type_and_manure_handling_is_compost(self):
        for animal_type in self.animal_types.beef_cattle_type:
            for manure_state in (common.ManureStateType.compost_intensive,
                                 common.ManureStateType.compost_passive):
                self.assertEqual(
                    common.FractionOfOrganicNitrogenMineralizedData(
                        fraction_immobilized=0,
                        fraction_mineralized=0.46,
                        fraction_nitrified=0.25,
                        fraction_denitrified=0,
                        n2o_n=0.033,
                        no_n=0.0033,
                        n2_n=0.099,
                        n_leached=0.0575),
                    common.get_fraction_of_organic_nitrogen_mineralized_data(
                        state_type=manure_state,
                        animal_type=animal_type))

    def test_function_values_when_is_beef_cattle_type_and_manure_handling_is_deep_bedding_or_solid_storage(self):
        for animal_type in self.animal_types.beef_cattle_type:
            for manure_state in (common.ManureStateType.deep_bedding,
                                 common.ManureStateType.solid_storage):
                self.assertEqual(
                    common.FractionOfOrganicNitrogenMineralizedData(
                        fraction_immobilized=0,
                        fraction_mineralized=0.28,
                        fraction_nitrified=0.125,
                        fraction_denitrified=0,
                        n2o_n=0.033,
                        no_n=0.0033,
                        n2_n=0.099,
                        n_leached=0.0575),
                    common.get_fraction_of_organic_nitrogen_mineralized_data(
                        state_type=manure_state,
                        animal_type=animal_type))

    def test_values_when_is_dairy_cattle_type_and_manure_handling_is_compost(self):
        for animal_type in self.animal_types.dairy_cattle_type:
            for manure_state in (common.ManureStateType.compost_intensive,
                                 common.ManureStateType.compost_passive):
                self.assertEqual(
                    common.FractionOfOrganicNitrogenMineralizedData(
                        fraction_immobilized=0,
                        fraction_mineralized=0.46,
                        fraction_nitrified=0.282,
                        fraction_denitrified=0.152,
                        n2o_n=0.037,
                        no_n=0.0037,
                        n2_n=0.111,
                        n_leached=0.13),
                    common.get_fraction_of_organic_nitrogen_mineralized_data(
                        state_type=manure_state,
                        animal_type=animal_type))

    def test_values_when_is_dairy_cattle_type_and_manure_handling_is_deep_bedding_or_solid_storage(self):
        for animal_type in self.animal_types.dairy_cattle_type:
            for manure_state in (common.ManureStateType.deep_bedding,
                                 common.ManureStateType.solid_storage):
                self.assertEqual(
                    common.FractionOfOrganicNitrogenMineralizedData(
                        fraction_immobilized=0,
                        fraction_mineralized=0.28,
                        fraction_nitrified=0.141,
                        fraction_denitrified=0.076,
                        n2o_n=0.0185,
                        no_n=0.0019,
                        n2_n=0.0555,
                        n_leached=0.065),
                    common.get_fraction_of_organic_nitrogen_mineralized_data(
                        state_type=manure_state,
                        animal_type=animal_type))

    def test_values_when_animal_type_is_not_beef_or_dairy_cattle_type_and_manure_handling_is_case_1(self):
        for animal_type in self.animal_types_not_beef_or_dairy:
            for manure_state in (common.ManureStateType.liquid_with_natural_crust,
                                 common.ManureStateType.liquid_with_solid_cover,
                                 common.ManureStateType.deep_pit):
                self.assertEqual(
                    common.FractionOfOrganicNitrogenMineralizedData(
                        fraction_immobilized=0,
                        fraction_mineralized=0.1,
                        fraction_nitrified=0.021,
                        fraction_denitrified=0.021,
                        n2o_n=0.005,
                        no_n=0.0005,
                        n2_n=0.015,
                        n_leached=0),
                    common.get_fraction_of_organic_nitrogen_mineralized_data(
                        state_type=manure_state,
                        animal_type=animal_type))

    def test_values_when_animal_type_is_not_beef_or_dairy_cattle_type_and_manure_handling_is_case_2(self):
        for animal_type in self.animal_types_not_beef_or_dairy:
            self.assertEqual(
                common.FractionOfOrganicNitrogenMineralizedData(
                    fraction_immobilized=0,
                    fraction_mineralized=0.1,
                    fraction_nitrified=0.0,
                    fraction_denitrified=0,
                    n2o_n=0,
                    no_n=0,
                    n2_n=0,
                    n_leached=0),
                common.get_fraction_of_organic_nitrogen_mineralized_data(
                    state_type=common.ManureStateType.liquid_no_crust,
                    animal_type=animal_type))

    def test_default_value(self):
        for animal_type, manure_state in product(self.animal_types_not_beef_or_dairy,
                                                 self.manure_state_type_for_default_values):
            self.assertEqual(
                common.FractionOfOrganicNitrogenMineralizedData(),
                common.get_fraction_of_organic_nitrogen_mineralized_data(
                    state_type=manure_state,
                    animal_type=animal_type))


class TestGetAmmoniaEmissionFactorForStorageOfPoultryManure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.animal_types = _AnimalGroups

    def test_values_for_chicken_hens_and_layers(self):
        for animal_type in ((
                common.AnimalType.chicken_hens,
                common.AnimalType.layers)):
            self.assertEqual(
                0.24,
                common.get_ammonia_emission_factor_for_storage_of_poultry_manure(animal_type=animal_type))

    def test_default_values_for_chicken_type(self):
        for animal_type in [v for v in self.animal_types.chicken_type if v not in (
                common.AnimalType.chicken_hens,
                common.AnimalType.layers
        )]:
            self.assertEqual(
                0.25,
                common.get_ammonia_emission_factor_for_storage_of_poultry_manure(animal_type=animal_type))

    def test_default_values_for_poultry_type(self):
        for animal_type in [v for v in self.animal_types.poultry_type if not v.is_chicken_type()]:
            self.assertEqual(
                0.24,
                common.get_ammonia_emission_factor_for_storage_of_poultry_manure(animal_type=animal_type))


class TestManureStateType(unittest.TestCase):
    def test_is_grazing_area(self):
        for handling_system in (
                common.ManureStateType.paddock,
                common.ManureStateType.range,
                common.ManureStateType.pasture
        ):
            self.assertTrue(handling_system.is_grazing_area())

    def test_is_liquid_manure(self):
        for handling_system in (
                common.ManureStateType.liquid_no_crust,
                common.ManureStateType.liquid_with_natural_crust,
                common.ManureStateType.liquid_with_solid_cover,
                common.ManureStateType.deep_pit
        ):
            self.assertTrue(handling_system.is_liquid_manure())

    def test_is_compost(self):
        for handling_system in (
                common.ManureStateType.compost_intensive,
                common.ManureStateType.compost_passive,
                common.ManureStateType.composted
        ):
            self.assertTrue(handling_system.is_compost())

    def test_is_solid_manure(self):
        for handling_system in common.ManureStateType:
            if not handling_system.is_liquid_manure():
                self.assertTrue(handling_system.is_solid_manure())

    def test_is_covered_system(self):
        for handling_system in (
                common.ManureStateType.liquid_with_natural_crust,
                common.ManureStateType.liquid_with_solid_cover
        ):
            self.assertTrue(handling_system.is_covered_system())


class TestGetAmmoniaEmissionFactorForStorageOfBeefAndDairyCattleManure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.handling_systems = list(common.ManureStateType)

    def run_test(
            self,
            handling_system: common.ManureStateType,
            expected_value: float
    ):
        self.assertEqual(
            expected_value,
            common.get_ammonia_emission_factor_for_storage_of_beef_and_dairy_cattle_manure(
                storage_type=handling_system))
        self.handling_systems.pop(self.handling_systems.index(handling_system))

    def test_values_for_liquid_manure_and_deep_pit_handling_systems(self):
        for handling_system in (
                common.ManureStateType.liquid_no_crust,
                common.ManureStateType.liquid_with_natural_crust,
                common.ManureStateType.liquid_with_solid_cover,
                common.ManureStateType.deep_pit
        ):
            self.run_test(handling_system=handling_system, expected_value=0.13)

    def test_values_for_compost_handling_systems(self):
        for handling_system in (
                common.ManureStateType.compost_intensive,
                common.ManureStateType.compost_passive,
                common.ManureStateType.composted
        ):
            self.run_test(handling_system=handling_system, expected_value=0.7)

    def test_values_for_solid_storage_and_deep_bedding_handling_systems(self):
        for handling_system in (
                common.ManureStateType.solid_storage,
                common.ManureStateType.deep_bedding
        ):
            self.run_test(handling_system=handling_system, expected_value=0.35)

    def test_z_default_values(self):
        for handling_system in self.handling_systems:
            self.run_test(handling_system=handling_system, expected_value=0.)


class TestDiet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.animal_type = _AnimalGroups

    def setUp(self):
        self.diet = common.Diet(
            crude_protein_percentage=15.3,
            forage_percentage=100,
            total_digestible_nutrient_percentage=57.7,
            ash_percentage=10.15,
            starch_percentage=4.35,
            fat_percentage=1.95,
            neutral_detergent_fiber_percentage=49.3,
            metabolizable_energy=2)

    def test_calc_dietary_net_energy_concentration(self):
        self.assertEqual(
            0,
            common.Diet.calc_dietary_net_energy_concentration(
                net_energy_for_maintenance=0,
                net_energy_for_growth=0))

        self.assertEqual(
            0,
            common.Diet.calc_dietary_net_energy_concentration(
                net_energy_for_maintenance=1,
                net_energy_for_growth=-1))

    def test_calc_dietary_net_energy_concentration_for_beef(self):
        self.diet.metabolizable_energy = 0

        self.assertAlmostEqual(
            -6.4,
            self.diet.calc_dietary_net_energy_concentration_for_beef(),
            places=1)

        values = []
        for metabolizable_energy in range(0, 6):
            self.diet.metabolizable_energy = metabolizable_energy
            values.append(self.diet.calc_dietary_net_energy_concentration_for_beef())

        self.assertTrue(utils.assert_is_ascending(values=values))

    def test_calc_dietary_net_energy_concentration_for_dairy(self):
        self.diet.metabolizable_energy = 0

        self.assertAlmostEqual(
            -3.6,
            self.diet.calc_dietary_net_energy_concentration_for_dairy(),
            places=1)

        values = []
        for metabolizable_energy in range(0, 6):
            self.diet.metabolizable_energy = metabolizable_energy
            values.append(self.diet.calc_dietary_net_energy_concentration_for_beef())

        self.assertTrue(utils.assert_is_ascending(values=values))

    def test_calc_methane_conversion_factor_returns_expected_values_when_is_dairy_cattle_type(self):
        for total_digestible_nutrient, expected_value in (
                (65, 0.063),
                (60, 0.065),
                (50, 0.07)):
            self.diet.total_digestible_nutrient_percentage = total_digestible_nutrient
            for animal_type in self.animal_type.dairy_cattle_type:
                self.assertEqual(
                    expected_value,
                    self.diet.calc_methane_conversion_factor(animal_type=animal_type))

    def test_calc_methane_conversion_factor_returns_expected_values_when_is_beef_cattle_type(self):
        for total_digestible_nutrient, expected_value in (
                (65, 0.065),
                (60, 0.07),
                (50, 0.08)):
            self.diet.total_digestible_nutrient_percentage = total_digestible_nutrient
            for animal_type in self.animal_type.beef_cattle_type:
                if animal_type != common.AnimalType.beef_finisher:
                    self.assertEqual(
                        expected_value,
                        self.diet.calc_methane_conversion_factor(animal_type=animal_type))

    def test_calc_methane_conversion_factor_returns_expected_values_for_beef_finisher(self):
        for total_digestible_nutrient, expected_value in (
                (85, 0.03),
                (80, 0.04)):
            self.diet.total_digestible_nutrient_percentage = total_digestible_nutrient
            self.assertEqual(
                expected_value,
                self.diet.calc_methane_conversion_factor(animal_type=common.AnimalType.beef_finisher))

    def test_calc_methane_conversion_factor_returns_expected_value_for_sheep(self):
        for animal_type in _AnimalGroups.sheep_type:
            self.assertEqual(
                0.067,
                self.diet.calc_methane_conversion_factor(animal_type=animal_type))

    def test_calc_methane_conversion_factor_returns_expected_default_values(self):
        for animal_type in common.AnimalType:
            if not any([
                animal_type.is_dairy_cattle_type(),
                animal_type.is_beef_cattle_type(),
                animal_type == common.AnimalType.beef_finisher,
                animal_type.is_sheep_type()
            ]):
                self.assertEqual(
                    None,
                    self.diet.calc_methane_conversion_factor(animal_type=animal_type))


class TestGetEmissionFactorForVolatilizationBasedOnClimate(unittest.TestCase):
    def test_function_returns_expected_value_for_wet_conditions(self):
        self.assertEqual(
            0.014,
            common.get_emission_factor_for_volatilization_based_on_climate(
                mean_annual_precipitation=1000,
                mean_annual_potential_evapotranspiration=700))

    def test_function_returns_expected_value_for_dry_conditions(self):
        self.assertEqual(
            0.005,
            common.get_emission_factor_for_volatilization_based_on_climate(
                mean_annual_precipitation=700,
                mean_annual_potential_evapotranspiration=1000))


class TestGetMethaneConversionFactor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cool_climate_zones = [
            ClimateZones.CoolTemperateMoist,
            ClimateZones.CoolTemperateDry,
            ClimateZones.BorealDry,
            ClimateZones.BorealMoist]

        cls.warm_climate_zones = [
            ClimateZones.WarmTemperateDry,
            ClimateZones.WarmTemperateMoist]

    def test_values_for_solid_and_solid_storage_manure_under_cool_climates(self):
        for manure_state_type in [
            common.ManureStateType.solid,
            common.ManureStateType.solid_storage
        ]:
            for climate_zone in self.cool_climate_zones:
                self.assertEqual(
                    0.02,
                    common.get_methane_conversion_factor(
                        manure_state_type=manure_state_type,
                        climate_zone=climate_zone))

    def test_values_for_solid_and_solid_storage_manure_under_warm_climates(self):
        for manure_state_type in [
            common.ManureStateType.solid,
            common.ManureStateType.solid_storage
        ]:
            for climate_zone in self.warm_climate_zones:
                self.assertEqual(
                    0.04,
                    common.get_methane_conversion_factor(
                        manure_state_type=manure_state_type,
                        climate_zone=climate_zone))

    def test_values_for_compost_intensive_under_cool_climates(self):
        for climate_zone in self.cool_climate_zones:
            self.assertEqual(
                0.005,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.compost_intensive,
                    climate_zone=climate_zone))

    def test_values_for_compost_intensive_under_warm_climates(self):
        for climate_zone in self.warm_climate_zones:
            self.assertEqual(
                0.01,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.compost_intensive,
                    climate_zone=climate_zone))

    def test_values_for_compost_passive_under_cool_climates(self):
        for climate_zone in self.cool_climate_zones:
            self.assertEqual(
                0.01,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.compost_passive,
                    climate_zone=climate_zone))

    def test_values_for_compost_passive_under_warm_climates(self):
        for climate_zone in self.warm_climate_zones:
            self.assertEqual(
                0.02,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.compost_passive,
                    climate_zone=climate_zone))

    def test_values_for_deep_bedding(self):
        for climate_zone, expected_value in [
            (ClimateZones.CoolTemperateMoist, 0.21),
            (ClimateZones.CoolTemperateDry, 0.26),
            (ClimateZones.BorealDry, 0.14),
            (ClimateZones.BorealMoist, 0.14),
            (ClimateZones.WarmTemperateDry, 0.37),
            (ClimateZones.WarmTemperateMoist, 0.41)
        ]:
            self.assertEqual(
                expected_value,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.deep_bedding,
                    climate_zone=climate_zone))

    def test_values_for_compost_in_vessel(self):
        for climate_zone in ClimateZones:
            self.assertEqual(
                0.005,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.composted_in_vessel,
                    climate_zone=climate_zone))

    def test_values_for_daily_spread_under_cool_climates(self):
        for climate_zone in self.cool_climate_zones:
            self.assertEqual(
                0.001,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.daily_spread,
                    climate_zone=climate_zone))

    def test_values_for_daily_spread_under_warm_climates(self):
        for climate_zone in self.warm_climate_zones:
            self.assertEqual(
                0.005,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.daily_spread,
                    climate_zone=climate_zone))

    def test_values_for_deep_pit(self):
        for climate_zone, expected_value in [
            (ClimateZones.CoolTemperateMoist, 0.06),
            (ClimateZones.CoolTemperateDry, 0.08),
            (ClimateZones.BorealDry, 0.04),
            (ClimateZones.BorealMoist, 0.04),
            (ClimateZones.WarmTemperateDry, 0.15),
            (ClimateZones.WarmTemperateMoist, 0.13)
        ]:
            self.assertEqual(
                expected_value,
                common.get_methane_conversion_factor(
                    manure_state_type=common.ManureStateType.deep_pit,
                    climate_zone=climate_zone))

    def test_default_values(self):
        for climate_zone, manure_state_type in product(ClimateZones, common.ManureStateType):
            if manure_state_type not in [
                common.ManureStateType.solid_storage,
                common.ManureStateType.solid,
                common.ManureStateType.compost_intensive,
                common.ManureStateType.compost_passive,
                common.ManureStateType.deep_bedding,
                common.ManureStateType.composted_in_vessel,
                common.ManureStateType.daily_spread,
                common.ManureStateType.deep_pit
            ]:
                self.assertEqual(
                    0,
                    common.get_methane_conversion_factor(
                        manure_state_type=manure_state_type,
                        climate_zone=climate_zone))


class TestGetDirectEmissionFactorBasedOnClimate(unittest.TestCase):
    def test_function_returns_expected_value_for_wet_conditions(self):
        self.assertEqual(
            0.006,
            common.get_direct_emission_factor_based_on_climate(
                mean_annual_precipitation=1000,
                mean_annual_potential_evapotranspiration=700))

    def test_function_returns_expected_value_for_dry_conditions(self):
        self.assertEqual(
            0.002,
            common.get_direct_emission_factor_based_on_climate(
                mean_annual_precipitation=700,
                mean_annual_potential_evapotranspiration=1000))


class TestGetVolatilizationFractionsFromLandAppliedManureDataForSwineType(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = read_holos_resource_table(
            path_file=PathsHolosResources.Table_62_Fractions_of_swine_N_volatilized,
            index_col="Year")
        cls.provinces = [v for v in CanadianProvince if v.value.abbreviation not in ('NT', 'NU', 'YT')]

    def test_func_returns_expected_values(self):
        for province, year in product(self.provinces, self.df.index):
            self.assertEqual(
                self.df.loc[year, province.value.abbreviation],
                common.get_volatilization_fractions_from_land_applied_manure_data_for_swine_type(
                    province=province,
                    year=year))

    def test_func_returns_closest_values(self):
        for province in self.provinces:
            for year, closest_year in [
                (1980, 1990),
                (1994, 1995),
                (2009, 2010),
                (2025, 2020),
            ]:
                self.assertEqual(
                    self.df.loc[closest_year, province.value.abbreviation],
                    common.get_volatilization_fractions_from_land_applied_manure_data_for_swine_type(
                        province=province,
                        year=year))


class TestGetVolatilizationFractionsFromLandAppliedManureDataForDairyCattleManure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = read_holos_resource_table(
            path_file=PathsHolosResources.Table_61_Fractions_of_dairy_cattle_N_volatilized,
            index_col="Year")
        cls.provinces = [v for v in CanadianProvince if v.value.abbreviation not in ('NT', 'NU', 'YT')]

    def test_func_returns_expected_values(self):
        for province, year in product(self.provinces, self.df.index):
            self.assertEqual(
                self.df.loc[year, province.value.abbreviation],
                common.get_volatilization_fractions_from_land_applied_manure_data_for_dairy_cattle_type(
                    province=province,
                    year=year))

    def test_func_returns_closest_values(self):
        for province in self.provinces:
            for year, closest_year in [
                (1980, 1990),
                (1994, 1995),
                (2009, 2010),
                (2025, 2020),
            ]:
                self.assertEqual(
                    self.df.loc[closest_year, province.value.abbreviation],
                    common.get_volatilization_fractions_from_land_applied_manure_data_for_dairy_cattle_type(
                        province=province,
                        year=year))


class TestGetVolatilizationFractionForLandApplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df_dairy = read_holos_resource_table(
            path_file=PathsHolosResources.Table_61_Fractions_of_dairy_cattle_N_volatilized,
            index_col="Year")
        cls.df_swine = read_holos_resource_table(
            path_file=PathsHolosResources.Table_62_Fractions_of_swine_N_volatilized,
            index_col="Year")
        cls.provinces = [v for v in CanadianProvince if v.value.abbreviation not in ('NT', 'NU', 'YT')]

    def test_expected_values_for_swine_type(self):
        for animal_type in _AnimalGroups.swine_type:
            for province, year in product(self.provinces, self.df_swine.index):
                self.assertEqual(
                    self.df_swine.loc[year, province.value.abbreviation],
                    common.get_volatilization_fraction_for_land_application(
                        animal_type=animal_type,
                        province=province,
                        year=year))

    def test_expected_values_for_dairy_cattle_type(self):
        for animal_type in _AnimalGroups.dairy_cattle_type:
            for province, year in product(self.provinces, self.df_dairy.index):
                self.assertEqual(
                    self.df_dairy.loc[year, province.value.abbreviation],
                    common.get_volatilization_fraction_for_land_application(
                        animal_type=animal_type,
                        province=province,
                        year=year))

    def test_default_values(self):
        for animal_type in common.AnimalType:
            if not any([
                animal_type.is_swine_type(),
                animal_type.is_dairy_cattle_type()
            ]):
                for province, year in product(self.provinces, self.df_dairy.index):
                    self.assertEqual(
                        0.21,
                        common.get_volatilization_fraction_for_land_application(
                            animal_type=animal_type,
                            province=province,
                            year=year))


class TestGetLandApplicationFactors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.west_region_provinces = (
            CanadianProvince.Alberta,
            CanadianProvince.BritishColumbia,
            CanadianProvince.Manitoba,
            CanadianProvince.Saskatchewan,
            # CanadianProvince.NorthwestTerritories,
            # CanadianProvince.Nunavut
        )
        cls.east_region_provinces = [v for v in CanadianProvince if all([
            v not in cls.west_region_provinces,
            v.value.abbreviation not in ('NT', 'NU', 'YT')
        ])]

        cls.other_animal_types = [v for v in common.AnimalType if not any([
            v.is_swine_type(),
            v.is_dairy_cattle_type()
        ])]

        cls.year = 1990

        cls.mean_annual_precipitation = 1000
        cls.mean_annual_evapotranspiration = 700
        cls.growing_season_precipitation = 400
        cls.growing_season_evapotranspiration = 570

        cls.emission_factor_volatilization = 0.014

        cls.n2o_direct_emission_factor_west = 0.00043
        cls.n2o_direct_emission_factor_east_fine_soil = 0.0078
        cls.n2o_direct_emission_factor_east_medium_soil = 0.0062
        cls.n2o_direct_emission_factor_east_coarse_soil = 0.0047

        cls.volatilization_fraction_for_other_animal_types = 0.21

        cls.methane_conversion_factor = 0.0047
        cls.emission_factor_leaching = Defaults.EmissionFactorForLeachingAndRunoff.value
        cls.leaching_fraction = common.calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff(
            growing_season_precipitation=cls.growing_season_precipitation,
            growing_season_evapotranspiration=cls.growing_season_evapotranspiration)

        cls.df_dairy = read_holos_resource_table(
            path_file=PathsHolosResources.Table_61_Fractions_of_dairy_cattle_N_volatilized,
            index_col='Year')
        cls.df_swine = read_holos_resource_table(
            path_file=PathsHolosResources.Table_62_Fractions_of_swine_N_volatilized,
            index_col='Year')

    def test_western_regions_for_swine_animal_type(self):
        for province, animal_type, soil_texture in product(
                self.west_region_provinces,
                _AnimalGroups.swine_type,
                SoilTexture
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=soil_texture)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_west,
                volatilization_fraction=self.df_swine.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_western_regions_for_dairy_cattle_animal_type(self):
        for province, animal_type, soil_texture in product(
                self.west_region_provinces,
                _AnimalGroups.dairy_cattle_type,
                SoilTexture
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=soil_texture)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_west,
                volatilization_fraction=self.df_dairy.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_western_regions_for_other_animal_type(self):
        for province, animal_type, soil_texture in product(
                self.west_region_provinces,
                self.other_animal_types,
                SoilTexture
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=soil_texture)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_west,
                volatilization_fraction=self.volatilization_fraction_for_other_animal_types,
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_swine_animal_type_and_fine_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                _AnimalGroups.swine_type,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Fine)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_fine_soil,
                volatilization_fraction=self.df_swine.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_swine_animal_type_and_medium_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                _AnimalGroups.swine_type,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Medium)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_medium_soil,
                volatilization_fraction=self.df_swine.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_swine_animal_type_and_coarse_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                _AnimalGroups.swine_type,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Coarse)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_coarse_soil,
                volatilization_fraction=self.df_swine.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_dairy_animal_type_and_fine_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                _AnimalGroups.dairy_cattle_type,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Fine)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_fine_soil,
                volatilization_fraction=self.df_dairy.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_dairy_animal_type_and_medium_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                _AnimalGroups.dairy_cattle_type,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Medium)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_medium_soil,
                volatilization_fraction=self.df_dairy.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_dairy_animal_type_and_coarse_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                _AnimalGroups.dairy_cattle_type,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Coarse)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_coarse_soil,
                volatilization_fraction=self.df_dairy.loc[self.year, province.value.abbreviation],
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_other_animal_types_and_fine_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                self.other_animal_types,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Fine)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_fine_soil,
                volatilization_fraction=self.volatilization_fraction_for_other_animal_types,
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_other_animal_types_and_medium_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                self.other_animal_types,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Medium)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_medium_soil,
                volatilization_fraction=self.volatilization_fraction_for_other_animal_types,
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)

    def test_eastern_regions_for_other_animal_types_and_coarse_soil_texture(self):
        for province, animal_type in product(
                self.east_region_provinces,
                self.other_animal_types,
        ):
            actual = common.get_land_application_factors(
                province=province,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=animal_type,
                year=self.year,
                soil_texture=SoilTexture.Coarse)
            expected = common.LivestockEmissionConversionFactorsData(
                methane_conversion_factor=self.methane_conversion_factor,
                n2o_direct_emission_factor=self.n2o_direct_emission_factor_east_coarse_soil,
                volatilization_fraction=self.volatilization_fraction_for_other_animal_types,
                emission_factor_volatilization=self.emission_factor_volatilization,
                leaching_fraction=self.leaching_fraction,
                emission_factor_leach=self.emission_factor_leaching,
                methane_enteric_rat=0,
                methane_manure_rate=0,
                nitrogen_excretion_rate=0)

            self.assertEqual(
                expected.__dict__,
                actual.__dict__)


class TestGetManureEmissionFactors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.climate_dependent_methane_conversion_factor = 1

        cls.provinces = [v for v in CanadianProvince if v.value.abbreviation not in ('NT', 'NU', 'YT')]

        cls.year = 1990
        cls.mean_annual_precipitation = 1000
        cls.mean_annual_evapotranspiration = 700
        cls.mean_annual_temperature = 10
        cls.growing_season_precipitation = 383
        cls.growing_season_evapotranspiration = 568
        cls.animal_types = list(common.AnimalType)
        cls.soil_texture = list(common.SoilTexture)

        cls.beef_production_category = [
            v for v in common.AnimalType
            if v.get_component_category_from_animal_type() == ComponentCategory.BeefProduction]
        cls.dairy_production_category = [
            v for v in common.AnimalType
            if v.get_component_category_from_animal_type() == ComponentCategory.Dairy]
        cls.swine_production_category = [
            v for v in common.AnimalType
            if v.get_component_category_from_animal_type() == ComponentCategory.Swine]
        cls.sheep_production_category = [
            v for v in common.AnimalType
            if v.get_component_category_from_animal_type() == ComponentCategory.Sheep]
        cls.poultry_production_category = [
            v for v in common.AnimalType
            if v.get_component_category_from_animal_type() == ComponentCategory.Poultry]
        cls.other_production_category = [
            v for v in common.AnimalType
            if v.get_component_category_from_animal_type() == ComponentCategory.OtherLivestock]

    @patch("pyholos.components.animals.common.get_land_application_factors")
    def test_get_manure_emission_factors_call_same_function_for_pasture_manure_holding_system(self, mocker):
        mocker.return_value = {'foo': 'dummy'}
        res = []
        for manure_state_type, province, animal_type, soil_texture in product(
                [
                    common.ManureStateType.pasture,
                    common.ManureStateType.paddock,
                    common.ManureStateType.range,
                ],
                self.provinces,
                common.AnimalType,
                SoilTexture
        ):
            res.append(
                common.get_land_application_factors(
                    province=province,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    year=self.year,
                    soil_texture=soil_texture)
            )
        for v in res[1:]:
            self.assertEqual(
                res[0],
                v
            )

    def run_test(
            self,
            expected_value: common.LivestockEmissionConversionFactorsData,
            actual_value: common.LivestockEmissionConversionFactorsData,
            look_at_attributes: list[str]
    ):
        expected_value = expected_value.__dict__
        actual_value = actual_value.__dict__
        for s in look_at_attributes:
            self.assertEqual(
                expected_value[s],
                actual_value[s])

    def test_category_beef_production_solid_storage_manure_state(self):
        for animal_type in self.beef_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.01,
                    volatilization_fraction=0.45,
                    leaching_fraction=0.02,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.solid_storage,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_beef_production_compost_intensive_manure_state(self):
        for animal_type in self.beef_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.65,
                    leaching_fraction=0.06,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.compost_intensive,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_beef_production_compost_passive_manure_state(self):
        for animal_type in self.beef_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.6,
                    leaching_fraction=0.04,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.compost_passive,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_beef_production_deep_bedding_manure_state(self):
        for animal_type in self.beef_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.01,
                    volatilization_fraction=0.25,
                    leaching_fraction=0.035,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.deep_bedding,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_beef_production_anaerobic_digester_manure_state(self):
        for animal_type in self.beef_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.01,
                    n2o_direct_emission_factor=0.0006,
                    volatilization_fraction=0.1,
                    leaching_fraction=0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.anaerobic_digester,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_beef_production_error_case(self):
        self.assertEqual(
            common.LivestockEmissionConversionFactorsData().__dict__,
            common.get_manure_emission_factors(
                manure_state_type=common.ManureStateType.daily_spread,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_temperature=self.mean_annual_temperature,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=common.AnimalType.beef,
                province=random.choice(self.provinces),
                year=self.year,
                soil_texture=random.choice(self.soil_texture)).__dict__
        )

    def test_category_dairy_production_daily_spread_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0,
                    volatilization_fraction=0.07,
                    leaching_fraction=0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.daily_spread,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_daily_solid_storage_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.01,
                    volatilization_fraction=0.3,
                    leaching_fraction=0.02,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.solid_storage,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_compost_intensive_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.5,
                    leaching_fraction=0.06,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.compost_intensive,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_compost_passive_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.45,
                    leaching_fraction=0.04,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.compost_passive,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_deep_bedding_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.01,
                    volatilization_fraction=0.25,
                    leaching_fraction=0.035,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.deep_bedding,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_liquid_with_natural_crust_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.3,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.liquid_with_natural_crust,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_liquid_no_crust_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0,
                    volatilization_fraction=0.48,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.liquid_no_crust,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_liquid_with_solid_cover_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.1,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.liquid_with_solid_cover,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_deep_pit_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.002,
                    volatilization_fraction=0.28,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.deep_pit,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_anaerobic_digester_manure_state(self):
        for animal_type in self.dairy_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.01,
                    n2o_direct_emission_factor=0.0006,
                    volatilization_fraction=0.1,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.anaerobic_digester,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_dairy_production_error_case(self):
        with self.assertRaises(ValueError):
            common.get_manure_emission_factors(
                manure_state_type=common.ManureStateType.pit_lagoon_no_cover,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_temperature=self.mean_annual_temperature,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=common.AnimalType.dairy,
                province=random.choice(self.provinces),
                year=self.year,
                soil_texture=random.choice(self.soil_texture))

    def test_category_swine_production_composted_in_vessel_manure_state(self):
        for animal_type in self.swine_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.005,
                    n2o_direct_emission_factor=0.006,
                    volatilization_fraction=0.6,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.composted_in_vessel,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_swine_production_liquid_with_natural_crust_manure_state(self):
        for animal_type in self.swine_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0,
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.3,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.liquid_with_natural_crust,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_swine_production_liquid_no_crust_manure_state(self):
        for animal_type in self.swine_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0,
                    n2o_direct_emission_factor=0,
                    volatilization_fraction=0.48,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.liquid_no_crust,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_swine_production_liquid_with_solid_cover_manure_state(self):
        for animal_type in self.swine_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0,
                    n2o_direct_emission_factor=0.005,
                    volatilization_fraction=0.1,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.liquid_with_solid_cover,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_swine_production_deep_pit_manure_state(self):
        for animal_type in self.swine_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.002,
                    volatilization_fraction=0.25,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.deep_pit,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_swine_production_anaerobic_digester_manure_state(self):
        for animal_type in self.swine_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.01,
                    n2o_direct_emission_factor=0.0006,
                    volatilization_fraction=0.1,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.anaerobic_digester,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_swine_production_error_case(self):
        with self.assertRaises(ValueError):
            common.get_manure_emission_factors(
                manure_state_type=common.ManureStateType.pit_lagoon_no_cover,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_temperature=self.mean_annual_temperature,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=common.AnimalType.swine,
                province=random.choice(self.provinces),
                year=self.year,
                soil_texture=random.choice(self.soil_texture))

    def test_category_sheep_production_solid_storage_manure_state(self):
        for animal_type in self.sheep_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.01,
                    volatilization_fraction=0.12,
                    leaching_fraction=0.02,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.solid_storage,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_sheep_production_error_case(self):
        with self.assertRaises(ValueError):
            common.get_manure_emission_factors(
                manure_state_type=common.ManureStateType.pit_lagoon_no_cover,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_temperature=self.mean_annual_temperature,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=common.AnimalType.sheep,
                province=random.choice(self.provinces),
                year=self.year,
                soil_texture=random.choice(self.soil_texture))

    def test_category_poultry_production_anaerobic_digester_manure_state(self):
        for animal_type in self.poultry_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.01,
                    n2o_direct_emission_factor=0.0006,
                    volatilization_fraction=0.1,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.anaerobic_digester,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_poultry_production_solid_storage_with_or_without_litter_manure_state(self):
        for animal_type in self.poultry_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.015,
                    n2o_direct_emission_factor=0.001,
                    volatilization_fraction=0.4,
                    leaching_fraction=0.0,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.solid_storage_with_or_without_litter,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "MethaneConversionFactor",
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_poultry_production_error_case(self):
        with self.assertRaises(ValueError):
            common.get_manure_emission_factors(
                manure_state_type=common.ManureStateType.compost_intensive,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_temperature=self.mean_annual_temperature,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=common.AnimalType.poultry,
                province=random.choice(self.provinces),
                year=self.year,
                soil_texture=random.choice(self.soil_texture)),

    def test_category_other_livestock_solid_storage_manure_state(self):
        for animal_type in self.other_production_category:
            self.run_test(
                expected_value=common.LivestockEmissionConversionFactorsData(
                    n2o_direct_emission_factor=0.01,
                    volatilization_fraction=0.12,
                    leaching_fraction=0.02,
                    emission_factor_leach=0.011),
                actual_value=common.get_manure_emission_factors(
                    manure_state_type=common.ManureStateType.solid_storage,
                    mean_annual_precipitation=self.mean_annual_precipitation,
                    mean_annual_temperature=self.mean_annual_temperature,
                    mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                    growing_season_precipitation=self.growing_season_precipitation,
                    growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                    animal_type=animal_type,
                    province=random.choice(self.provinces),
                    year=self.year,
                    soil_texture=random.choice(self.soil_texture)),
                look_at_attributes=[
                    "N2ODirectEmissionFactor",
                    "VolatilizationFraction",
                    "LeachingFraction",
                    "EmissionFactorLeach"
                ])

    def test_category_other_livestock_error_case(self):
        with self.assertRaises(ValueError):
            common.get_manure_emission_factors(
                manure_state_type=common.ManureStateType.pit_lagoon_no_cover,
                mean_annual_precipitation=self.mean_annual_precipitation,
                mean_annual_temperature=self.mean_annual_temperature,
                mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                growing_season_precipitation=self.growing_season_precipitation,
                growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                animal_type=common.AnimalType.other_livestock,
                province=random.choice(self.provinces),
                year=self.year,
                soil_texture=random.choice(self.soil_texture))

    def test_error_case(self):
        for animal_type in common.AnimalType:
            if animal_type.get_component_category_from_animal_type() not in [
                ComponentCategory.BeefProduction,
                ComponentCategory.Dairy,
                ComponentCategory.Swine,
                ComponentCategory.Sheep,
                ComponentCategory.Poultry,
                ComponentCategory.OtherLivestock,
            ]:
                with self.assertRaises(ValueError):
                    common.get_manure_emission_factors(
                        manure_state_type=common.ManureStateType.pit_lagoon_no_cover,
                        mean_annual_precipitation=self.mean_annual_precipitation,
                        mean_annual_temperature=self.mean_annual_temperature,
                        mean_annual_evapotranspiration=self.mean_annual_evapotranspiration,
                        growing_season_precipitation=self.growing_season_precipitation,
                        growing_season_evapotranspiration=self.growing_season_evapotranspiration,
                        animal_type=common.AnimalType.other_livestock,
                        province=random.choice(self.provinces),
                        year=self.year,
                        soil_texture=random.choice(self.soil_texture))


class TestGetManureExcretionRate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = read_holos_resource_table(
            path_file=PathsHolosResources.Table_29_Percentage_Total_Manure_Produced_In_Systems,
            index_col="Animal group",
            usecols=["Animal group", "manure_excreted_rate"]).squeeze()

    def test_value_for_beef_animal_type(self):
        for animal_type in _AnimalGroups.beef_cattle_type:
            self.assertEqual(
                self.df.loc['Non-dairy cattle'],
                common.get_manure_excretion_rate(animal_type=animal_type))

    def test_value_for_dairy_animal_type(self):
        for animal_type in _AnimalGroups.dairy_cattle_type:
            self.assertEqual(
                self.df.loc['Dairy cattle'],
                common.get_manure_excretion_rate(animal_type=animal_type))

    def test_value_for_sheep_animal_type(self):
        for animal_type in _AnimalGroups.sheep_type:
            self.assertEqual(
                self.df.loc['Sheep and lambs'],
                common.get_manure_excretion_rate(animal_type=animal_type))

    def test_value_for_swine_animal_type(self):
        for animal_type in _AnimalGroups.swine_type:
            self.assertEqual(
                self.df.loc['Swine'],
                common.get_manure_excretion_rate(animal_type=animal_type))

    def test_value_for_turkey_animal_type(self):
        for animal_type in _AnimalGroups.turkey_type:
            self.assertEqual(
                self.df.loc['Turkeys'],
                common.get_manure_excretion_rate(animal_type=animal_type))

    def test_value_for_poultry_animal_type(self):
        for animal_type in _AnimalGroups.poultry_type:
            if animal_type == common.AnimalType.chicken_hens:
                self.assertEqual(
                    self.df.loc['Chicken layers'],
                    common.get_manure_excretion_rate(animal_type=animal_type))

    def test_values_for_other_animal_types(self):
        for animal_type in common.AnimalType:
            if not any([
                animal_type in _AnimalGroups.beef_cattle_type,
                animal_type in _AnimalGroups.dairy_cattle_type,
                animal_type in _AnimalGroups.sheep_type,
                animal_type in _AnimalGroups.swine_type,
                animal_type in _AnimalGroups.turkey_type,
                animal_type == common.AnimalType.chicken_hens,
                animal_type == common.AnimalType.not_selected,
                animal_type == common.AnimalType.chicken,
                animal_type == common.AnimalType.cow_calf,
                animal_type == common.AnimalType.calf,
                animal_type == common.AnimalType.layers_dry_poultry,
                animal_type == common.AnimalType.layers_wet_poultry,
                animal_type == common.AnimalType.layers_wet_poultry,
                animal_type == common.AnimalType.other_livestock,
                animal_type == common.AnimalType.poultry,
                animal_type == common.AnimalType.young_bulls,
                animal_type == common.AnimalType.chicken_roosters,
                animal_type == common.AnimalType.chicken_eggs,
                animal_type == common.AnimalType.chicks,
                animal_type == common.AnimalType.cattle,
            ]):
                self.assertIsNotNone(
                    common.get_manure_excretion_rate(animal_type=animal_type))


class TestConvertManureStateTypeName(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.used_manure_handling_systems = []

    def run_test(
            self,
            expected_manure_state_type: common.ManureStateType,
            user_defined_manure_state_type: str
    ):
        self.assertEqual(
            expected_manure_state_type,
            common.convert_manure_state_type_name(name=user_defined_manure_state_type))

        self.used_manure_handling_systems.append(self._clearn_text(user_defined_manure_state_type))

    @staticmethod
    def _clearn_text(s: str) -> str:
        return s.lower().strip().replace(' ', '').replace('-', '').replace('/', '')

    def test_value_for_pasture(self):
        for manure_handling_system in [
            "Pasture",
            "Pasture/range/paddock"
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.pasture,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_deep_bedding(self):
        self.run_test(
            expected_manure_state_type=common.ManureStateType.deep_bedding,
            user_defined_manure_state_type="Deep bedding"),

    def test_value_for_solid_storage_with_or_without_litter(self):
        self.run_test(
            expected_manure_state_type=common.ManureStateType.solid_storage_with_or_without_litter,
            user_defined_manure_state_type="Solid storage - with or without litter"),

    def test_value_for_solid_storage(self):
        for manure_handling_system in [
            "Solid storage",
            "Solid-Storage/Stock Piled"
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.solid_storage,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_solid_compost_passive(self):
        for manure_handling_system in [
            "Composted - passive",
            "Compost/Passive- ",
            " Compost-Passive Windrow/",
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.compost_passive,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_solid_compost_intensive(self):
        for manure_handling_system in [
            "Composted/Intensive- ",
            "/ Compost-intensivE/",
            "Compost - intensive windrow",
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.compost_intensive,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_solid_compost_in_vessel(self):
        self.run_test(
            expected_manure_state_type=common.ManureStateType.composted_in_vessel,
            user_defined_manure_state_type="Composted in-vessel"),

    def test_value_for_composted(self):
        self.run_test(
            expected_manure_state_type=common.ManureStateType.composted,
            user_defined_manure_state_type=" // -Composted-/ "),

    def test_value_for_anaerobic_digestion(self):
        for manure_handling_system in [
            "anaerobic--/digestion- ",
            "/ AnaerobicDigesTOR/"
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.anaerobic_digester,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_deep_pit(self):
        for manure_handling_system in [
            " ///DeepPit/- ",
            " Deep pit under barn--/- "
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.deep_pit,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_liquid_with_solid_cover(self):
        for manure_handling_system in [
            "liquid/solid-cover",
            "liquid/with solid cover",
            "liquid-slurry-with Solid/cover"
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.liquid_with_solid_cover,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_liquid_with_natural_crust(self):
        for manure_handling_system in [
            "/liquid/natural crust",
            "LIQUIDWITHNATURALCRUST",
            "Liquid/slurry with natural crust"
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.liquid_with_natural_crust,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_liquid_no_crust(self):
        for manure_handling_system in [
            "liquid no crust",
            "liquid with no crust",
            "Liquid/slurry with no natural crust"
        ]:
            self.run_test(
                expected_manure_state_type=common.ManureStateType.liquid_no_crust,
                user_defined_manure_state_type=manure_handling_system),

    def test_value_for_daily_spread(self):
        self.run_test(
            expected_manure_state_type=common.ManureStateType.daily_spread,
            user_defined_manure_state_type="/Daily/spread "),

    def test_z_default_value(self):
        for manure_handling_system in common.ManureStateType:
            v = manure_handling_system.value
            if self._clearn_text(v) not in self.used_manure_handling_systems:
                self.run_test(
                    expected_manure_state_type=common.ManureStateType.not_selected,
                    user_defined_manure_state_type=v),


class GetDefaultManureCompositionData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simulated_animal_types = []
        _df = read_holos_resource_table(path_file=PathsHolosResources.Table_6_Manure_Types_And_Default_Composition)
        _df['animal_type'] = _df['animal_type'].apply(lambda x: common.convert_animal_type_name(name=x))
        _df.set_index(['animal_type', 'manure_state_type'], inplace=True)
        cls.df = _df

        cls.simulated_animal_types = []

    def run_test(
            self,
            animal_type_in_table: common.AnimalType,
            animal_type: common.AnimalType,
            manure_handling_system: str
    ):
        self.assertEqual(
            self.df.loc[(animal_type_in_table, manure_handling_system)].to_dict(),
            common.get_default_manure_composition_data(
                animal_type=animal_type,
                manure_state_type=common.convert_manure_state_type_name(name=manure_handling_system)).__dict__)

        self.simulated_animal_types.append(animal_type)

    def test_value_for_beef_cattle(self):
        for animal_type, manure_handling_system in product(
                _AnimalGroups.beef_cattle_type,
                ["Pasture/range/paddock",
                 "Deep bedding",
                 "Solid storage",
                 "Compost - passive windrow",
                 "Compost - intensive windrow"
                 ]
        ):
            self.run_test(
                animal_type_in_table=common.AnimalType.beef,
                animal_type=animal_type,
                manure_handling_system=manure_handling_system)

    def test_value_for_dairy_cattle(self):
        for animal_type, manure_handling_system in product(
                _AnimalGroups.dairy_cattle_type,
                [
                    "Pasture/range/paddock",
                    "Deep bedding",
                    "Solid storage",
                    "Compost - passive windrow",
                    "Compost - intensive windrow",
                    "Daily spread",
                    "Liquid/slurry with natural crust",
                    "Liquid/slurry with no natural crust",
                    "Liquid/slurry with solid cover",
                    "Deep pit under barn"
                ]
        ):
            self.run_test(
                animal_type_in_table=common.AnimalType.dairy,
                animal_type=animal_type,
                manure_handling_system=manure_handling_system)

    def test_value_for_sheep(self):
        for animal_type, manure_handling_system in product(
                _AnimalGroups.sheep_type,
                [
                    "Pasture/range/paddock",
                    "Solid storage",
                ]
        ):
            self.run_test(
                animal_type_in_table=common.AnimalType.sheep,
                animal_type=animal_type,
                manure_handling_system=manure_handling_system)

    def test_value_for_swine(self):
        for animal_type, manure_handling_system in product(
                _AnimalGroups.swine_type,
                [
                    "Liquid/slurry with natural crust",
                    "Liquid/slurry with no natural crust",
                    "Liquid/slurry with solid cover",
                    "Deep pit under barn"
                ]
        ):
            self.run_test(
                animal_type_in_table=common.AnimalType.swine,
                animal_type=animal_type,
                manure_handling_system=manure_handling_system)

    def test_value_for_poultry(self):
        for animal_type in _AnimalGroups.poultry_type:
            self.run_test(
                animal_type_in_table=common.AnimalType.poultry,
                animal_type=animal_type,
                manure_handling_system="Solid storage - with or without litter")

    def test_value_for_other_animals(self):
        ls = list(product(
            [
                common.AnimalType.alpacas,
                common.AnimalType.deer,
                common.AnimalType.elk,
                common.AnimalType.goats,
                common.AnimalType.horses,
                common.AnimalType.llamas,
                common.AnimalType.mules
            ],
            [
                "Pasture/range/paddock",
                "Solid storage"
            ]
        ))

        ls = list(ls) + [(common.AnimalType.bison, 'Pasture'),
                         (common.AnimalType.bison, 'Solid storage')]

        for animal_type, manure_handling_system in ls:
            self.run_test(
                animal_type_in_table=animal_type,
                animal_type=animal_type,
                manure_handling_system=manure_handling_system)

    def test_error(self):
        for animal_type in common.AnimalType:
            if animal_type not in self.simulated_animal_types:
                with self.assertRaises(KeyError):
                    self.run_test(
                        animal_type_in_table=animal_type,
                        animal_type=animal_type,
                        manure_handling_system="")


class TestGetBeefAndDairyCattleFeedingActivityCoefficient(unittest.TestCase):
    def test_get_feeding_activity_coefficient_returns_expected_values(self):
        housing_types = list(common.HousingType)

        for housing_type, expected_value in [
            (common.HousingType.housed_in_barn, 0),
            (common.HousingType.confined, 0),
            (common.HousingType.confined_no_barn, 0),
            (common.HousingType.pasture, 0.17),
            (common.HousingType.flat_pasture, 0.17),
            (common.HousingType.enclosed_pasture, 0.17),
            (common.HousingType.open_range_or_hills, 0.36)
        ]:
            self.assertEqual(
                expected_value,
                common.get_beef_and_dairy_cattle_feeding_activity_coefficient(housing_type=housing_type))

            housing_types.pop(housing_types.index(housing_type))

        for housing_type in housing_types:
            self.assertEqual(
                0,
                common.get_beef_and_dairy_cattle_feeding_activity_coefficient(housing_type=housing_type))


class TestGetBeefAndDairyCattleCoefficientData(unittest.TestCase):

    def run_animal_coefficient_data_test(
            self,
            animal_type: common.AnimalType,
            expected_baseline_maintenance_coefficient: float,
            expected_gain_coefficient: float,
            expected_default_initial_weight: float,
            expected_default_final_weight: float
    ) -> None:
        _animal_coefficient_data = common.get_beef_and_dairy_cattle_coefficient_data(animal_type=animal_type.value)
        self.assertEqual(
            expected_baseline_maintenance_coefficient,
            _animal_coefficient_data.baseline_maintenance_coefficient)

        self.assertEqual(
            expected_gain_coefficient,
            _animal_coefficient_data.gain_coefficient)

        self.assertEqual(
            expected_default_initial_weight,
            _animal_coefficient_data.default_initial_weight)

        self.assertEqual(
            expected_default_final_weight,
            _animal_coefficient_data.default_final_weight)

    def test_animal_coefficient_data_returns_expected(self):
        animal_types = list(common.AnimalType)
        for animal_type, (baseline_maintenance_coefficient,
                          gain_coefficient,
                          default_initial_weight,
                          default_final_weight) in [
            (common.AnimalType.beef_calf, (CoreConstants.NotApplicable, CoreConstants.NotApplicable, 39, 90)),
            (common.AnimalType.beef_cow_lactating, (0.386, 0.8, 610, 610)),
            (common.AnimalType.beef_cow_dry, (0.322, 0.8, 610, 610)),
            (common.AnimalType.beef_bulls, (0.37, 1.2, 900, 900)),
            (common.AnimalType.beef_backgrounder_steer, (0.322, 1.0, 250, 380)),
            (common.AnimalType.beef_backgrounder_heifer, (0.322, 0.8, 240, 360)),
            (common.AnimalType.beef_replacement_heifers, (0.322, 0.8, 240, 360)),
            (common.AnimalType.beef_finishing_steer, (0.322, 1.0, 310, 610)),
            (common.AnimalType.beef_finishing_heifer, (0.322, 0.8, 300, 580)),
            (common.AnimalType.dairy_lactating_cow, (0.386, 0.8, 687, 687)),
            (common.AnimalType.dairy_dry_cow, (0.322, 0.8, 687, 687)),
            (common.AnimalType.dairy_heifers, (0.322, 0.8, 637, 687)),
            (common.AnimalType.dairy_bulls, (0.37, 1.2, 1200, 1200)),
            (common.AnimalType.dairy_calves, (0.0, 0.0, 45, 127)),
        ]:
            self.run_animal_coefficient_data_test(
                animal_type=animal_type,
                expected_baseline_maintenance_coefficient=baseline_maintenance_coefficient,
                expected_gain_coefficient=gain_coefficient,
                expected_default_initial_weight=default_initial_weight,
                expected_default_final_weight=default_final_weight)

            animal_types.pop(animal_types.index(animal_type))

        for animal_type in animal_types:
            self.run_animal_coefficient_data_test(
                animal_type=animal_type,
                expected_baseline_maintenance_coefficient=0,
                expected_gain_coefficient=0,
                expected_default_initial_weight=0,
                expected_default_final_weight=0)


class TestGetAverageMilkProductionForDairyCowsValue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table_21 = read_holos_resource_table(
            path_file=PathsHolosResources.Table_21_Average_Milk_Production_For_Dairy_Cows_By_Province,
            index_col='Year')

        cls.provinces = [v for v in CanadianProvince if v not in (
            CanadianProvince.NorthwestTerritories,
            CanadianProvince.Nunavut,
            CanadianProvince.Yukon)]

    def test_original_table_expected_values_returned(self):
        for province in self.provinces:
            for year in self.table_21.index:
                self.assertEqual(
                    self.table_21.loc[year, province.value.abbreviation],
                    common.get_average_milk_production_for_dairy_cows_value(
                        province=province,
                        year=year))

    def test_interpolated_values_returned(self):
        years = range(self.table_21.index.min(), self.table_21.index.max() + 1)
        for province in self.provinces:
            for year in years:
                if year not in self.table_21.index:
                    self.assertIsNotNone(
                        common.get_average_milk_production_for_dairy_cows_value(
                            province=province,
                            year=year))

    def test_values_returned_for_oldest_year_for_years_older_than_oldest_year(self):
        year = self.table_21.index.min()
        for province in self.provinces:
            self.assertEqual(
                self.table_21.loc[year, province.value.abbreviation],
                common.get_average_milk_production_for_dairy_cows_value(
                    province=province,
                    year=year - 1))

    def test_values_returned_for_most_recent_year_for_years_later_than_the_most_recent_year(self):
        year = self.table_21.index.max()
        for province in self.provinces:
            self.assertEqual(
                self.table_21.loc[year, province.value.abbreviation],
                common.get_average_milk_production_for_dairy_cows_value(
                    province=province,
                    year=year + 1))


if __name__ == '__main__':
    unittest.main()
