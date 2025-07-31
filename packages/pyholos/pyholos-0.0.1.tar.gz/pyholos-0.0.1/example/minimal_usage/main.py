from pathlib import Path
from shutil import rmtree

from pyholos import launching


class ExampleData:
    _path = Path(__file__).parent
    path_dir_farms = _path / 'farm_data'
    path_dir_outputs = _path / 'outputs'
    name_farm_json = 'farm.json'
    name_dir_farms_json = None
    name_settings = None
    id_slc_polygon = 851003
    timeout_secs = 60
    expected_output_folders = ['farm_from_json', 'HolosExampleFarm']

def clean_up(p: Path):
    for f in p.iterdir():
        if f.is_dir():
            if f != ExampleData.path_dir_farms:
                rmtree(f)
            else:
                clean_up(f)
        else:
            if f.name not in ("farm.json", Path(__file__).name):
                f.unlink()

def run_using_json_file():
    print('\n***')
    print('Running using a JSON input...')

    launching.launch_holos(
        path_dir_farms=ExampleData.path_dir_farms,
        name_farm_json=ExampleData.name_farm_json,
        name_dir_farms_json=ExampleData.name_dir_farms_json,
        name_settings=ExampleData.name_settings,
        path_dir_outputs=ExampleData.path_dir_outputs / 'from_json',
        id_slc_polygon=ExampleData.id_slc_polygon)


def run_using_existing_farm_data():
    print('***')
    print('Running using already parsed data from the JSON input...')

    # path_dir_outputs = ExampleData.path_dir_farms / 'outputs_from_already_parsed_data'
    launching.launch_holos(
        path_dir_farms=ExampleData.path_dir_farms,
        name_farm_json=None,
        name_dir_farms_json=None,
        name_settings=None,
        path_dir_outputs=ExampleData.path_dir_outputs / 'from_already_parsed_files',
        id_slc_polygon=None)



if __name__ == '__main__':
    clean_up(Path(__file__).parent)
    run_using_json_file()
    run_using_existing_farm_data()