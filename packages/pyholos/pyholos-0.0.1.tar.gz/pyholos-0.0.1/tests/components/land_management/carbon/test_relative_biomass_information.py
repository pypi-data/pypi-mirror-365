import unittest
from random import choice, randint, random

from pyholos.components.land_management.carbon.relative_biomass_information import (
    BiogasAndMethaneProductionParametersData, NitrogenLigninContentInCropsData,
    RelativeBiomassInformationData, get_nitrogen_lignin_content_in_crops_data,
    get_relative_biomass_information_data, parse_biomethane_data,
    parse_carbon_residue_data, parse_irrigation_data,
    parse_lignin_content_data, parse_nitrogen_lignin_content_in_crops_data,
    parse_nitrogen_residue_data, parse_province_data,
    parse_relative_biomass_information_data, parse_table_7, parse_table_9,
    read_table_7, read_table_9)
from pyholos.components.land_management.common import IrrigationType
from pyholos.components.land_management.crop import (CropType,
                                                     convert_crop_type_name)
from pyholos.common2 import CanadianProvince


class TestParseIrrigationData(unittest.TestCase):

    def test_values(self):
        float_inf = float('inf')
        for raw_input, expected in [
            ("<200 mm", [None, 0, 200]),
            ("<350", [None, 0, 350]),
            (">200mm", [None, 200, float_inf]),
            (">350 mm", [None, 350, float_inf]),
            (">750", [None, 750, float_inf]),
            ("200 -350 mm", [None, 200, 350]),
            ("350-750", [None, 350, 750]),
            ("AB", [None, 0, 0]),
            ("Canada", [None, 0, 0]),
            ("Irrigated", [IrrigationType.Irrigated, 0, 0]),
            ("Rainfed", [IrrigationType.RainFed, 0, 0])
        ]:
            self.assertEqual(
                expected,
                list(parse_irrigation_data(raw_input=raw_input).__dict__.values()))


class TestParseProvinceData(unittest.TestCase):

    def test_values(self):
        for raw_input, expected in [
            ("<200 mm", None),
            ("<350", None),
            (">200mm", None),
            (">350 mm", None),
            (">750", None),
            ("200 -350 mm", None),
            ("350-750", None),
            ("AB", CanadianProvince.Alberta),
            ("Canada", None),
            ("Irrigated", None),
            ("Rainfed", None)
        ]:
            self.assertEqual(
                expected,
                parse_province_data(raw_input=raw_input))


class TestParseCarbonResidueData(unittest.TestCase):
    def test_all_filled_columns(self):
        self.assertNotIn(
            None,
            parse_carbon_residue_data(raw_inputs=[str(v) for v in [random()] * 4]).__dict__.values())

    def test_columns_include_empty_column(self):
        for i in range(4):
            base_columns = [str(v) for v in [random()] * 3]
            base_columns.insert(i, "")
            self.assertEqual(
                0,
                list(parse_carbon_residue_data(raw_inputs=base_columns).__dict__.values())[i])

    def test_all_empty_columns(self):
        self.assertEqual(
            {0},
            set(parse_carbon_residue_data(raw_inputs=[''] * 4).__dict__.values()))


class TestParseNitrogenResidueData(unittest.TestCase):
    def test_all_filled_columns(self):
        self.assertNotIn(
            None,
            parse_nitrogen_residue_data(raw_inputs=[str(v) for v in [randint(0, 100)] * 3]).__dict__.values())

    def test_columns_include_empty_column(self):
        for i in range(4):
            base_columns = [str(v) for v in [randint(0, 100)] * 2]
            base_columns.insert(i, "")
            self.assertEqual(
                0,
                list(parse_nitrogen_residue_data(raw_inputs=base_columns).__dict__.values())[i])

    def test_all_empty_columns(self):
        self.assertEqual(
            {0},
            set(parse_nitrogen_residue_data(raw_inputs=[''] * 3).__dict__.values()))


