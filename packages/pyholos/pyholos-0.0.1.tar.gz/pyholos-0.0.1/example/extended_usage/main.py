from datetime import datetime, timedelta
from pathlib import Path

from pandas import DataFrame, read_csv

from example.extended_usage.beef_inputs import set_beef_data
from example.extended_usage.dairy_inputs import set_dairy_data
from example.extended_usage.field_inputs import set_field_data
from example.extended_usage.sheep_inputs import set_sheep_data
from pyholos.farm.farm import create_farm
from pyholos.farm.farm_inputs import WeatherData, WeatherSummary


def get_weather_data(df: DataFrame) -> WeatherData:
    return WeatherData(
        year=df.loc[0, "year"],
        precipitation=df['precipitation'],
        potential_evapotranspiration=df['potential_evapotranspiration'],
        temperature=df['air_temperature'])


def get_weather_summary(df: DataFrame) -> WeatherSummary:
    year = df.loc[0, 'year']
    date_base = datetime(year - 1, 12, 31)
    df['date'] = df['day_of_year'].apply(lambda x: date_base + timedelta(x))
    gdf = df.groupby(df['date'].dt.month)
    precipitation = gdf['precipitation'].sum()
    etp = gdf['potential_evapotranspiration'].sum()
    return WeatherSummary(
        year=2024,
        mean_annual_precipitation=542,
        mean_annual_temperature=3.57,
        mean_annual_evapotranspiration=626,
        growing_season_precipitation=precipitation[(precipitation.index > 4) & (precipitation.index < 12)].sum(),
        growing_season_evapotranspiration=etp[(etp.index > 4) & (etp.index < 12)].sum(),
        monthly_precipitation=precipitation.tolist(),
        monthly_potential_evapotranspiration=etp.tolist(),
        monthly_temperature=gdf['air_temperature'].mean().to_list())


if __name__ == '__main__':
    path_root = Path(__file__).parent
    weather_df = read_csv('weather_data.csv', sep=',', decimal='.', comment='#')
    weather_summary = get_weather_summary(weather_df)
    farm = create_farm(
        latitude=49.98,
        longitude=-98.04,
        weather_summary=get_weather_summary(df=weather_df),
        beef_cattle_data=set_beef_data(weather_summary=weather_summary),
        dairy_cattle_data=set_dairy_data(weather_summary=weather_summary),
        sheep_flock_data=set_sheep_data(weather_summary=weather_summary),
        fields_data=set_field_data(weather_data=get_weather_data(df=weather_df))
    )

    farm.write_files(path_dir_farm=path_root / 'farm_data/example_farm')
