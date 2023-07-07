import yaml


def get_config(path):
    with open(path) as f:
        return yaml.full_load(f)


if __name__ == 'main':
    print(get_config('../config.local.yaml'))
