from app.main import _resolve_city_renderer


def test_resolve_city_renderer_returns_callable_for_live_city():
    renderer = _resolve_city_renderer("Montreal")
    assert callable(renderer)


def test_resolve_city_renderer_returns_none_for_missing_city():
    assert _resolve_city_renderer("Calgary") is None