class TestParseLigninContentData(unittest.TestCase):
    def test_filled_column(self):
        self.assertNotEqual(
            None,
            parse_lignin_content_data(raw_input=str(random())))

    def test_empty_column(self):
        self.assertEqual(
            0,
            parse_lignin_content_data(raw_input=""))


class TestParseBiomethaneData(unittest.TestCase):
    def test_all_filled_columns(self):
        self.assertNotIn(
            None,
            parse_biomethane_data(
                crop_type=choice(list(CropType)),
                raw_inputs=[str(v) for v in [random()] * 5]).__dict__.values()
        )

    def test_columns_include_empty_column(self):
        for i in range(4):
            base_columns = [str(v) for v in [random()] * 4]
            base_columns.insert(i, "")
            self.assertEqual(
                0,
                list(parse_biomethane_data(
                    crop_type=choice(list(CropType)),
                    raw_inputs=base_columns).__dict__.values())[i + 1])

    def test_all_empty_columns(self):
        self.assertEqual(
            {0},
            set(list(parse_biomethane_data(
                crop_type=choice(list(CropType)),
                raw_inputs=[''] * 5).__dict__.values())[1:]))


class TestParseRelativeBiomassInformationData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = read_table_7()

    def test_summer_fallow(self):
        crop_type = CropType.SummerFallow
        actual = parse_relative_biomass_information_data(raw_input=self.lines[0])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=0,
            irrigation_upper_range_limit=0,
            moisture_content_of_product=0,
            relative_biomass_product=0,
            relative_biomass_straw=0,
            relative_biomass_root=0,
            relative_biomass_extraroot=0,
            nitrogen_content_product=0,
            nitrogen_content_straw=0,
            nitrogen_content_root=0,
            nitrogen_content_extraroot=0,
            lignin_content=0,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=0,
            #     methane_fraction=0,
            #     volatile_solids=0,
            #     total_solids=0,
            #     total_nitrogen=0)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_barley_high_irrigation_rate(self):
        crop_type = CropType.Barley
        actual = parse_relative_biomass_information_data(raw_input=self.lines[7])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=750,
            irrigation_upper_range_limit=float('inf'),
            moisture_content_of_product=12,
            relative_biomass_product=0.424,
            relative_biomass_straw=0.498,
            relative_biomass_root=0.047,
            relative_biomass_extraroot=0.031,
            nitrogen_content_product=19,
            nitrogen_content_straw=3.8,
            nitrogen_content_root=9.5,
            nitrogen_content_extraroot=9.5,
            lignin_content=0.046,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=267,
            #     methane_fraction=0.44,
            #     volatile_solids=90,
            #     total_solids=880,
            #     total_nitrogen=6.1)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_canola_medium_irrigation_rate(self):
        crop_type = CropType.Canola
        actual = parse_relative_biomass_information_data(raw_input=self.lines[30])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=200,
            irrigation_upper_range_limit=350,
            moisture_content_of_product=9,
            relative_biomass_product=0.176,
            relative_biomass_straw=0.529,
            relative_biomass_root=0.183,
            relative_biomass_extraroot=0.111,
            nitrogen_content_product=62.1,
            nitrogen_content_straw=9.9,
            nitrogen_content_root=13.4,
            nitrogen_content_extraroot=13.4,
            lignin_content=0.073,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=0,
            #     methane_fraction=0,
            #     volatile_solids=0,
            #     total_solids=0,
            #     total_nitrogen=0)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_berries_and_grapes_canada(self):
        crop_type = CropType.BerriesAndGrapes
        actual = parse_relative_biomass_information_data(raw_input=self.lines[53])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=0,
            irrigation_upper_range_limit=0,
            moisture_content_of_product=85,
            relative_biomass_product=0,
            relative_biomass_straw=0,
            relative_biomass_root=0,
            relative_biomass_extraroot=0,
            nitrogen_content_product=7,
            nitrogen_content_straw=20,
            nitrogen_content_root=10,
            nitrogen_content_extraroot=10,
            lignin_content=0,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=0,
            #     methane_fraction=0,
            #     volatile_solids=0,
            #     total_solids=0,
            #     total_nitrogen=0)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_oat_avena_sativa(self):
        crop_type = CropType.OatAvenaSativa
        actual = parse_relative_biomass_information_data(raw_input=self.lines[71])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=0,
            irrigation_upper_range_limit=0,
            moisture_content_of_product=65,
            relative_biomass_product=0.737,
            relative_biomass_straw=0,
            relative_biomass_root=0.16,
            relative_biomass_extraroot=0.104,
            nitrogen_content_product=24.3,
            nitrogen_content_straw=0,
            nitrogen_content_root=15.7,
            nitrogen_content_extraroot=15.7,
            lignin_content=0.047,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=0,
            #     methane_fraction=0,
            #     volatile_solids=0,
            #     total_solids=0,
            #     total_nitrogen=0)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_sesame_sesamum_indicum(self):
        crop_type = CropType.SesameSesamumIndicum
        actual = parse_relative_biomass_information_data(raw_input=self.lines[73])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=0,
            irrigation_upper_range_limit=0,
            moisture_content_of_product=65,
            relative_biomass_product=0,
            relative_biomass_straw=0,
            relative_biomass_root=0,
            relative_biomass_extraroot=0,
            nitrogen_content_product=0,
            nitrogen_content_straw=12.2,
            nitrogen_content_root=0,
            nitrogen_content_extraroot=0,
            lignin_content=0.053,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=0,
            #     methane_fraction=0,
            #     volatile_solids=0,
            #     total_solids=0,
            #     total_nitrogen=0)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_shepherds_purse(self):
        crop_type = CropType.ShepherdsPurse
        actual = parse_relative_biomass_information_data(raw_input=self.lines[79])
        expected = RelativeBiomassInformationData(
            crop_type=crop_type,
            irrigation_type=None,
            irrigation_lower_range_limit=0,
            irrigation_upper_range_limit=0,
            moisture_content_of_product=65,
            relative_biomass_product=0.352,
            relative_biomass_straw=0,
            relative_biomass_root=0.393,
            relative_biomass_extraroot=0.255,
            nitrogen_content_product=16.3,
            nitrogen_content_straw=0,
            nitrogen_content_root=9.4,
            nitrogen_content_extraroot=9.4,
            lignin_content=0.075,
            province=None,
            # biogas_and_methane_production_parameters_data=BiogasAndMethaneProductionParametersData(
            #     crop_type=crop_type,
            #     bio_methane_potential=0,
            #     methane_fraction=0,
            #     volatile_solids=0,
            #     total_solids=0,
            #     total_nitrogen=0)
        )
        self.assertDictEqual(actual.__dict__, expected.__dict__)


