import unittest
from itertools import product
from json import load
from pathlib import Path
from random import randint, random

from pyholos.components.land_management.carbon import climate
from pyholos.defaults import Defaults
from pyholos.utils import read_holos_resource_table
from tests.helpers.utils import assert_is_ascending, assert_is_descending


class TestCalculateGreenAreaIndexMax(unittest.TestCase):
    def test_calculate_green_area_index_max_returns_zero_for_zero_yield(self):
        self.assertEqual(
            0,
            climate.calculate_green_area_index_max(crop_yield=0))

    def test_calculate_green_area_index_max_returns_expected_value_for_1000_kg_yield(self):
        self.assertEqual(
            0.0731 + 0.408,
            climate.calculate_green_area_index_max(crop_yield=1000))


class TestCalculateMidSeason(unittest.TestCase):
    def test_calculate_mid_season_returns_expected_results(self):
        for emergence_day, ripening_day in [
            (0, 100),
            (50, 150),
            (50, 50)
        ]:
            self.assertEqual(
                (emergence_day + ripening_day) / 2.,
                climate.calculate_mid_season(
                    emergence_day=emergence_day,
                    ripening_day=ripening_day))


class TestCalculateGreenAreaIndex(unittest.TestCase):
    def test_calculate_green_area_index_returns_green_area_index_max_at_mid_season(self):
        gai_max = 1
        self.assertEqual(
            gai_max,
            climate.calculate_green_area_index(
                green_area_index_max=gai_max,
                julian_day=100,
                mid_season=100,
                variance=1))

    def test_calculate_green_area_index_returns_increasing_values_towards_mid_season(self):
        mid_season = 100
        gai = [climate.calculate_green_area_index(
            green_area_index_max=1,
            julian_day=v,
            mid_season=mid_season,
            variance=1)
            for v in range(mid_season)
        ]

        assert_is_ascending(gai)

    def test_calculate_green_area_index_returns_decreasing_values_after_mid_season(self):
        mid_season = 100
        gai = [climate.calculate_green_area_index(
            green_area_index_max=1,
            julian_day=v,
            mid_season=mid_season,
            variance=1)
            for v in range(mid_season, mid_season + 100)
        ]

        assert_is_descending(gai)


class TestCalculateOrganicCarbonFactor(unittest.TestCase):
    def test_calculate_organic_carbon_factor_returns_expected_value_for_no_organic_carbon_in_soil(self):
        self.assertEqual(
            -0.837531,
            climate.calculate_organic_carbon_factor(percent_organic_carbon=0))

    def test_calculate_organic_carbon_factor_returns_zero_for_a_specific_value_of_organic_carbon_in_soil(self):
        self.assertEqual(
            0,
            climate.calculate_organic_carbon_factor(percent_organic_carbon=0.837531 / 0.430183))

    def test_calculate_organic_carbon_factor_returns_increasing_values_with_organic_carbon_in_soil(self):
        assert_is_ascending([climate.calculate_organic_carbon_factor(percent_organic_carbon=v)
                             for v in range(20)])


class TestCalculateClayFactor(unittest.TestCase):
    def test_calculate_clay_factor_returns_expected_value_for_zero_clay_content(self):
        self.assertEqual(
            -1.40744,
            climate.calculate_clay_factor(clay_content=0))

    def test_calculate_clay_factor_returns_zero_at_specific_value_of_clay_content(self):
        self.assertEqual(
            0,
            climate.calculate_clay_factor(clay_content=1.40744 / (0.0661969 * 100)))

    def test_calculate_clay_factor_returns_increasing_values_with_clay_content(self):
        assert_is_ascending([climate.calculate_clay_factor(clay_content=v) for v in range(100)])


