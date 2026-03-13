from pathlib import Path

import yaml


def load_city_config(config_path: str = "config/cities.yml") -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if "supported_cities" not in config or not isinstance(config["supported_cities"], dict):
        raise ValueError("Config must include a 'supported_cities' mapping.")
    if "dataset_path" not in config:
        raise ValueError("Config must include a top-level 'dataset_path'.")

    return config