class TestGetRelativeBiomassInformationData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table_7 = parse_table_7()
        cls.included_crops = [v.crop_type for v in cls.table_7]
        cls.irrigation_type = choice(list(IrrigationType))
        cls.irrigation_amount = random()
        cls.province = choice(list(CanadianProvince))

    def setUp(self):
        self.irrigation_type = choice(list(IrrigationType))
        self.irrigation_amount = random()
        self.province = choice(list(CanadianProvince))

    def test_values_for_fallow_or_undefined_crops(self):
        for crop_type in CropType:
            if any([
                crop_type == CropType.NotSelected,
                crop_type.is_fallow()
            ]):
                self.assertEqual(
                    RelativeBiomassInformationData(),
                    get_relative_biomass_information_data(
                        table_7=self.table_7,
                        crop_type=crop_type,
                        irrigation_type=self.irrigation_type,
                        irrigation_amount=self.irrigation_amount,
                        province=choice(list(CanadianProvince))
                    ))

    def test_values_for_grassland_crops(self):
        expected = get_relative_biomass_information_data(
            table_7=self.table_7,
            crop_type=CropType.RangelandNative,
            irrigation_type=self.irrigation_type,
            irrigation_amount=self.irrigation_amount,
            province=self.province)

        for crop_type in CropType:
            if crop_type.is_grassland():
                self.assertEqual(
                    expected,
                    get_relative_biomass_information_data(
                        table_7=self.table_7,
                        crop_type=crop_type,
                        irrigation_type=self.irrigation_type,
                        irrigation_amount=self.irrigation_amount,
                        province=self.province))

    def test_values_for_crops_outside_table(self):
        for crop_type in CropType:
            if not any([
                crop_type in self.included_crops,
                crop_type.is_fallow(),
                crop_type.is_grassland()
            ]):
                self.assertEqual(
                    RelativeBiomassInformationData(),
                    get_relative_biomass_information_data(
                        table_7=self.table_7,
                        crop_type=crop_type,
                        irrigation_type=self.irrigation_type,
                        irrigation_amount=self.irrigation_amount,
                        province=self.province))

    def test_values_for_wheat(self):
        for i, irrigation_amount in [
            (2, 100),
            (3, 250),
            (4, 400)
        ]:
            self.assertEqual(
                self.table_7[i],
                get_relative_biomass_information_data(
                    table_7=self.table_7,
                    crop_type=CropType.Wheat,
                    irrigation_type=self.irrigation_type,
                    irrigation_amount=irrigation_amount,
                    province=self.province))

    def test_values_for_canola(self):
        for i, irrigation_amount in [
            (29, 100),
            (30, 250),
            (31, 400)
        ]:
            self.assertEqual(
                self.table_7[i],
                get_relative_biomass_information_data(
                    table_7=self.table_7,
                    crop_type=CropType.Canola,
                    irrigation_type=self.irrigation_type,
                    irrigation_amount=irrigation_amount,
                    province=self.province))

    def test_values_for_some_crops_having_one_data_row(self):
        for i, crop in [
            (8, CropType.UndersownBarley),
            (38, CropType.Soybeans),
            (49, CropType.Safflower),
            (59, CropType.CrimsonCloverTrifoliumIncarnatum),
        ]:
            self.assertEqual(
                self.table_7[i],
                get_relative_biomass_information_data(
                    table_7=self.table_7,
                    crop_type=crop,
                    irrigation_type=self.irrigation_type,
                    irrigation_amount=self.irrigation_amount,
                    province=self.province))

    def test_values_for_crops_having_specified_irrigation_types(self):
        for i, crop, irrigation_type in [
            (1, CropType.SmallGrainCereals, IrrigationType.RainFed),
            (26, CropType.Oilseeds, IrrigationType.RainFed),
            (27, CropType.Oilseeds, IrrigationType.Irrigated),
            (36, CropType.PulseCrops, IrrigationType.RainFed),
            (37, CropType.PulseCrops, IrrigationType.Irrigated)
        ]:
            self.assertEqual(
                self.table_7[i],
                get_relative_biomass_information_data(
                    table_7=self.table_7,
                    crop_type=crop,
                    irrigation_type=irrigation_type,
                    irrigation_amount=self.irrigation_amount,
                    province=self.province))

    def test_values_for_potato(self):
        for i, province in [
            (46, choice([v for v in CanadianProvince if v != CanadianProvince.Alberta])),
            (47, CanadianProvince.Alberta)
        ]:
            self.assertEqual(
                self.table_7[i],
                get_relative_biomass_information_data(
                    table_7=self.table_7,
                    crop_type=CropType.Potatoes,
                    irrigation_type=self.irrigation_type,
                    irrigation_amount=self.irrigation_amount,
                    province=province))


