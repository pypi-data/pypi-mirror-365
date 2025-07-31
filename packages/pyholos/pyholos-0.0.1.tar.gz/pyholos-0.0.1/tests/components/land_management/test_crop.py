import random
import unittest

from pyholos.components.land_management.crop import (
    CropType, convert_crop_type_name, get_alberta_economic_crop_types,
    get_economic_crop_types, get_grassland_types,
    get_manitoba_economic_crop_types, get_nitrogen_fixation,
    get_ontario_economic_crop_types, get_saskatchewan_economic_crop_types,
    get_valid_crop_types, get_valid_perennial_types)
from pyholos.utils import concat_lists
from tests.helpers.utils import CropTypePerCategory


class _EconomicCropTypes:
    alberta = [
        CropType.AlfalfaHay,
        CropType.ArgentineHTCanola,
        CropType.CPSWheat,
        CropType.CerealSilage,
        CropType.DryBean,
        CropType.Durum,
        CropType.FeedBarley,
        CropType.FieldPeas,
        CropType.Flax,
        CropType.TameMixed,
        CropType.KabuliChickpea,
        CropType.MaltBarley,
        CropType.MillingOats,
        CropType.PolishCanola,
        CropType.RedLentils,
        CropType.SoftWheat,
        CropType.SpringWheat,
        CropType.SummerFallow,
        CropType.YellowMustard
    ]
    saskatchewan = [
        CropType.BlackBean,
        CropType.BrownMustard,
        CropType.Camelina,
        CropType.CanarySeed,
        CropType.Canola,
        CropType.CarawayFirstSeason,
        CropType.CarawaySecondSeason,
        CropType.Coriander,
        CropType.Corn,
        CropType.DesiChickpeas,
        CropType.Durum,
        CropType.EdibleGreenPeas,
        CropType.EdibleYellowPeas,
        CropType.FabaBeans,
        CropType.FeedBarley,
        CropType.Fenugreek,
        CropType.Flax,
        CropType.HybridFallRye,
        CropType.LargeGreenLentils,
        CropType.LargeKabuliChickpea,
        CropType.MaltBarley,
        CropType.Oats,
        CropType.OrientalMustard,
        CropType.Quinoa,
        CropType.RedLentils,
        CropType.SmallKabuliChickpea,
        CropType.Soybeans,
        CropType.SpringWheat,
        CropType.SunflowerOilseedEMSS,
        CropType.WinterWheat,
        CropType.YellowMustard
    ]
    manitoba = [
        CropType.Barley,
        CropType.BeansPinto,
        CropType.BeansWhite,
        CropType.Canola,
        CropType.Corn,
        CropType.FlaxSeed,
        CropType.HardRedSpringWheat,
        CropType.HybridFallRye,
        CropType.Oats,
        CropType.Peas,
        CropType.Soybeans,
        CropType.SunflowerConfection,
        CropType.SunflowerOil,
        CropType.WheatNorthernHardRed,
        CropType.WheatOtherSpring,
        CropType.WheatPrairieSpring,
        CropType.WinterWheat
    ]
    ontario = [
        CropType.AlfalfaHay,
        CropType.ColouredBeans,
        CropType.CornSilage,
        CropType.GrainCorn,
        CropType.HardRedSpringWheat,
        CropType.HardRedWinterWheat,
        CropType.HardRedWinterWheatNoTill,
        CropType.NorthernOntarioBarley,
        CropType.NorthernOntarioOats,
        CropType.SoftWinterWheat,
        CropType.SoftWinterWheatNoTill,
        CropType.SouthernOntarioBarley,
        CropType.SouthernOntarioOats,
        CropType.SoybeanNoTill,
        CropType.Soybeans,
        CropType.SoybeansRoundUpReady,
        CropType.SpringCanolaHt,
        CropType.SwitchgrassDirect,
        CropType.SwitchgrassDirectNoTill,
        CropType.SwitchgrassUnderseeded,
        CropType.SwitchgrassUnderseededNoTill,
        CropType.WhiteBlackBeans,
        CropType.WinterCanolaHybrid
    ]


