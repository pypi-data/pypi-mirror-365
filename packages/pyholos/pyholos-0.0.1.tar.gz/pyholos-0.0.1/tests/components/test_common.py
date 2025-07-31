import unittest

from pyholos.components import common
from pyholos.common2 import CanadianProvince


class TestComponentType(unittest.TestCase):
    def test_to_str(self):
        for component_type in common.ComponentType:
            self.assertEqual(
                component_type.value,
                component_type.to_str().replace('Component', '')
            )


class TestCalculateFractionOfNitrogenLostByLeachingAndRunoff(unittest.TestCase):
    def test_value_when_precipitation_is_lower_than_evapotranspiration(self):
        self.assertEqual(
            0.13765,
            common.calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff(
                growing_season_precipitation=1,
                growing_season_evapotranspiration=2))

    def test_value_when_precipitation_is_higher_than_evapotranspiration(self):
        self.assertEqual(
            0.3,
            common.calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff(
                growing_season_precipitation=2,
                growing_season_evapotranspiration=1))

    def test_max_value(self):
        evapotranspiration = 1
        for precipitation_to_evapotranspiration_ratio in range(1, 11):
            self.assertEqual(
                0.3,
                common.calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff(
                    growing_season_precipitation=precipitation_to_evapotranspiration_ratio * evapotranspiration,
                    growing_season_evapotranspiration=evapotranspiration))

    def test_min_value(self):
        evapotranspiration = 1
        for evapotranspiration_to_precipitation_ratio in range(5, 11):
            self.assertEqual(
                0.05,
                common.calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff(
                    growing_season_precipitation=evapotranspiration / evapotranspiration_to_precipitation_ratio,
                    growing_season_evapotranspiration=evapotranspiration))


class TestConvertProvinceName(unittest.TestCase):
    def test_alberta(self):
        for v in ("alberta", "ab", "alta", "alb"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Alberta)

    def test_british_columbia(self):
        for v in ("britishcolumbia", "colombiebritannique", "bc", "cb"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.BritishColumbia)

    def test_saskatchewan(self):
        for v in "saskatchewan", "sk", "sask":
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Saskatchewan)

    def test_manitoba(self):
        for v in ("manitoba", "mb", "man"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Manitoba)

    def test_ontario(self):
        for v in ("ontario", "on", "ont"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Ontario)

    def test_quebec(self):
        for v in ("quebec", "québec", "qc", "que"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Quebec)

    def test_newbrunswick(self):
        for v in ("newbrunswick", "nouveaubrunswick", "nb"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.NewBrunswick)

    def test_novascotia(self):
        for v in ("novascotia", "nouvelleécosse", "nouvelleecosse", "ns", "né", "ne"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.NovaScotia)

    def test_princeedwardisland(self):
        for v in ("princeedwardisland", "îleduprinceédouard", "îleduprinceedouard", "ileduprinceédouard",
                  "ileduprinceedouard", "pe", "pei", "ipe", "ipé", "îpe", "îpé"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.PrinceEdwardIsland)

    def test_newfoundland(self):
        for v in ("newfoundlandandlabrador", "terreneuveetlabrador", "nl", "nf", "tnl", "nfld", "newfoundland"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.NewfoundlandAndLabrador)

    def test_yukon(self):
        for v in ("yukon", "yt", "yk", "yuk", "yn"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Yukon)

    def test_northwest_territories(self):
        for v in ("northwestterritories", "territoiresdunordouest", "nt", "tno"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.NorthwestTerritories)

    def test_nunavut(self):
        for v in ("nunavut", "nu", "nvt"):
            self.assertEqual(
                common.convert_province_name(name=v),
                CanadianProvince.Nunavut)

    def test_default(self):
        self.assertEqual(
            common.convert_province_name(name='soMe RanDom nAmE'),
            CanadianProvince.Alberta)


class TestCalcDefaultIrrigationAmount(unittest.TestCase):
    def test_values_for_water_deficit_conditions(self):
        precipitation = 500
        for water_deficit in range(1, 300, 10):
            self.assertEqual(
                water_deficit,
                common.calc_default_irrigation_amount(
                    precipitation=precipitation,
                    evapotranspiration=precipitation + water_deficit))

    def test_values_for_no_water_deficit_conditions(self):
        precipitation = 500
        for water_excess in range(1, 300, 10):
            self.assertEqual(
                0,
                common.calc_default_irrigation_amount(
                    precipitation=precipitation,
                    evapotranspiration=precipitation - water_excess))


if __name__ == '__main__':
    unittest.main()