class TestParseNitrogenLigninContentInCropsData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = read_table_9()

    def test_values_for_summer_fallow(self):
        crop_type = CropType.SummerFallow
        self.assertEqual(
            NitrogenLigninContentInCropsData(
                CropType=crop_type),
            parse_nitrogen_lignin_content_in_crops_data(
                raw_input=self.lines[0]))

    def test_values_for_sorghum(self):
        crop_type = CropType.Sorghum
        self.assertEqual(
            NitrogenLigninContentInCropsData(
                CropType=crop_type,
                InterceptValue=-9,
                SlopeValue=-9,
                RSTRatio=-9,
                NitrogenContentResidues=0.0065,
                LigninContentResidues=0.06,
                MoistureContent=12),
            parse_nitrogen_lignin_content_in_crops_data(
                raw_input=self.lines[6]))

    def test_values_for_wheat(self):
        crop_type = CropType.Durum
        self.assertEqual(
            NitrogenLigninContentInCropsData(
                CropType=crop_type,
                InterceptValue=0.344,
                SlopeValue=0.015,
                RSTRatio=0.229,
                NitrogenContentResidues=0.007,
                LigninContentResidues=0.053,
                MoistureContent=12,
                BiomethaneData=BiogasAndMethaneProductionParametersData(
                    crop_type=crop_type,
                    bio_methane_potential=162,
                    methane_fraction=0.6,
                    volatile_solids=90,
                    total_solids=880,
                    total_nitrogen=7.8)),
            parse_nitrogen_lignin_content_in_crops_data(
                raw_input=self.lines[12]))

    def test_values_for_fall_rye(self):
        for i, crop_type in [
            (11, CropType.Rye),
            (40, CropType.FallRye)
        ]:
            self.assertEqual(
                NitrogenLigninContentInCropsData(
                    CropType=crop_type,
                    InterceptValue=0.344,
                    SlopeValue=0.015,
                    RSTRatio=0.229,
                    NitrogenContentResidues=0.007,
                    LigninContentResidues=0.053,
                    MoistureContent=12,
                    BiomethaneData=BiogasAndMethaneProductionParametersData(
                        crop_type=crop_type,
                        bio_methane_potential=241,
                        methane_fraction=0.44,
                        volatile_solids=94,
                        total_solids=880,
                        total_nitrogen=6)),
                parse_nitrogen_lignin_content_in_crops_data(
                    raw_input=self.lines[i]))


