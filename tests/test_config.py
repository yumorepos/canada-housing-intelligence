from pathlib import Path

import pytest
import yaml

from app.utils.config import get_city_profiles, get_profiled_cities, load_city_config


def test_load_city_config_requires_cities(tmp_path: Path):
    config_path = tmp_path / "cities.yml"
    config_path.write_text("shared_defaults:\n  dataset_path: data.csv\n", encoding="utf-8")

    with pytest.raises(ValueError, match="cities"):
        load_city_config(str(config_path))


def test_get_city_profiles_applies_guardrail_defaults(tmp_path: Path):
    config_path = tmp_path / "cities.yml"
    payload = {
        "shared_defaults": {
            "dataset_path": "data.csv",
            "guardrails": {"min_years": 5, "min_avg_listings": 120, "min_avg_coverage": 0.7},
        },
        "cities": {
            "Montreal": {
                "display_name": "Montreal",
                "status": "live",
                "enabled": True,
                "dataset_path": "data.csv",
                "subtitle": "Montreal subtitle",
            }
        },
    }
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    config = load_city_config(str(config_path))
    profiles = get_city_profiles(config)

    assert profiles["Montreal"]["guardrails"]["min_years"] == 5
    assert profiles["Montreal"]["guardrails"]["min_avg_listings"] == 120
    assert profiles["Montreal"]["guardrails"]["min_avg_coverage"] == 0.7


def test_get_profiled_cities_separates_live_and_upcoming():
    config = load_city_config()

    implemented, upcoming = get_profiled_cities(config)

    assert {city["city"] for city in implemented} == {"Montreal", "Toronto", "Vancouver"}
    assert {city["city"] for city in upcoming} == set()


def test_vancouver_profile_is_live_and_enabled():
    config = load_city_config()
    profiles = get_city_profiles(config)

    assert profiles["Vancouver"]["status"] == "live"
    assert profiles["Vancouver"]["enabled"] is True
    assert profiles["Vancouver"]["guardrails"]["min_years"] >= 6
