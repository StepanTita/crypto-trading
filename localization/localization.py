import yaml


def get_localization(path):
    with open(path) as f:
        return yaml.full_load(f)
