from pyholos.components.land_management.crop import CropType


def assert_is_ascending(values: list | tuple) -> bool:
    """Asserts that a vector of numeric values follows an ascending trend

    Args:
        values: values whose trend is to be checked
    """
    return all([x <= y for x, y in zip(values, values[1:])])


def assert_is_descending(values: list | tuple) -> bool:
    """Asserts that a vector of numeric values follows a descending trend

    Args:
        values: values whose trend is to be checked
    """
    return all([x >= y for x, y in zip(values, values[1:])])


class CropTypePerCategory:
    perennial = [
        CropType.Forage,
        CropType.TameGrass,
        CropType.TameLegume,
        CropType.TameMixed,
        CropType.PerennialForages,
        CropType.ForageForSeed,
        CropType.SeededGrassland,
        CropType.RangelandNative
    ]
    grassland = [
        CropType.BrokenGrassland,
        CropType.GrasslandSeeded,
        CropType.RangelandNative
    ]
    cover_crop = [
        CropType.RedCloverTrifoliumPratenseL,
        CropType.BerseemCloverTrifoliumAlexandriumL,
        CropType.SweetCloverMelilotusOfficinalis,
        CropType.CrimsonCloverTrifoliumIncarnatum,
        CropType.HairyVetchViciaVillosaRoth,
        CropType.AlfalfaMedicagoSativaL,
        CropType.FabaBeanBroadBeanViciaFaba,
        CropType.CowpeaVignaUnguiculata,
        CropType.AustrianWinterPea,
        CropType.RapeseedBrassicaNapusL,
        CropType.WinterTurnipRapeBrassicaRapaSppOleiferaLCVLargo,
        CropType.PhaceliaPhaceliaTanacetifoliaCVPhaci,
        CropType.ForageRadishRaphanusSativusL,
        CropType.MustardSinapusAlbaLSubspMaireiHLindbMaire,
        CropType.BarleyHordeumVulgare,
        CropType.OatAvenaSativa,
        CropType.RyeSecaleCerealeWinterRyeCerealRye,
        CropType.SesameSesamumIndicum,
        CropType.FlaxLinumUsitatissimum,
        CropType.RyeGrassLoliumPerenneL,
        CropType.AnnualRyeGrassLoliumMultiflorum,
        CropType.SorghumSorghumBicolour,
        CropType.PigeonBean,
        CropType.ShepherdsPurse,
        CropType.WinterWheatTriticumAestivum
    ]
    leguminous_cover_crop = [
        CropType.RedCloverTrifoliumPratenseL,
        CropType.BerseemCloverTrifoliumAlexandriumL,
        CropType.SweetCloverMelilotusOfficinalis,
        CropType.CrimsonCloverTrifoliumIncarnatum,
        CropType.HairyVetch,
        CropType.AlfalfaMedicagoSativaL,
        CropType.FabaBeanBroadBeanViciaFaba,
        CropType.CowpeaVignaUnguiculata,
        CropType.AustrianWinterPea,
        CropType.PigeonBean
    ]
    non_leguminous_cover_crop = [
        CropType.WinterWeeds,
        CropType.RapeseedBrassicaNapusL,
        CropType.WinterTurnipRapeBrassicaRapaSppOleiferaLCVLargo,
        CropType.PhaceliaPhaceliaTanacetifoliaCVPhaci,
        CropType.ForageRadishRaphanusSativusL,
        CropType.MustardSinapusAlbaLSubspMaireiHLindbMaire,
        CropType.BarleyHordeumVulgare,
        CropType.OatAvenaSativa,
        CropType.RyeSecaleCerealeWinterRyeCerealRye,
        CropType.SesameSesamumIndicum,
        CropType.FlaxLinumUsitatissimum,
        CropType.RyeGrassLoliumPerenneL,
        CropType.AnnualRyeGrassLoliumMultiflorum,
        CropType.SorghumSorghumBicolour,
        CropType.WinterWheatTriticumAestivum,
        CropType.FallRye
    ]
    native_grassland = CropType.RangelandNative
    fallow = [
        CropType.Fallow,
        CropType.SummerFallow
    ]
    annual = [
        CropType.SmallGrainCereals,
        CropType.Wheat,
        CropType.WheatSilage,
        CropType.Barley,
        CropType.BarleySilage,
        CropType.UndersownBarley,
        CropType.Oats,
        CropType.OatSilage,
        CropType.Camelina,
        CropType.Triticale,
        CropType.TriticaleSilage,
        CropType.Sorghum,
        CropType.CanarySeed,
        CropType.Buckwheat,
        CropType.FallRye,
        CropType.MixedGrains,
        CropType.Oilseeds,
        CropType.Canola,
        CropType.Mustard,
        CropType.Flax,
        CropType.PulseCrops,
        CropType.Soybeans,
        CropType.BeansDryField,
        CropType.Chickpeas,
        CropType.DryPeas,
        CropType.FieldPeas,
        CropType.Lentils,
        CropType.GrainCorn,
        CropType.SilageCorn,
        CropType.Safflower,
        CropType.SunflowerSeed,
        CropType.Tobacco,
        CropType.Vegetables,
        CropType.BerriesAndGrapes,
        CropType.OtherFieldCrops
    ]
    silage_crop = [
        CropType.SilageCorn,
        CropType.GrassSilage,
        CropType.BarleySilage,
        CropType.OatSilage,
        CropType.TriticaleSilage,
        CropType.WheatSilage
    ]
    silage_crop_without_defaults = [
        CropType.BarleySilage,
        CropType.OatSilage,
        CropType.SilageCorn,
        CropType.TriticaleSilage,
        CropType.GrassSilage,
        CropType.WheatSilage
    ]
    root_crops = [
        CropType.Potatoes,
        CropType.SugarBeets
    ]
    small_grains = [
        CropType.SmallGrainCereals,
        CropType.Wheat,
        CropType.WinterWheat,
        CropType.WheatSilage,
        CropType.Barley,
        CropType.GrainCorn,
        CropType.BarleySilage,
        CropType.UndersownBarley,
        CropType.Oats,
        CropType.OatSilage,
        CropType.Triticale,
        CropType.TriticaleSilage,
        CropType.Sorghum,
        CropType.CanarySeed,
        CropType.Buckwheat,
        CropType.FallRye,
        CropType.MixedGrains
    ]
    oil_seed = [
        CropType.Oilseeds,
        CropType.Canola,
        CropType.Camelina,
        CropType.Mustard,
        CropType.Soybeans,
        CropType.Flax
    ]
    other_field_crop = [
        CropType.Safflower,
        CropType.SunflowerSeed,
        CropType.Tobacco,
        CropType.Vegetables,
        CropType.BerriesAndGrapes,
        CropType.OtherFieldCrops
    ]
    pulse_crop = [
        CropType.PulseCrops,
        CropType.BeansDryField,
        CropType.Chickpeas,
        CropType.DryPeas,
        CropType.FieldPeas,
        CropType.Lentils
    ]
    national_inventory_report = [
        CropType.Barley,
        CropType.Buckwheat,
        CropType.Canola,
        CropType.SmallGrainCereals,
        CropType.Chickpeas,
        CropType.GrainCorn,
        CropType.SilageCorn,
        CropType.BeansDryField,
        CropType.FieldPeas,
        CropType.FabaBeans,
        CropType.FlaxSeed,
        CropType.Grains,
        CropType.Lentils,
        CropType.MustardSeed,
        CropType.MixedGrains,
        CropType.Oats,
        CropType.OtherDryFieldBeans,
        CropType.Oilseeds,
        CropType.Peas,
        CropType.Potatoes,
        CropType.Pulses,
        CropType.Rye,
        CropType.FallRye,
        CropType.SpringRye,
        CropType.Safflower,
        CropType.Soybeans,
        CropType.SugarBeets,
        CropType.SunflowerSeed,
        CropType.Triticale,
        CropType.WhiteBeans,
        CropType.Wheat,
        CropType.WheatRye,
        CropType.SpringWheat,
        CropType.WinterWheat,
        CropType.Durum,
        CropType.CanarySeed,
        CropType.Tobacco
    ]

    valid_crop_types = [
        CropType.Barley,
        CropType.BarleySilage,
        CropType.BeansDryField,
        CropType.BerriesAndGrapes,
        CropType.Buckwheat,
        CropType.CanarySeed,
        CropType.Canola,
        CropType.Chickpeas,
        CropType.Camelina,
        CropType.DryPeas,
        CropType.FallRye,
        CropType.Flax,
        CropType.ForageForSeed,
        CropType.GrainCorn,
        CropType.GrassSilage,
        CropType.TameGrass,
        CropType.TameLegume,
        CropType.TameMixed,
        CropType.Lentils,
        CropType.MixedGrains,
        CropType.Mustard,
        CropType.OatSilage,
        CropType.Oats,
        CropType.Oilseeds,
        CropType.RangelandNative,
        CropType.OtherFieldCrops,
        CropType.SeededGrassland,
        CropType.Potatoes,
        CropType.PulseCrops,
        CropType.Safflower,
        CropType.SilageCorn,
        CropType.SmallGrainCereals,
        CropType.Sorghum,
        CropType.Soybeans,
        CropType.SugarBeets,
        CropType.SummerFallow,
        CropType.SunflowerSeed,
        CropType.Tobacco,
        CropType.Triticale,
        CropType.TriticaleSilage,
        CropType.UndersownBarley,
        CropType.Vegetables,
        CropType.Wheat,
        CropType.WheatSilage
    ]
    valid_perennial_types = [
        CropType.ForageForSeed,
        CropType.TameGrass,
        CropType.TameLegume,
        CropType.TameMixed,
        CropType.RangelandNative,
        CropType.SeededGrassland
    ]