class TestCropTypeExtension(unittest.TestCase):
    def test_is_perennial(self):
        for crop_type in CropTypePerCategory.perennial:
            self.assertTrue(
                crop_type.is_perennial())

    def test_is_pasture(self):
        for crop_type in concat_lists(CropTypePerCategory.perennial, CropTypePerCategory.grassland):
            self.assertTrue(
                crop_type.is_pasture())

    def test_is_cover_crop(self):
        for crop_type in CropTypePerCategory.cover_crop:
            self.assertTrue(
                crop_type.is_cover_crop())

    def test_is_leguminous_cover_crop(self):
        for crop_type in CropTypePerCategory.leguminous_cover_crop:
            self.assertTrue(
                crop_type.is_leguminous_cover_crop())

    def test_is_non_leguminous_cover_crop(self):
        for crop_type in CropTypePerCategory.non_leguminous_cover_crop:
            self.assertTrue(
                crop_type.is_non_leguminous_cover_crop())

    def test_is_rangeland(self):
        self.assertTrue(random.choice(list(CropType)))

    def test_is_grassland(self):
        for crop_type in CropTypePerCategory.grassland:
            self.assertTrue(
                crop_type.is_grassland())

    def test_is_native_grassland(self):
        self.assertTrue(CropTypePerCategory.native_grassland.is_native_grassland())

    def test_is_fallow(self):
        for crop_type in CropTypePerCategory.fallow:
            self.assertTrue(
                crop_type.is_fallow())

    def test_is_annual(self):
        for crop_type in concat_lists(CropTypePerCategory.silage_crop, CropTypePerCategory.root_crops,
                                      CropTypePerCategory.annual):
            self.assertTrue(
                crop_type.is_annual())

    def test_is_silage_crop(self):
        for crop_type in CropTypePerCategory.silage_crop:
            self.assertTrue(
                crop_type.is_silage_crop())

    def test_is_silage_crop_without_defaults(self):
        for crop_type in CropTypePerCategory.silage_crop:
            self.assertTrue(
                crop_type.is_silage_crop_without_defaults())

    def test_get_grain_crop_equivalent_of_silage_crop(self):
        crop_types = []
        for crop_type, grain_crop_equivalent in [
            (CropType.BarleySilage, CropType.Barley),
            (CropType.OatSilage, CropType.Oats),
            (CropType.GrassSilage, CropType.TameLegume),
            (CropType.TriticaleSilage, CropType.Triticale),
            (CropType.WheatSilage, CropType.Wheat),
            (CropType.CornSilage, CropType.GrainCorn),
            (CropType.SilageCorn, CropType.GrainCorn),
            (CropType.CerealSilage, CropType.Cereals)
        ]:
            self.assertEqual(
                grain_crop_equivalent,
                crop_type.get_grain_crop_equivalent_of_silage_crop()
            )
            crop_types.append(crop_type)

        for crop in CropType:
            if crop not in crop_types:
                self.assertIsNone(
                    crop.get_grain_crop_equivalent_of_silage_crop()
                )

    def test_is_root_crop(self):
        for crop_type in CropTypePerCategory.root_crops:
            self.assertTrue(
                crop_type.is_root_crop())

    def test_is_small_grains(self):
        for crop_type in CropTypePerCategory.small_grains:
            self.assertTrue(
                crop_type.is_small_grains())

    def test_is_oil_seed(self):
        for crop_type in CropTypePerCategory.oil_seed:
            self.assertTrue(
                crop_type.is_oil_seed())

    def test_is_other_field_crop(self):
        for crop_type in CropTypePerCategory.other_field_crop:
            self.assertTrue(
                crop_type.is_other_field_crop())

    def test_is_pulse_crop(self):
        for crop_type in CropTypePerCategory.pulse_crop:
            self.assertTrue(
                crop_type.is_pulse_crop())

    def test_is_economic_crop(self):
        self.assertEqual(
            sorted(
                concat_lists(_EconomicCropTypes.alberta,
                             _EconomicCropTypes.manitoba,
                             _EconomicCropTypes.ontario,
                             _EconomicCropTypes.saskatchewan,
                             )),
            get_economic_crop_types()
        )

    def test_national_inventory_report(self):
        for crop_type in CropTypePerCategory.national_inventory_report:
            self.assertTrue(
                crop_type.is_national_inventory_report())

    def test_valid_crop_types(self):
        self.assertEqual(
            sorted(CropTypePerCategory.valid_crop_types),
            get_valid_crop_types()
        )

    def test_valid_perennial_types(self):
        self.assertEqual(
            sorted(CropTypePerCategory.valid_perennial_types),
            get_valid_perennial_types()
        )

    def test_alberta_economic_crop_types(self):
        self.assertEqual(
            sorted(_EconomicCropTypes.alberta),
            get_alberta_economic_crop_types()
        )

    def test_saskatchewan_economic_crop_types(self):
        self.assertEqual(
            sorted(_EconomicCropTypes.saskatchewan),
            get_saskatchewan_economic_crop_types()
        )

    def test_manitoba_economic_crop_types(self):
        self.assertEqual(
            sorted(_EconomicCropTypes.manitoba),
            get_manitoba_economic_crop_types()
        )

    def test_ontario_economic_crop_types(self):
        self.assertEqual(
            sorted(_EconomicCropTypes.ontario),
            get_ontario_economic_crop_types()
        )

    def test_get_grassland_types(self):
        grassland_types = CropTypePerCategory.grassland
        grassland_types.pop(grassland_types.index(CropType.RangelandNative))
        self.assertEqual(
            grassland_types,
            get_grassland_types()
        )


