from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_REQUIRED_CITY_FIELDS = {"display_name", "status", "enabled", "dataset_path", "subtitle"}


def load_city_config(config_path: str = "config/cities.yml") -> dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if "cities" not in config or not isinstance(config["cities"], dict):
        raise ValueError("Config must include a 'cities' mapping.")

    shared_defaults = config.get("shared_defaults", {})
    if "dataset_path" not in shared_defaults:
        raise ValueError("Config must include shared_defaults.dataset_path.")
    if "fallback_dataset_path" not in shared_defaults:
        raise ValueError("Config must include shared_defaults.fallback_dataset_path.")

    for city_name, profile in config["cities"].items():
        missing = _REQUIRED_CITY_FIELDS.difference(profile.keys())
        if missing:
            raise ValueError(f"City '{city_name}' is missing required fields: {sorted(missing)}")

    return config


def get_city_profiles(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    shared_defaults = config.get("shared_defaults", {})
    default_dataset = shared_defaults.get("dataset_path")
    fallback_dataset = shared_defaults.get("fallback_dataset_path")
    default_guardrails = shared_defaults.get("guardrails", {})
    freshness_defaults = shared_defaults.get("freshness", {})

    profiles: dict[str, dict[str, Any]] = {}
    for city_name, profile in config["cities"].items():
        merged = {
            "city": city_name,
            "display_name": profile["display_name"],
            "status": profile["status"],
            "enabled": bool(profile["enabled"]),
            "dataset_path": profile.get("dataset_path", default_dataset),
            "fallback_dataset_path": profile.get("fallback_dataset_path", fallback_dataset),
            "subtitle": profile["subtitle"],
            "canada_positioning": profile.get("canada_positioning"),
            "upcoming_note": profile.get("upcoming_note"),
            "chart_labels": profile.get("chart_labels", {}),
            "guardrails": {
                "min_years": int(profile.get("guardrails", {}).get("min_years", default_guardrails.get("min_years", 6))),
                "min_avg_listings": int(
                    profile.get("guardrails", {}).get("min_avg_listings", default_guardrails.get("min_avg_listings", 150))
                ),
                "min_avg_coverage": float(
                    profile.get("guardrails", {}).get("min_avg_coverage", default_guardrails.get("min_avg_coverage", 0.72))
                ),
            },
            "freshness": {
                "max_age_days": int(profile.get("freshness", {}).get("max_age_days", freshness_defaults.get("max_age_days", 45)))
            },
        }
        profiles[city_name] = merged

    return profiles


def get_profiled_cities(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profiles = get_city_profiles(config)
    implemented = [
        profile
        for profile in profiles.values()
        if profile["enabled"] and profile["status"] == "live"
    ]
    upcoming = [profile for profile in profiles.values() if profile["status"] != "live"]
    return implemented, upcoming
