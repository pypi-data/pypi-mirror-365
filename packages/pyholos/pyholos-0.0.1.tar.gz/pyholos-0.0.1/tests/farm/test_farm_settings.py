import unittest
from pathlib import Path

from pyholos.farm import farm_settings


class TestFarmSettingsVar(unittest.TestCase):
    def test_farm_settings_variable_works_accepts_any_type_for_values(self):
        for v in (1, 1.0, 'str', Path):
            self.assertEqual(v, farm_settings.FarmSettingsVar(name='test_variable', value=v).value)


class TestParamGeneric(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.param_generic = farm_settings.ParamGeneric(title='test')

    def test_param_generic_has_expected_title(self):
        self.assertEqual('# test', self.param_generic.title)

    def test_param_generic_method_returns_expected_list(self):
        self.assertEqual(['# test'], self.param_generic.to_list())


class TestParamsFarmSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params_farm_settings = farm_settings.ParamsFarmSettings(
            year=1,
            latitude=50,
            longitude=-98,
            monthly_precipitation=list(range(12)),
            monthly_potential_evapotranspiration=list(range(10, 22)),
            monthly_temperature=list(range(-5, 7)),
            run_in_period_years=15)
        cls.path_farm_settings = Path(__file__).parents[1] / 'sources/Farm.settings'

    @classmethod
    def tearDownClass(cls):
        if cls.path_farm_settings.exists():
            cls.path_farm_settings.unlink()

    def test_params_farm_settings_output_is_written_to_file(self):
        self.params_farm_settings.write(self.path_farm_settings.parent)
        self.assertTrue(self.path_farm_settings.exists())

        expected_output = [
            '# General',
            'Yield Assignment Method = SmallAreaData',
            'Polygon Number = 851003',
            'Latitude = 50',
            'Longitude = -98',
            'Carbon Concentration  (kg kg^-1) = 0.45',
            'Emergence Day = 141',
            'Ripening Day = 197',
            'Variance = 300',
            'Alfa = 0.7',
            'Decomposition Minimum Temperature  (°C) = -3.78',
            'Decomposition Maximum Temperature  (°C)  = 30',
            'Moisture Response Function At Saturation = 0.42',
            'Moisture Response Function At Wilting Point = 0.18',
            '',
            '# Annual Crops',
            'Percentage Of Product Returned To Soil For Annuals = 2',
            'Percentage Of Straw Returned To Soil For Annuals = 100',
            'Percentage Of Roots Returned To Soil For Annuals = 100',
            '',
            '# Silage Crops',
            'Percentage Of Product Yield Returned To Soil For Silage Crops = 35',
            'Percentage Of Roots Returned To Soil For Silage Crops = 100',
            '',
            '# Cover Crops',
            'Percentage Of Product Yield Returned To Soil For Cover Crops = 100',
            'Percentage Of Product Yield Returned To Soil For Cover Crops Forage = 35',
            'Percentage Of Product Yield Returned To Soil For Cover Crops Produce = 0',
            'Percentage Of Straw Returned To Soil For Cover Crops = 100',
            'Percentage Of Roots Returned To Soil For Cover Crops = 100',
            '',
            '# Root Crops',
            'Percentage Of Product Returned To Soil For Root Crops = 0',
            'Percentage Of Straw Returned To Soil For Root Crops = 100',
            '',
            '# Perennial Crops',
            'Percentage Of Product Returned To Soil For Perennials = 35',
            'Percentage Of Roots Returned To Soil For Perennials = 100',
            '',
            '# Rangeland',
            'Percentage Of Product Returned To Soil For Rangeland Due To Harvest Loss = 35',
            'Percentage Of Roots Returned To Soil For Rangeland = 100',
            '',
            '# Fodder Corn',
            'Percentage Of Product Returned To Soil For Fodder Corn = 35',
            'Percentage Of Roots Returned To Soil For Fodder Corn = 100',
            'Decomposition Rate Constant Young Pool = 0.8',
            'Decomposition Rate Constant Old Pool = 0.00605',
            'Old Pool Carbon N = 0.1',
            'NO Ratio = 0.1',
            'Emission Factor For Leaching And Runoff  (kg N2O-N (kg N)^-1) = 0.011',
            'Emission Factor For Volatilization  (kg N2O-N (kg N)^-1) = 0.01',
            'Fraction Of N Lost By Volatilization = 0.21',
            'Microbe Death = 0.2',
            'Denitrification = 0.5',
            'Carbon modelling strategy = ICBM',
            'Run In Period Years = 15',
            '',
            '# ICBM/Climate',
            'Humification Coefficient Above Ground = 0.125',
            'Humification Coefficient Below Ground = 0.3',
            'Humification Coefficient Manure = 0.31',
            'Climate filename = climate.csv',
            'Climate Data Acquisition = NASA',
            'Use climate parameter instead of management factor = True',
            'Enable Carbon Modelling = True',
            '',
            '# Precipitation Data (mm)',
            'January Precipitation = 0',
            'February Precipitation = 1',
            'March Precipitation = 2',
            'April Precipitation = 3',
            'May Precipitation = 4',
            'June Precipitation = 5',
            'July Precipitation = 6',
            'August Precipitation = 7',
            'September Precipitation = 8',
            'October Precipitation = 9',
            'November Precipitation = 10',
            'December Precipitation = 11',
            '',
            '# Evapotranspiration Data (mm year^-1)',
            'January Potential Evapotranspiration = 10',
            'February Potential Evapotranspiration = 11',
            'March Potential Evapotranspiration = 12',
            'April Potential Evapotranspiration = 13',
            'May Potential Evapotranspiration = 14',
            'June Potential Evapotranspiration = 15',
            'July Potential Evapotranspiration = 16',
            'August Potential Evapotranspiration = 17',
            'September Potential Evapotranspiration = 18',
            'October Potential Evapotranspiration = 19',
            'November Potential Evapotranspiration = 20',
            'December Potential Evapotranspiration = 21',
            '',
            '# Temperature Data (°C)',
            'January Mean Temperature = -5',
            'February Mean Temperature = -4',
            'March Mean Temperature = -3',
            'April Mean Temperature = -2',
            'May Mean Temperature = -1',
            'June Mean Temperature = 0',
            'July Mean Temperature = 1',
            'August Mean Temperature = 2',
            'September Mean Temperature = 3',
            'October Mean Temperature = 4',
            'November Mean Temperature = 5',
            'December Mean Temperature = 6',
            '',
            '# Soil Data',
            'Province = Manitoba',
            'Year Of Observation = 1',
            'Ecodistrict ID = 851',
            'Soil Great Group = Regosol',
            'Soil functional category = Black',
            'Bulk Density = 1.2',
            'Soil Texture = Fine',
            'Soil Ph = 7.8',
            'Top Layer Thickness  (mm) = 200',
            'Proportion Of Sand In Soil = 0.2',
            'Proportion Of Clay In Soil = 0.3',
            'Proportion Of Soil Organic Carbon = 3.1'
        ]
        with self.path_farm_settings.open(mode='r', encoding='utf-8') as f:
            output = f.readlines()
        self.assertEqual(expected_output, [s.replace('\n', '') for s in output])
        pass


if __name__ == '__main__':
    unittest.main()