class TestCropTypeConverter(unittest.TestCase):
    def test_alfalfa_seed(self):
        self.assertEqual(
            convert_crop_type_name(name="alfalfaseed"),
            CropType.AlfalfaSeed)

    def test_barley(self):
        self.assertEqual(
            convert_crop_type_name(name="barley"),
            CropType.Barley)

    def test_barley_silage(self):
        self.assertEqual(
            convert_crop_type_name(name="barleysilage"),
            CropType.BarleySilage)

    def test_barley_silage_under_seed(self):
        self.assertEqual(
            convert_crop_type_name(name="barleysilageunderseed"),
            CropType.BarleySilageUnderSeed)

    def test_brome_hay(self):
        self.assertEqual(
            convert_crop_type_name(name="bromehay"),
            CropType.BromeHay)

    def test_grass_silage(self):
        self.assertEqual(
            convert_crop_type_name(name="grasssilage"),
            CropType.GrassSilage)

    def test_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="beans"),
            CropType.Beans)

    def test_beans_dry_field(self):
        for s in ('beansdryfield', 'dryfieldbeans', "dfbns"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.BeansDryField)

    def test_other_dry_field_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="otherdryfieldbeans"),
            CropType.OtherDryFieldBeans)

    def test_berries_and_grapes(self):
        for s in ("berriesgrapes", "berriesandgrapes"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.BerriesAndGrapes)

    def test_buckwheat(self):
        for s in ("buckwheat", "bucwht"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Buckwheat)

    def test_canary_seed(self):
        for s in ('canaryseed', 'canaryseeds', "canary"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.CanarySeed)

    def test_canola(self):
        self.assertEqual(
            convert_crop_type_name(name="canola"),
            CropType.Canola)

    def test_caraway(self):
        self.assertEqual(
            convert_crop_type_name(name="caraway"),
            CropType.Caraway)

    def test_carrot(self):
        self.assertEqual(
            convert_crop_type_name(name="carrot"),
            CropType.Carrot)

    def test_chickpeas(self):
        for s in ("chickpeas", "chickpea"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Chickpeas)

    def test_coloured_white_faba_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="colouredwhitefababeans"),
            CropType.ColouredWhiteFabaBeans)

    def test_cps_wheat(self):
        self.assertEqual(
            convert_crop_type_name(name="cpswheat"),
            CropType.CPSWheat)

    def test_dry_bean(self):
        self.assertEqual(
            convert_crop_type_name(name="drybean"),
            CropType.DryBean)

    def test_dry_peas(self):
        for s in ("drypeas", "drypea", "peasdry"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.DryPeas)

    def test_dry_field_peas(self):
        for s in ("dryfieldpeas", "dfpeas"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.DryFieldPeas)

    def test_dill(self):
        self.assertEqual(
            convert_crop_type_name(name="dill"),
            CropType.Dill)

    def test_durum(self):
        for s in ("durum", "wheatdurum", "durumwheat", "whtdur"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Durum)

    def test_faba_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="fababean"),
            CropType.FabaBeans)

    def test_fallow(self):
        self.assertEqual(
            convert_crop_type_name(name="fallow"),
            CropType.Fallow)

    def test_fall_rye(self):
        for s in ("fallrye", "ryefallremaining", "ryefal"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.FallRye)

    def test_field_peas(self):
        for s in ("fieldpea", "fieldpeas"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.FieldPeas)

    def test_flax(self):
        self.assertEqual(
            convert_crop_type_name(name="flax"),
            CropType.Flax)

    def test_flax_seed(self):
        for s in ("flaxseed", "flaxsd"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.FlaxSeed)

    def test_fresh_corn_sweet(self):
        self.assertEqual(
            convert_crop_type_name(name="freshcornsweet"),
            CropType.FreshCornSweet)

    def test_fresh_peas(self):
        self.assertEqual(
            convert_crop_type_name(name="freshpeas"),
            CropType.FreshPeas)

    def test_forage(self):
        self.assertEqual(
            convert_crop_type_name(name="forage"),
            CropType.Forage)

    def test_fodder_corn(self):
        self.assertEqual(
            convert_crop_type_name(name="foddercorn"),
            CropType.FodderCorn)

    def test_forage_for_seed(self):
        self.assertEqual(
            convert_crop_type_name(name="forageforseed"),
            CropType.ForageForSeed)

    def test_grain_corn(self):
        for s in ("graincorn", "cornforgrain", "corngr"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.GrainCorn)

    def test_grains(self):
        self.assertEqual(
            convert_crop_type_name(name="grains"),
            CropType.Grains)

    def test_generic_grains(self):
        self.assertEqual(
            convert_crop_type_name(name="genericgrains"),
            CropType.GenericGrains)

    def test_corn(self):
        for s in ("corn", "maize"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Corn)

    def test_grain_sorghum(self):
        self.assertEqual(
            convert_crop_type_name(name="grainsorghum"),
            CropType.GrainSorghum)

    def test_grass_seed(self):
        self.assertEqual(
            convert_crop_type_name(name="grassseed"),
            CropType.GrassSeed)

    def test_rangeland_native(self):
        for s in ("rangelandnative", "rangelandlandnative"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.RangelandNative)

    def test_green_feed(self):
        self.assertEqual(
            convert_crop_type_name(name="greenfeed"),
            CropType.GreenFeed)

    def test_hard_red_spring_wheat(self):
        self.assertEqual(
            convert_crop_type_name(name="hardredspringwheat"),
            CropType.HardRedSpringWheat)

    def test_tame_grass(self):
        self.assertEqual(
            convert_crop_type_name(name="tamegrass"),
            CropType.TameGrass)

    def test_grass_hay(self):
        self.assertEqual(
            convert_crop_type_name(name="grasshay"),
            CropType.GrassHay)

    def test_tame_legume(self):
        self.assertEqual(
            convert_crop_type_name(name="tamelegume"),
            CropType.TameLegume)

    def test_non_legume_hay(self):
        self.assertEqual(
            convert_crop_type_name(name="nonlegumehay"),
            CropType.NonLegumeHay)

    def test_tame_mixed(self):
        for s in ("tamemixed", "mixedhay"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.TameMixed)

    def test_hay_and_forage_seed(self):
        self.assertEqual(
            convert_crop_type_name(name="hayandforageseed"),
            CropType.HayAndForageSeed)

    def test_hairy_vetch(self):
        self.assertEqual(
            convert_crop_type_name(name="hairyvetch"),
            CropType.HairyVetch)

    def test_hairy_vetch_and_rye(self):
        self.assertEqual(
            convert_crop_type_name(name="hairyvetchrye"),
            CropType.HairyVetchAndRye)

    def test_hyola(self):
        self.assertEqual(
            convert_crop_type_name(name="hyola"),
            CropType.Hyola)

    def test_lentils(self):
        for s in ("lentils", "lentil"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Lentils)

    def test_linola(self):
        self.assertEqual(
            convert_crop_type_name(name="linola"),
            CropType.Linola)

    def test_malt_barley(self):
        self.assertEqual(
            convert_crop_type_name(name="maltbarley"),
            CropType.MaltBarley)

    def test_market_garden(self):
        self.assertEqual(
            convert_crop_type_name(name="marketgarden"),
            CropType.MarketGarden)

    def test_milk_vetch(self):
        self.assertEqual(
            convert_crop_type_name(name="milkvetch"),
            CropType.MilkVetch)

    def test_millet(self):
        self.assertEqual(
            convert_crop_type_name(name="millet"),
            CropType.Millet)

    def test_mint(self):
        self.assertEqual(
            convert_crop_type_name(name="mint"),
            CropType.Mint)

    def test_mixed_grains(self):
        for s in ("mixedgrains", "mixedgrain", "mxdgrn"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.MixedGrains)

    def test_mustard(self):
        self.assertEqual(
            convert_crop_type_name(name="mustard"),
            CropType.Mustard)

    def test_mustard_seed(self):
        for s in ("mustardseed", "mustsd"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.MustardSeed)

    def test_monarda(self):
        self.assertEqual(
            convert_crop_type_name(name="monarda"),
            CropType.Monarda)

    def test_native_pasture(self):
        self.assertEqual(
            convert_crop_type_name(name="nativepasture"),
            CropType.NativePasture)

    def test_oats(self):
        self.assertEqual(
            convert_crop_type_name(name="oats"),
            CropType.Oats)

    def test_oat_silage(self):
        self.assertEqual(
            convert_crop_type_name(name="oatsilage"),
            CropType.OatSilage)

    def test_oilseeds(self):
        self.assertEqual(
            convert_crop_type_name(name="oilseeds"),
            CropType.Oilseeds)

    def test_onion(self):
        self.assertEqual(
            convert_crop_type_name(name="onion"),
            CropType.Onion)

    def test_other_field_crops(self):
        self.assertEqual(
            convert_crop_type_name(name="otherfieldcrops"),
            CropType.OtherFieldCrops)

    def test_peas(self):
        self.assertEqual(
            convert_crop_type_name(name="peas"),
            CropType.Peas)

    def test_pulses(self):
        self.assertEqual(
            convert_crop_type_name(name="pulses"),
            CropType.Pulses)

    def test_pulse_crops(self):
        self.assertEqual(
            convert_crop_type_name(name="pulsecrops"),
            CropType.PulseCrops)

    def test_seeded_grassland(self):
        self.assertEqual(
            convert_crop_type_name(name="seededgrassland"),
            CropType.SeededGrassland)

    def test_peanuts(self):
        self.assertEqual(
            convert_crop_type_name(name="peanuts"),
            CropType.Peanuts)

    def test_perennial_forages(self):
        self.assertEqual(
            convert_crop_type_name(name="perennialforages"),
            CropType.PerennialForages)

    def test_perennial_grasses(self):
        self.assertEqual(
            convert_crop_type_name(name="perennialgrasses"),
            CropType.PerennialGrasses)

    def test_potatoes(self):
        for s in ("potatoes", "potato", "potats"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Potatoes)

    def test_rice(self):
        self.assertEqual(
            convert_crop_type_name(name="rice"),
            CropType.Rice)

    def test_rye(self):
        for s in ("rye", "ryeall"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Rye)

    def test_safflower(self):
        for s in ("safflower", "safflwr"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Safflower)

    def test_seed_potato(self):
        self.assertEqual(
            convert_crop_type_name(name="seedpotato"),
            CropType.SeedPotato)

    def test_silage_corn(self):
        for s in ("silagecorn", "cornsilage", "cornslg"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.SilageCorn)

    def test_small_fruit(self):
        self.assertEqual(
            convert_crop_type_name(name="smallfruit"),
            CropType.SmallFruit)

    def test_soft_wheat(self):
        self.assertEqual(
            convert_crop_type_name(name="softwheat"),
            CropType.SoftWheat)

    def test_soybeans(self):
        for s in ("soybeans", "soybean", "soybns"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Soybeans)

    def test_sorghum(self):
        self.assertEqual(
            convert_crop_type_name(name="sorghum"),
            CropType.Sorghum)

    def test_sorghum_sudan_grass(self):
        self.assertEqual(
            convert_crop_type_name(name="sorghumsudangrass"),
            CropType.SorghumSudanGrass)

    def test_small_grain_cereals(self):
        self.assertEqual(
            convert_crop_type_name(name="smallgraincereals"),
            CropType.SmallGrainCereals)

    def test_spring_wheat(self):
        for s in ("springwheat", "wheatspring", "whtspg"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.SpringWheat)

    def test_spring_rye(self):
        for s in ("springrye", "ryespring", "ryespg"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.SpringRye)

    def test_sugar_beets(self):
        for s in ("sugarbeets", "sugarb"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.SugarBeets)

    def test_summer_fallow(self):
        self.assertEqual(
            convert_crop_type_name(name="summerfallow"),
            CropType.SummerFallow)

    def test_sunflower(self):
        for s in ("sunflower", "sunfls"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Sunflower)

    def test_sunflower_seed(self):
        for s in ("sunflowerseed", "sunflowerseeds"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.SunflowerSeed)

    def test_tame_pasture(self):
        self.assertEqual(
            convert_crop_type_name(name="tamepasture"),
            CropType.TamePasture)

    def test_timothy_hay(self):
        for s in ("timothyhay", 'ohayfd'):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.TimothyHay)

    def test_tobacco(self):
        self.assertEqual(
            convert_crop_type_name(name="tobacco"),
            CropType.Tobacco)

    def test_tree_fruit_and_nuts(self):
        self.assertEqual(
            convert_crop_type_name(name="totaltreefruitsnuts"),
            CropType.TreeFruitAndNuts)

    def test_triticale(self):
        for s in ("triticale", 'tritcl'):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Triticale)

    def test_tubers(self):
        self.assertEqual(
            convert_crop_type_name(name="tubers"),
            CropType.Tubers)

    def test_turf_sod(self):
        self.assertEqual(
            convert_crop_type_name(name="turfsod"),
            CropType.TurfSod)

    def test_undersown_barley(self):
        self.assertEqual(
            convert_crop_type_name(name="undersownbarley"),
            CropType.UndersownBarley)

    def test_vegetables(self):
        self.assertEqual(
            convert_crop_type_name(name="vegetables"),
            CropType.Vegetables)

    def test_wheat_bolinder(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatbolinder"),
            CropType.WheatBolinder)

    def test_wheat_gan(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatgan"),
            CropType.WheatGan)

    def test_wheat(self):
        for s in ("wheat", "wheatall", "whtall"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.Wheat)

    def test_wheat_rye(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatrye"),
            CropType.WheatRye)

    def test_winter_wheat(self):
        for s in ("winterwheat", "wheatwinter", "wheatwinterremaining", "whtwint"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.WinterWheat)

    def test_winter_weeds(self):
        self.assertEqual(
            convert_crop_type_name(name="winterweeds"),
            CropType.WinterWeeds)

    def test_triticale_silage(self):
        self.assertEqual(
            convert_crop_type_name(name="triticalesilage"),
            CropType.TriticaleSilage)

    def test_wheat_silage(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatsilage"),
            CropType.WheatSilage)

    def test_grass_clover_mixtures(self):
        self.assertEqual(
            convert_crop_type_name(name="grassclovermixtures"),
            CropType.GrassCloverMixtures)

    def test_red_clover_trifolium_pratense_l(self):
        self.assertEqual(
            convert_crop_type_name(name="redclovertrifoliumpratensel"),
            CropType.RedCloverTrifoliumPratenseL)

    def test_berseem_clover_trifolium_alexandrium_l(self):
        self.assertEqual(
            convert_crop_type_name(name="berseemclovertrifoliumalexandriuml"),
            CropType.BerseemCloverTrifoliumAlexandriumL)

    def test_sweet_clover_melilotus_officinalis(self):
        self.assertEqual(
            convert_crop_type_name(name="sweetclovermelilotusofficinalis"),
            CropType.SweetCloverMelilotusOfficinalis)

    def test_crimson_clover_trifolium_incarnatum(self):
        self.assertEqual(
            convert_crop_type_name(name="crimsonclovertrifoliumincarnatum"),
            CropType.CrimsonCloverTrifoliumIncarnatum)

    def test_hairy_vetch_vicia_villosa_roth(self):
        self.assertEqual(
            convert_crop_type_name(name="hairyvetchviciavillosaroth"),
            CropType.HairyVetchViciaVillosaRoth)

    def test_alfalfa_medicago_sativa_l(self):
        self.assertEqual(
            convert_crop_type_name(name="alfalfamedicagosatival"),
            CropType.AlfalfaMedicagoSativaL)

    def test_faba_bean_broad_bean_vicia_faba(self):
        self.assertEqual(
            convert_crop_type_name(name="fababeanbroadbeanviciafaba"),
            CropType.FabaBeanBroadBeanViciaFaba)

    def test_cowpea_vigna_unguiculata(self):
        self.assertEqual(
            convert_crop_type_name(name="cowpeavignaunguiculata"),
            CropType.CowpeaVignaUnguiculata)

    def test_austrian_winter_pea(self):
        self.assertEqual(
            convert_crop_type_name(name="austrianwinterpea"),
            CropType.AustrianWinterPea)

    def test_rapeseed_brassica_napus_l(self):
        self.assertEqual(
            convert_crop_type_name(name="rapeseedbrassicanapusl"),
            CropType.RapeseedBrassicaNapusL)

    def test_winter_turnip_rape_brassica_rapa_spp_oleifera_l_c_v_largo(self):
        self.assertEqual(
            convert_crop_type_name(name="winterturniprapebrassicarapasppoleiferalcvlargo"),
            CropType.WinterTurnipRapeBrassicaRapaSppOleiferaLCVLargo)

    def test_phacelia_phacelia_tanacetifolia_c_v_phaci(self):
        self.assertEqual(
            convert_crop_type_name(name="phaceliaphaceliatanacetifoliacvphaci"),
            CropType.PhaceliaPhaceliaTanacetifoliaCVPhaci)

    def test_forage_radish_raphanus_sativus_l(self):
        self.assertEqual(
            convert_crop_type_name(name="forageradishraphanussativusl"),
            CropType.ForageRadishRaphanusSativusL)

    def test_mustard_sinapus_alba_l_subsp_mairei_h_lindb_maire(self):
        self.assertEqual(
            convert_crop_type_name(name="mustardsinapusalbalsubspmaireihlindbmaire"),
            CropType.MustardSinapusAlbaLSubspMaireiHLindbMaire)

    def test_barley_hordeum_vulgare(self):
        self.assertEqual(
            convert_crop_type_name(name="barleyhordeumvulgare"),
            CropType.BarleyHordeumVulgare)

    def test_oat_avena_sativa(self):
        self.assertEqual(
            convert_crop_type_name(name="oatavenasativa"),
            CropType.OatAvenaSativa)

    def test_rye_secale_cereale_winter_rye_cereal_rye(self):
        self.assertEqual(
            convert_crop_type_name(name="ryesecalecerealewinterryecerealrye"),
            CropType.RyeSecaleCerealeWinterRyeCerealRye)

    def test_sesame_sesamum_indicum(self):
        self.assertEqual(
            convert_crop_type_name(name="sesamesesamumindicum"),
            CropType.SesameSesamumIndicum)

    def test_flax_linum_usitatissimum(self):
        self.assertEqual(
            convert_crop_type_name(name="flaxlinumusitatissimum"),
            CropType.FlaxLinumUsitatissimum)

    def test_rye_grass_lolium_perenne_l(self):
        self.assertEqual(
            convert_crop_type_name(name="ryegrassloliumperennel"),
            CropType.RyeGrassLoliumPerenneL)

    def test_annual_rye_grass_lolium_multiflorum(self):
        self.assertEqual(
            convert_crop_type_name(name="annualryegrassloliummultiflorum"),
            CropType.AnnualRyeGrassLoliumMultiflorum)

    def test_sorghum_sorghum_bicolour(self):
        self.assertEqual(
            convert_crop_type_name(name="sorghumsorghumbicolour"),
            CropType.SorghumSorghumBicolour)

    def test_pigeon_bean(self):
        self.assertEqual(
            convert_crop_type_name(name="pigeonbean"),
            CropType.PigeonBean)

    def test_shepherds_purse(self):
        self.assertEqual(
            convert_crop_type_name(name="shepherdspurse"),
            CropType.ShepherdsPurse)

    def test_winter_wheat_triticum_aestivum(self):
        self.assertEqual(
            convert_crop_type_name(name="winterwheattriticumaestivum"),
            CropType.WinterWheatTriticumAestivum)

    def test_feed_barley(self):
        self.assertEqual(
            convert_crop_type_name(name="feedbarley"),
            CropType.FeedBarley)

    def test_red_lentils(self):
        self.assertEqual(
            convert_crop_type_name(name="redlentil"),
            CropType.RedLentils)

    def test_milling_oats(self):
        self.assertEqual(
            convert_crop_type_name(name="millingoats"),
            CropType.MillingOats)

    def test_polish_canola(self):
        self.assertEqual(
            convert_crop_type_name(name="polishcanola"),
            CropType.PolishCanola)

    def test_argentine_h_t_canola(self):
        self.assertEqual(
            convert_crop_type_name(name="argentinehtcanola"),
            CropType.ArgentineHTCanola)

    def test_kabuli_chickpea(self):
        self.assertEqual(
            convert_crop_type_name(name="kabulichickpea"),
            CropType.KabuliChickpea)

    def test_yellow_mustard(self):
        self.assertEqual(
            convert_crop_type_name(name="yellowmustard"),
            CropType.YellowMustard)

    def test_cereal_silage(self):
        self.assertEqual(
            convert_crop_type_name(name="cerealsilage"),
            CropType.CerealSilage)

    def test_cereals(self):
        self.assertEqual(
            convert_crop_type_name(name="cereals"),
            CropType.Cereals)

    def test_alfalfa_hay(self):
        for s in ("alfalfahay", "alfalfa"):
            self.assertEqual(
                convert_crop_type_name(name=s),
                CropType.AlfalfaHay)

    def test_edible_green_peas(self):
        self.assertEqual(
            convert_crop_type_name(name="ediblegreenpeas"),
            CropType.EdibleGreenPeas)

    def test_edible_yellow_peas(self):
        self.assertEqual(
            convert_crop_type_name(name="edibleyellowpeas"),
            CropType.EdibleYellowPeas)

    def test_black_bean(self):
        self.assertEqual(
            convert_crop_type_name(name="blackbean"),
            CropType.BlackBean)

    def test_hybrid_fall_rye(self):
        self.assertEqual(
            convert_crop_type_name(name="hybridfallrye"),
            CropType.HybridFallRye)

    def test_brown_mustard(self):
        self.assertEqual(
            convert_crop_type_name(name="brownmustard"),
            CropType.BrownMustard)

    def test_oriental_mustard(self):
        self.assertEqual(
            convert_crop_type_name(name="orientalmustard"),
            CropType.OrientalMustard)

    def test_sunflower_oilseed_e_m_s_s(self):
        self.assertEqual(
            convert_crop_type_name(name="sunfloweroilseedemss"),
            CropType.SunflowerOilseedEMSS)

    def test_desi_chickpeas(self):
        self.assertEqual(
            convert_crop_type_name(name="desichickpea"),
            CropType.DesiChickpeas)

    def test_camelina(self):
        self.assertEqual(
            convert_crop_type_name(name="camelina"),
            CropType.Camelina)

    def test_caraway_first_season(self):
        self.assertEqual(
            convert_crop_type_name(name="carawayfirstseason"),
            CropType.CarawayFirstSeason)

    def test_caraway_second_season(self):
        self.assertEqual(
            convert_crop_type_name(name="carawaysecondseason"),
            CropType.CarawaySecondSeason)

    def test_coriander(self):
        self.assertEqual(
            convert_crop_type_name(name="coriander"),
            CropType.Coriander)

    def test_fenugreek(self):
        self.assertEqual(
            convert_crop_type_name(name="fenugreek"),
            CropType.Fenugreek)

    def test_quinoa(self):
        self.assertEqual(
            convert_crop_type_name(name="quinoa"),
            CropType.Quinoa)

    def test_wheat_hard_red_spring(self):
        self.assertEqual(
            convert_crop_type_name(name="wheathardredspring"),
            CropType.WheatHardRedSpring)

    def test_wheat_prairie_spring(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatprairiespring"),
            CropType.WheatPrairieSpring)

    def test_wheat_other_spring(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatotherspring"),
            CropType.WheatOtherSpring)

    def test_beans_pinto(self):
        self.assertEqual(
            convert_crop_type_name(name="beanspinto"),
            CropType.BeansPinto)

    def test_sunflower_confection(self):
        self.assertEqual(
            convert_crop_type_name(name="sunflowerconfection"),
            CropType.SunflowerConfection)

    def test_large_green_lentils(self):
        self.assertEqual(
            convert_crop_type_name(name="largegreenlentils"),
            CropType.LargeGreenLentils)

    def test_wheat_northern_hard_red(self):
        self.assertEqual(
            convert_crop_type_name(name="wheatnorthernhardred"),
            CropType.WheatNorthernHardRed)

    def test_sunflower_oil(self):
        self.assertEqual(
            convert_crop_type_name(name="sunfloweroil"),
            CropType.SunflowerOil)

    def test_beans_white(self):
        self.assertEqual(
            convert_crop_type_name(name="beanswhite"),
            CropType.BeansWhite)

    def test_large_kabuli_chickpea(self):
        self.assertEqual(
            convert_crop_type_name(name="kabulichickpealarge"),
            CropType.LargeKabuliChickpea)

    def test_small_kabuli_chickpea(self):
        self.assertEqual(
            convert_crop_type_name(name="kabulichickpeasmall"),
            CropType.SmallKabuliChickpea)

    def test_coloured_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="colouredbeans"),
            CropType.ColouredBeans)

    def test_hard_red_winter_wheat(self):
        self.assertEqual(
            convert_crop_type_name(name="hardredwinterwheat"),
            CropType.HardRedWinterWheat)

    def test_northern_ontario_barley(self):
        self.assertEqual(
            convert_crop_type_name(name="northernontariobarley"),
            CropType.NorthernOntarioBarley)

    def test_southern_ontario_barley(self):
        self.assertEqual(
            convert_crop_type_name(name="southernontariobarley"),
            CropType.SouthernOntarioBarley)

    def test_northern_ontario_oats(self):
        self.assertEqual(
            convert_crop_type_name(name="northernontariooats"),
            CropType.NorthernOntarioOats)

    def test_southern_ontario_oats(self):
        self.assertEqual(
            convert_crop_type_name(name="southernontariooats"),
            CropType.SouthernOntarioOats)

    def test_spring_canola_ht(self):
        self.assertEqual(
            convert_crop_type_name(name="springcanolaht"),
            CropType.SpringCanolaHt)

    def test_soybean_no_till(self):
        self.assertEqual(
            convert_crop_type_name(name="soybeansnotill"),
            CropType.SoybeanNoTill)

    def test_soybeans_round_up_ready(self):
        self.assertEqual(
            convert_crop_type_name(name="soybeansroundupready"),
            CropType.SoybeansRoundUpReady)

    def test_switchgrass_direct(self):
        self.assertEqual(
            convert_crop_type_name(name="switchgrassdirect"),
            CropType.SwitchgrassDirect)

    def test_switchgrass_direct_no_till(self):
        self.assertEqual(
            convert_crop_type_name(name="switchgrassdirectnotill"),
            CropType.SwitchgrassDirectNoTill)

    def test_switchgrass_underseeded(self):
        self.assertEqual(
            convert_crop_type_name(name="switchgrassunderseeded"),
            CropType.SwitchgrassUnderseeded)

    def test_switchgrass_underseeded_no_till(self):
        self.assertEqual(
            convert_crop_type_name(name="switchgrassunderseedednotill"),
            CropType.SwitchgrassUnderseededNoTill)

    def test_soft_winter_wheat(self):
        self.assertEqual(
            convert_crop_type_name(name="softwinterwheat"),
            CropType.SoftWinterWheat)

    def test_soft_winter_wheat_no_till(self):
        self.assertEqual(
            convert_crop_type_name(name="softwinterwheatnotill"),
            CropType.SoftWinterWheatNoTill)

    def test_white_black_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="whiteblackbeans"),
            CropType.WhiteBlackBeans)

    def test_white_beans(self):
        self.assertEqual(
            convert_crop_type_name(name="whitebeans"),
            CropType.WhiteBeans)

    def test_winter_canola_hybrid(self):
        self.assertEqual(
            convert_crop_type_name(name="wintercanolahybrid"),
            CropType.WinterCanolaHybrid)

    def test_hard_red_winter_wheat_no_till(self):
        self.assertEqual(
            convert_crop_type_name(name="hardredwinterwheatnotillage"),
            CropType.HardRedWinterWheatNoTill)

    def test_n_fixing_forages(self):
        self.assertEqual(
            convert_crop_type_name(name="nfixingforages"),
            CropType.NFixingForages)

    def test_non_n_fixing_forages(self):
        self.assertEqual(
            convert_crop_type_name(name="nonnfixingforages"),
            CropType.NonNFixingForages)

    def test_not_selected(self):
        self.assertEqual(
            convert_crop_type_name(name="_"),
            CropType.NotSelected)

    def test_misc(self):
        for crop_name, crop_type in [
            ("Berries & grapes", CropType.BerriesAndGrapes),
            ("Red clover(Trifolium pratense L.)", CropType.RedCloverTrifoliumPratenseL),
            ("Berseem clover (Trifolium alexandrium L.)", CropType.BerseemCloverTrifoliumAlexandriumL),
            ("Sweet clover (Melilotus officinalis)", CropType.SweetCloverMelilotusOfficinalis),
            ("Crimson clover (Trifolium incarnatum)", CropType.CrimsonCloverTrifoliumIncarnatum),
            ("Hairy Vetch (Vicia villosa roth)", CropType.HairyVetchViciaVillosaRoth),
            ("Alfalfa (Medicago sativa L.)", CropType.AlfalfaMedicagoSativaL),
            ("Faba bean / broad bean (Vicia faba)", CropType.FabaBeanBroadBeanViciaFaba),
            ("Cowpea (Vigna unguiculata)", CropType.CowpeaVignaUnguiculata),
            ("Rapeseed (Brassica Napus L.)", CropType.RapeseedBrassicaNapusL),
            ('Winter turnip rape [Brassica Rapa spp. oleifera L. (cv. "Largo")]',
             CropType.WinterTurnipRapeBrassicaRapaSppOleiferaLCVLargo),
            ("Phacelia[Phacelia tanacetifolia (cv.'Phaci')]", CropType.PhaceliaPhaceliaTanacetifoliaCVPhaci),
            ("Forage radish (Raphanus sativus L.)", CropType.ForageRadishRaphanusSativusL),
            ("Mustard (Sinapus alba L.subsp.Mairei (H.Lindb.) Maire)",
             CropType.MustardSinapusAlbaLSubspMaireiHLindbMaire),
            ("Barley (Hordeum vulgare)", CropType.BarleyHordeumVulgare),
            ("Oat (Avena sativa)", CropType.OatAvenaSativa),
            ("Rye (Secale cereale) / Winter rye / Cereal rye", CropType.RyeSecaleCerealeWinterRyeCerealRye),
            ("Sesame (Sesamum indicum)", CropType.SesameSesamumIndicum),
            ("Flax (Linum usitatissimum)", CropType.FlaxLinumUsitatissimum),
            ("Ryegrass (Lolium Perenne L.)", CropType.RyeGrassLoliumPerenneL),
            ("Annual Ryegrass (Lolium multiflorum)", CropType.AnnualRyeGrassLoliumMultiflorum),
            ("Sorghum (Sorghum bicolour)", CropType.SorghumSorghumBicolour),
            ("Shepherd's purse", CropType.ShepherdsPurse),
            ("Winter wheat (Triticum aestivum)", CropType.WinterWheatTriticumAestivum),
            ("(Fall) Rye", CropType.FallRye),
            ("Rangeland (native)", CropType.RangelandNative),
            ("Grazed pasture (all perennial types)", CropType.NotSelected),
            ("Total tree fruits & nuts", CropType.TreeFruitAndNuts)
        ]:
            self.assertEqual(
                crop_type,
                convert_crop_type_name(name=crop_name))


class TestGetNitrogenFixation(unittest.TestCase):
    def test_returns_expected_value_for_leguminous_crops(self):
        for crop_type in CropTypePerCategory.pulse_crop:
            self.assertEqual(
                0.7,
                get_nitrogen_fixation(crop_type=crop_type))

    def test_returns_expected_value_for_non_leguminous_crops(self):
        for crop_type in CropType:
            if crop_type not in CropTypePerCategory.pulse_crop:
                self.assertEqual(
                    0,
                    get_nitrogen_fixation(crop_type=crop_type))


if __name__ == '__main__':
    unittest.main()