class TestGetNitrogenLigninContentInCropsData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table_9 = parse_table_9()
        cls.included_crops = [(i, v.CropType) for i, v in enumerate(cls.table_9)]

    def test_values_for_wheat(self):
        for crop_type in [
            CropType.Wheat,
            CropType.Durum,
        ]:
            self.assertEqual(
                self.table_9[12],
                get_nitrogen_lignin_content_in_crops_data(
                    table_9=self.table_9,
                    crop_type=crop_type))

    def test_values_for_rye(self):
        for crop_type in [
            CropType.Rye,
            CropType.RyeSecaleCerealeWinterRyeCerealRye,
        ]:
            self.assertEqual(
                self.table_9[11],
                get_nitrogen_lignin_content_in_crops_data(
                    table_9=self.table_9,
                    crop_type=crop_type))

    def test_values_for_all_existing_crop_types(self):
        for i, crop_type in self.included_crops:
            self.assertEqual(
                self.table_9[i],
                get_nitrogen_lignin_content_in_crops_data(
                    crop_type=crop_type,
                    table_9=self.table_9))

    def test_values_for_crops_outside_table(self):
        _, included_crops = zip(*self.included_crops)
        for crop_type in CropType:
            if convert_crop_type_name(name=crop_type.name) not in (
                    list(included_crops) + [CropType.RyeSecaleCerealeWinterRyeCerealRye,
                                            CropType.Wheat]):
                self.assertEqual(
                    NitrogenLigninContentInCropsData(),
                    get_nitrogen_lignin_content_in_crops_data(
                        crop_type=crop_type,
                        table_9=self.table_9))


if __name__ == '__main__':
    unittest.main()