class TestCalculateSandFactor(unittest.TestCase):
    def test_calculate_sand_factor_returns_expected_value_for_zero_sand_content(self):
        self.assertEqual(
            -1.51866,
            climate.calculate_sand_factor(sand_content=0))

    def test_calculate_sand_factor_returns_zero_at_specific_value_of_sand_content(self):
        self.assertEqual(
            0,
            climate.calculate_sand_factor(sand_content=1.51866 / (0.0393284 * 100)))

    def test_calculate_sand_factor_returns_increasing_values_with_sand_content(self):
        assert_is_ascending([climate.calculate_sand_factor(sand_content=v) for v in range(100)])


class TestCalculateWiltingPoint(unittest.TestCase):
    def test_basal_value_of_volumetric_water_content_at_wilting_point_for_all_zero_inputs(self):
        self.assertAlmostEqual(
            (14.2568 + 7.36318 * 0.06865) / 100.,
            climate.calculate_wilting_point(
                organic_carbon_factor=0,
                clay_factor=0,
                sand_factor=0),
            places=3)

    def test_volumetric_water_content_at_wilting_point_decreases_with_organic_carbon(self):
        assert_is_ascending([climate.calculate_wilting_point(
            organic_carbon_factor=v,
            clay_factor=1,
            sand_factor=1)
            for v in range(20)
        ])

    def test_volumetric_water_content_at_wilting_point_increases_with_sand(self):
        assert_is_ascending([climate.calculate_wilting_point(
            organic_carbon_factor=1,
            clay_factor=1,
            sand_factor=v)
            for v in range(20)
        ])

    def test_volumetric_water_content_at_wilting_point_decreases_with_clay(self):
        assert_is_ascending([climate.calculate_wilting_point(
            organic_carbon_factor=1,
            clay_factor=v,
            sand_factor=1)
            for v in range(20)
        ])


class TestCalculateFieldCapacity(unittest.TestCase):
    def test_basal_value_of_volumetric_water_content_at_field_capacity_for_all_zero_inputs(self):
        self.assertAlmostEqual(
            (29.7528 + 10.3544 * 0.0461615) / 100,
            climate.calculate_field_capacity(
                organic_carbon_factor=0,
                clay_factor=0,
                sand_factor=0),
            places=3)

    def test_volumetric_water_content_at_field_capacity_decreases_with_organic_carbon(self):
        assert_is_ascending([climate.calculate_field_capacity(
            organic_carbon_factor=v,
            clay_factor=1,
            sand_factor=1)
            for v in range(20)
        ])

    def test_volumetric_water_content_at_field_capacity_increases_with_sand(self):
        assert_is_ascending([climate.calculate_field_capacity(
            organic_carbon_factor=1,
            clay_factor=1,
            sand_factor=v)
            for v in range(20)
        ])

    def test_volumetric_water_content_at_field_capacity_decreases_with_clay(self):
        assert_is_ascending([climate.calculate_field_capacity(
            organic_carbon_factor=1,
            clay_factor=v,
            sand_factor=1)
            for v in range(20)
        ])


class TestCalculateSoilMeanDepth(unittest.TestCase):
    def test_constant_value(self):
        self.assertEqual(
            12.5,
            climate.calculate_soil_mean_depth(layer_thickness=250))


class TestCalculateLeafAreaIndex(unittest.TestCase):
    def test_values_are_asa_expected(self):
        for gai in range(10):
            self.assertEqual(
                0.8 * gai,
                climate.calculate_leaf_area_index(green_area_index=gai))


class TestCalculateSurfaceTemperature(unittest.TestCase):
    def test_soil_surface_temperature_for_zero_daily_average_air_temperature(self):
        self.assertEqual(
            0,
            climate.calculate_surface_temperature(temperature=0, leaf_area_index=1))

    def test_soil_surface_temperature_for_negative_daily_average_air_temperature(self):
        for t in range(-20, 0):
            self.assertEqual(
                0.2 * t,
                climate.calculate_surface_temperature(temperature=t, leaf_area_index=1))

    def test_soil_surface_temperature_for_positive_daily_average_air_temperature_and_covering_leaf_area_index(self):
        for t in range(0, 20):
            self.assertEqual(
                t,
                climate.calculate_surface_temperature(temperature=t, leaf_area_index=3))

    def test_soil_surface_temperature_decreases_from_air_temperature_as_leaf_area_index_increases_over_covering_point(
            self):
        for t in range(0, 20):
            assert_is_ascending([climate.calculate_surface_temperature(temperature=t, leaf_area_index=lai) - t
                                 for lai in range(3, 7)])


