from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_data_mode_banner_source_backed_and_freshness_states():
    script = '''
from app.main import _render_data_mode_banner

_render_data_mode_banner(
    {
        "data_mode": "source_backed",
        "source_name": "Known Source",
        "source_type": "manual_csv_drop",
        "source_period": "2016-2023",
        "freshness_status": "fresh",
        "data_age_days": 3,
    },
    max_age_days=45,
)
'''
    at = AppTest.from_string(script)
    at.run(timeout=30)

    captions = " ".join(c.value for c in at.caption)
    assert "Data mode:" in captions
    assert "Source-backed processed" in captions
    assert "Known Source" in captions
    assert "2016-2023" in captions
    assert "Data freshness: 3 days old" in captions


def test_data_mode_banner_stale_and_unknown_paths():
    stale_script = '''
from app.main import _render_data_mode_banner

_render_data_mode_banner(
    {
        "data_mode": "source_backed",
        "source_name": "Known Source",
        "source_type": "manual_csv_drop",
        "source_period": "2016-2023",
        "freshness_status": "stale",
        "data_age_days": 90,
    },
    max_age_days=45,
)
'''
    stale = AppTest.from_string(stale_script)
    stale.run(timeout=30)
    assert any("stale" in w.value.lower() for w in stale.warning)

    unknown_script = '''
from app.main import _render_data_mode_banner

_render_data_mode_banner(
    {
        "data_mode": "sample",
        "source_name": "Fallback Sample",
        "source_type": "sample",
        "source_period": "n/a",
        "freshness_status": "unknown",
    },
    max_age_days=45,
)
'''
    unknown = AppTest.from_string(unknown_script)
    unknown.run(timeout=30)
    unknown_captions = " ".join(c.value for c in unknown.caption)

    assert "Local sample" in unknown_captions
    assert any("freshness status unavailable" in w.value.lower() for w in unknown.warning)


def test_canada_overview_renders_mode_and_provenance_fields():
    script = '''
import pandas as pd
from app.pages.canada_overview import render_canada_overview

data = pd.DataFrame({
    "city": ["Montreal", "Montreal", "Toronto", "Toronto"],
    "neighborhood": ["Plateau", "Plateau", "Downtown", "Downtown"],
    "year": [2023, 2024, 2023, 2024],
    "average_rent": [1800, 1900, 2400, 2500],
    "median_price": [600000, 640000, 900000, 950000],
    "listing_count": [180, 190, 220, 210],
    "coverage_score": [0.82, 0.84, 0.80, 0.81],
    "borough": ["Core", "Core", "Core", "Core"],
})
implemented = [{"city": "Montreal", "display_name": "Montreal", "canada_positioning": "Balanced profile."}]
render_canada_overview(
    data,
    implemented_profiles=implemented,
    upcoming_profiles=[],
    provenance={
        "data_mode": "source_backed",
        "source_name": "Known Source",
        "source_type": "manual_csv_drop",
        "source_period": "2016-2023",
        "processed_at": "2026-03-20T00:00:00+00:00",
    },
)
'''
    at = AppTest.from_string(script)
    at.run(timeout=30)

    captions = " ".join(c.value for c in at.caption)
    markdown = " ".join(m.value for m in at.markdown)
    assert "source-backed processed data" in captions
    assert "Data provenance" in markdown
    assert "Known Source" in markdown
    assert "2016-2023" in markdown


def test_city_overview_renders_source_context_and_unknown_recency_text():
    script = '''
import pandas as pd
from app.pages.city_overview import render_city_overview

rows = []
for neighborhood, base_rent, base_price in [("Plateau", 1700, 550000), ("Rosemont", 1600, 500000)]:
    for i, year in enumerate([2021, 2022, 2023, 2024]):
        rows.append({
            "city": "Montreal",
            "neighborhood": neighborhood,
            "year": year,
            "average_rent": base_rent + i * 80,
            "median_price": base_price + i * 20000,
            "listing_count": 200,
            "coverage_score": 0.83,
            "borough": "Core",
        })

data = pd.DataFrame(rows)
render_city_overview(
    data,
    city="Montreal",
    subtitle="City trust test",
    guardrails={"min_years": 4, "min_avg_listings": 100, "min_avg_coverage": 0.7},
    provenance={
        "source_name": "Test Source",
        "source_type": "manual_csv_drop",
        "source_period": "2021-2024",
    },
)
'''
    at = AppTest.from_string(script)
    at.run(timeout=30)

    assert any("Test Source" in i.value for i in at.info)
    joined_markdown = " ".join(m.value for m in at.markdown)
    assert "processed at **unknown**" in joined_markdown
