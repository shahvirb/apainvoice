import pathlib
import yaml


def get_config_path():
    return pathlib.Path(__file__).parent / "log_conf.yaml"


def get_config_dict():
    with open(get_config_path(), "r") as stream:
        return yaml.load(stream, Loader=yaml.FullLoader)