class TestCalculateSoilTemperatures(unittest.TestCase):
    def test_value_at_first_day_of_year(self):
        self.assertEqual(
            0,
            climate.calculate_soil_temperatures(
                julian_day=1,
                soil_mean_depth=random(),
                green_area_index=random(),
                surface_temperature=random(),
                soil_temperature_previous=random()))

    def test_value_for_equal_temperature_values_of_two_consecutive_days(self):
        t = 20
        self.assertEqual(
            t,
            climate.calculate_soil_temperatures(
                julian_day=randint(2, 365),
                soil_mean_depth=random(),
                green_area_index=random(),
                surface_temperature=t,
                soil_temperature_previous=t))

    def test_values_increase_with_increasing_temperature_gap_between_two_consecutive_days(self):
        assert_is_ascending([
            climate.calculate_soil_temperatures(
                julian_day=randint(2, 365),
                soil_mean_depth=12.5,
                green_area_index=3,
                surface_temperature=delta_t,
                soil_temperature_previous=0)
            for delta_t in range(25)
        ])

    def test_values_decreases_with_increasing_soil_depth(self):
        assert_is_ascending([
            climate.calculate_soil_temperatures(
                julian_day=randint(2, 365),
                soil_mean_depth=d,
                green_area_index=3,
                surface_temperature=1,
                soil_temperature_previous=0)
            for d in range(50)
        ])

    def test_values_decreases_with_increasing_green_area_index(self):
        assert_is_ascending([
            climate.calculate_soil_temperatures(
                julian_day=randint(2, 365),
                soil_mean_depth=12.5,
                green_area_index=gai,
                surface_temperature=1,
                soil_temperature_previous=0)
            for gai in range(10)
        ])


class TestCalculateCropCoefficient(unittest.TestCase):
    def test_value_for_no_green_area_index(self):
        self.assertEqual(
            0.8,
            climate.calculate_crop_coefficient(green_area_index=0))

    def test_values_increase_with_green_area_index(self):
        assert_is_ascending([
            climate.calculate_crop_coefficient(green_area_index=gai)
            for gai in range(10)])


class TestCalculateCropEvapotranspiration(unittest.TestCase):
    def test_value_at_unity(self):
        self.assertEqual(
            1,
            climate.calculate_crop_evapotranspiration(
                evapotranspiration=1,
                crop_coefficient=1))

    def test_values_increase_with_crop_coefficient(self):
        assert_is_ascending([
            climate.calculate_crop_evapotranspiration(
                evapotranspiration=1,
                crop_coefficient=kc)
            for kc in range(2)
        ])


class TestCalculateCropInterception(unittest.TestCase):
    def test_values_for_weak_precipitation_compared_to_interception_capacity(self):
        gai = 10
        for p in range(int(0.2 * gai)):
            self.assertEqual(
                p,
                climate.calculate_crop_interception(
                    total_daily_precipitation=p,
                    green_area_index=gai,
                    crop_evapotranspiration=p))

    def test_values_for_strong_precipitation_compared_to_interception_capacity(self):
        gai = 1
        for p in range(1, 100):
            self.assertEqual(
                0.2 * gai,
                climate.calculate_crop_interception(
                    total_daily_precipitation=p,
                    green_area_index=gai,
                    crop_evapotranspiration=p))

    def test_values_for_strong_precipitation_compared_to_interception_capacity_and_evapotranspiration_rate(self):
        gai = 10
        for p in range(5, 100):
            self.assertEqual(
                0.2 * gai,
                climate.calculate_crop_interception(
                    total_daily_precipitation=p,
                    green_area_index=gai,
                    crop_evapotranspiration=2))


