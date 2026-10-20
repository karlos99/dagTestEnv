from tasks.example import extract, load, transform


def test_extract_returns_rows():
    data = extract()
    assert len(data["rows"]) == 2


def test_transform_sums_values():
    upstream = {"extract": extract()}
    result = transform(upstream_results=upstream)
    assert result["total_value"] == 30


def test_load_message():
    upstream = {
        "extract": extract(),
        "transform": transform(upstream_results={"extract": extract()}),
    }
    message = load(upstream_results=upstream)
    assert "loaded 2 rows" in message