class TestCalculateSoilAvailableWater(unittest.TestCase):
    def test_values_are_as_expected(self):
        total_precipitation = 20
        for crop_interception in range(total_precipitation):
            self.assertEqual(
                total_precipitation - crop_interception,
                climate.calculate_soil_available_water(
                    total_daily_precipitation=total_precipitation,
                    crop_interception=crop_interception))


class TestCalculateVolumetricSoilWaterContent(unittest.TestCase):
    def test_min_value(self):
        wilting_point = 1
        self.assertEqual(
            wilting_point,
            climate.calculate_volumetric_soil_water_content(
                water_storage_previous=0,
                layer_thickness=randint(1, 100),
                wilting_point=wilting_point))

    def test_values_increase_with_water_storage(self):
        assert_is_ascending([
            climate.calculate_volumetric_soil_water_content(
                water_storage_previous=v,
                layer_thickness=1,
                wilting_point=1)
            for v in range(50)])

    def test_values_decrease_with_sol_thickness(self):
        assert_is_ascending([
            climate.calculate_volumetric_soil_water_content(
                water_storage_previous=1,
                layer_thickness=v,
                wilting_point=1)
            for v in range(1, 50)])


class TestCalculateSoilCoefficient(unittest.TestCase):
    def test_values_for_low_volumetric_water_content_values(self):
        wilting_point = 0.05
        alfa = 0.7
        lower_threshold = alfa * wilting_point / 100
        self.assertEqual(
            0,
            climate.calculate_soil_coefficient(
                field_capacity=random(),
                volumetric_soil_water_content=random() * lower_threshold,
                wilting_point=wilting_point,
                alfa=alfa))

    def test_values_for_volumetric_water_content_value_at_field_capacity(self):
        field_capacity = random()
        self.assertEqual(
            1,
            climate.calculate_soil_coefficient(
                field_capacity=field_capacity,
                volumetric_soil_water_content=field_capacity,
                wilting_point=field_capacity ** 2,
                alfa=1))

    def test_values_increase_with_field_capacity(self):
        wilting_point = 0.01
        soil_water_content = wilting_point
        assert_is_ascending(
            [climate.calculate_soil_coefficient(
                field_capacity=v / 100.,
                volumetric_soil_water_content=soil_water_content,
                wilting_point=wilting_point,
                alfa=0.7)
                for v in range(int(wilting_point * 100), 101)])

    def test_values_increase_with_alfa(self):
        assert_is_ascending(
            [climate.calculate_soil_coefficient(
                field_capacity=0.5,
                volumetric_soil_water_content=0.45,
                wilting_point=0.01,
                alfa=v / 10.)
                for v in range(11)])

    def test_values_increase_with_volumetric_water_content(self):
        field_capacity = 0.5
        wilting_point = 0
        assert_is_ascending(
            [climate.calculate_soil_coefficient(
                field_capacity=field_capacity,
                volumetric_soil_water_content=v,
                wilting_point=wilting_point,
                alfa=0.7)
                for v in range(int(field_capacity * 10))])


class TestCalculateActualEvapotranspiration(unittest.TestCase):
    def test_values_are_as_expected(self):
        for soil_coefficient, crop_evapotranspiration in product(
                [v / 100. for v in range(0, 110, 10)],
                range(11)
        ):
            self.assertEqual(
                soil_coefficient * crop_evapotranspiration,
                climate.calculate_actual_evapotranspiration(
                    crop_potential_evapotranspiration=crop_evapotranspiration,
                    soil_coefficient=soil_coefficient))


class TestCalculateDeepPercolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field_capacity = 0.5
        cls.layer_thickness = 1000
        cls.soil_holding_capacity = cls.field_capacity * cls.layer_thickness

    def test_deep_percolation_does_not_occur_below_soil_holding_capacity(self):
        self.assertEqual(
            0,
            climate.calculate_deep_percolation(
                field_capacity=self.field_capacity,
                layer_thickness=self.layer_thickness,
                previous_water_storage=random() * self.soil_holding_capacity))

    def test_deep_percolation_does_occur_for_excess_water_beyond_soil_holding_capacity(self):
        water_storage = (1 + random()) * self.soil_holding_capacity
        self.assertEqual(
            water_storage - self.soil_holding_capacity,
            climate.calculate_deep_percolation(
                field_capacity=self.field_capacity,
                layer_thickness=self.layer_thickness,
                previous_water_storage=water_storage))


class test_calculate_julian_day_water_storage(unittest.TestCase):
    def test_soil_water_stores_all_available_water_in_dry_conditions(self):
        available_water = random()
        self.assertEqual(
            available_water,
            climate.calculate_julian_day_water_storage(
                deep_percolation=0,
                previous_water_storage=0,
                soil_available_water=available_water,
                actual_evapotranspiration=0))

    def test_soil_water_storage_equals_that_of_the_previous_day_minos_deep_percolation_under_high_interception_conditions(
            self):
        actual_evapotranspiration = random()
        soil_available_water = actual_evapotranspiration
        previous_water_storage = random()
        deep_percolation = random()
        self.assertAlmostEqual(
            previous_water_storage - deep_percolation,
            climate.calculate_julian_day_water_storage(
                deep_percolation=deep_percolation,
                previous_water_storage=previous_water_storage,
                soil_available_water=soil_available_water,
                actual_evapotranspiration=actual_evapotranspiration),
            places=3)


class TestCalculateTemperatureResponseFactor(unittest.TestCase):
    def test_value_below_temperature_threshold(self):
        self.assertEqual(
            0,
            climate.calculate_temperature_response_factor(
                soil_temperature_previous=randint(-10, -4),
                decomposition_minimum_temperature=random(),
                decomposition_maximum_temperature=random()))

    def test_value_at_minimum_cardinal_temperature(self):
        decomposition_minimum_temperature = randint(-3, 25)
        self.assertEqual(
            0,
            climate.calculate_temperature_response_factor(
                soil_temperature_previous=decomposition_minimum_temperature,
                decomposition_minimum_temperature=decomposition_minimum_temperature,
                decomposition_maximum_temperature=random()))

    def test_value_increases_with_soil_temperature(self):
        decomposition_minimum_temperature = -1
        decomposition_maximum_temperature = 15

        assert_is_ascending([climate.calculate_temperature_response_factor(
            soil_temperature_previous=v,
            decomposition_minimum_temperature=decomposition_minimum_temperature,
            decomposition_maximum_temperature=decomposition_maximum_temperature)
            for v in range(decomposition_minimum_temperature, decomposition_maximum_temperature + 1)
        ])


class TestCalculateMoistureResponseFactor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.args = dict(
            field_capacity=0.4,
            wilting_point=0.2,
            reference_saturation_point=0.42,
            reference_wilting_point=0.18)

    def test_value_at_saturation_moisture_content(self):
        self.assertAlmostEqual(
            self.args['reference_saturation_point'],
            climate.calculate_moisture_response_factor(
                volumetric_water_content=1.2 * self.args['field_capacity'],
                **self.args),
            places=3)

    def test_value_at_optimal_moisture_content(self):
        self.assertEqual(
            1,
            climate.calculate_moisture_response_factor(
                volumetric_water_content=0.9 * self.args['field_capacity'],
                **self.args))

    def test_value_at_wilting_point(self):
        self.assertEqual(
            self.args['reference_wilting_point'],
            climate.calculate_moisture_response_factor(
                volumetric_water_content=self.args['wilting_point'],
                **self.args))

    def test_values_increase_with_soil_water_content(self):
        assert_is_ascending([
            climate.calculate_moisture_response_factor(
                volumetric_water_content=v / 10,
                **self.args)
            for v in range(int(self.args['wilting_point'] * 10), int(self.args['field_capacity'] * 10) + 5)
        ])


class TestCalculateClimateFactor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adjustment_factor = 0.10516

    def test_values_are_as_expected(self):
        for temperature_factor, moisture_factor, expected_value in [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 0),
            (1, self.adjustment_factor, 1),
            (self.adjustment_factor, 1, 1)
        ]:
            self.assertEqual(
                expected_value,
                climate.calculate_climate_factor(
                    moisture_response_factor=moisture_factor,
                    temperature_response_factor=temperature_factor))


class TestNonRegressionCalculateDailyClimateParameter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (Path(__file__).parents[3] / r'sources/holos/non_regression_climate_calculator.json').open(mode='r') as f:
            cls.non_regression_data = load(f)['calculate_daily_climate_parameter']

    def test_values(self):
        res = climate.calculate_daily_climate_parameter(**self.non_regression_data['inputs']).__dict__
        for k, v in self.non_regression_data['outputs'].items():
            self.assertAlmostEqual(
                v,
                res[k],
                places=2)


class TestNonRegressionCalculateDailyClimateParameters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (Path(__file__).parents[3] / r'sources/holos/non_regression_climate_calculator.json').open(mode='r') as f:
            cls.non_regression_data = load(f)['calculate_daily_climate_parameters']

    def test_values(self):
        """
        Notes:
            This test did not include a day-to-day comparison since input data taken from Holos
            (evapotranspirations, temperatures, precipitations) were rounded to 2-decimals, which makes the outputs
            of this function not identical to those from Holos.
        """
        func_inputs = self.non_regression_data['inputs']
        res = climate.calculate_daily_climate_parameters(**func_inputs)
        values_holos = self.non_regression_data['outputs']
        self.assertEqual(
            len(values_holos),
            len(res))

        self.assertLessEqual(
            sum([abs(v_res - v_holos) for v_res, v_holos in zip(res, values_holos)]) / len(res),
            0.02)

        self.assertAlmostEqual(
            sum(values_holos) / len(values_holos),
            sum(res) / len(res),
            places=2)

        self.assertAlmostEqual(
            climate.calculate_climate_parameter(**func_inputs),
            sum(res) / len(res),
            places=2)


class TestNonRegressionCalculateClimateParameter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weather_data = read_holos_resource_table(
            Path(__file__).parents[3] / r'sources/holos/daily_weather_data_example.csv',
            usecols=['Year', 'Mean Daily Air Temperature', 'Mean Daily Precipitation', 'Mean Daily Pet'])

    def test_values_of_monoculture_field_of_annual_crop(self):
        # Values reported for the climate parameter were exported from the GUI for a wheat field
        for year, crop_yield, expected_value in [
            (1985, 3490, 1.208),
            (1986, 3100, 1.17),
            (1987, 2800, 1.332),
            (1988, 2600, 1.282),
            (1989, 3100, 1.284),
            (1990, 3100, 1.344),
            (1991, 2900, 1.356),
            (1992, 3300, 1.149),
            (1993, 3000, 1.319),
            (1994, 2500, 1.467),
            (1995, 2800, 1.413),
            (1996, 2800, 1.366),
            (1997, 3100, 1.307),
            (1998, 2900, 1.569),
            (1999, 3000, 1.5),
            (2000, 3300, 1.26),
            (2001, 3200, 1.413),
            (2002, 3300, 1.367),
            (2003, 3100, 1.378),
            (2004, 3300, 1.356),
            (2005, 2900, 1.495),
            (2006, 2900, 1.442),
            (2007, 2800, 1.405),
            (2008, 2200, 1.374),
            (2009, 2500, 1.293),
            (2010, 2900, 1.518),
            (2011, 2800, 1.519),
            (2012, 3100, 1.448),
            (2013, 3300, 1.433),
            (2014, 3400, 1.381),
            (2015, 3500, 1.497),
            (2016, 3400, 1.463),
            (2017, 3020, 1.449),
            (2018, 3210, 1.442),
            (2019, 3030, 1.372),
            (2020, 3030, 1.364),
            (2021, 3030, 1.478),
            (2022, 3030, 1.574),
            (2023, 3030, 1.584),
            (2024, 3030, 1.741),
        ]:
            df = self.weather_data[self.weather_data['Year'] == year]
            res = climate.calculate_climate_parameter(
                emergence_day=Defaults.EmergenceDay,
                ripening_day=Defaults.RipeningDay,
                crop_yield=crop_yield,
                clay=0.26,
                sand=0.28,
                percentage_soil_organic_carbon=3.2,
                layer_thickness_in_millimeters=230,
                variance=Defaults.Variance,
                alfa=0.7,
                decomposition_minimum_temperature=-3.78,
                decomposition_maximum_temperature=30,
                moisture_response_function_at_wilting_point=0.18,
                moisture_response_function_at_saturation=0.42,
                evapotranspirations=df['Mean Daily Pet'],
                precipitations=df['Mean Daily Precipitation'],
                temperatures=df['Mean Daily Air Temperature'])

            self.assertAlmostEqual(
                expected_value,
                res,
                places=3
            )

    def test_values_of_a_crop_rotation_without_cover_crops(self):
        # Values reported for the climate parameter were exported from the GUI for a field with a
        # soybean/wheat/grain corn rotation
        for year, crop_yield, expected_value in [
            (1985, 2500, 1.226),
            (1986, 3100, 1.17),
            (1987, 6734, 1.245),
            (1988, 1900, 1.3),
            (1989, 3100, 1.284),
            (1990, 6911, 1.261),
            (1991, 2600, 1.365),
            (1992, 3300, 1.149),
            (1993, 5973, 1.222),
            (1994, 2829, 1.461),
            (1995, 2800, 1.413),
            (1996, 7039, 1.255),
            (1997, 2632, 1.326),
            (1998, 2900, 1.569),
            (1999, 7939, 1.353),
            (2000, 2094, 1.277),
            (2001, 3200, 1.413),
            (2002, 7225, 1.241),
            (2003, 2647, 1.393),
            (2004, 3300, 1.356),
            (2005, 7403, 1.335),
            (2006, 3301, 1.43),
            (2007, 2800, 1.405),
            (2008, 7194, 1.264),
            (2009, 2101, 1.301),
            (2010, 2900, 1.518),
            (2011, 7332, 1.399),
            (2012, 3172, 1.445),
            (2013, 3300, 1.433),
            (2014, 8660, 1.225),
            (2015, 3137, 1.506),
            (2016, 3400, 1.463),
            (2017, 8730, 1.326),
            (2018, 2880, 1.456),
            (2019, 3030, 1.372),
            (2020, 8628.3, 1.147),
            (2021, 2877.8, 1.483),
            (2022, 3030, 1.574),
            (2023, 8628.3, 1.41),
            (2024, 2877.8, 1.747),
        ]:
            df = self.weather_data[self.weather_data['Year'] == year]
            res = climate.calculate_climate_parameter(
                emergence_day=Defaults.EmergenceDay,
                ripening_day=Defaults.RipeningDay,
                crop_yield=crop_yield,
                clay=0.26,
                sand=0.28,
                percentage_soil_organic_carbon=3.2,
                layer_thickness_in_millimeters=230,
                variance=Defaults.Variance,
                alfa=0.7,
                decomposition_minimum_temperature=-3.78,
                decomposition_maximum_temperature=30,
                moisture_response_function_at_wilting_point=0.18,
                moisture_response_function_at_saturation=0.42,
                evapotranspirations=df['Mean Daily Pet'],
                precipitations=df['Mean Daily Precipitation'],
                temperatures=df['Mean Daily Air Temperature'])

            self.assertAlmostEqual(
                expected_value,
                res,
                places=3)


if __name__ == '__main__':
    unittest.main()
