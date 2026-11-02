from copy import deepcopy

from core import (
    Parcel,
    ProcessedParcel,
    build_pipeline,
    compose,
    reduce_stats,
)


def sample_parcels() -> list[Parcel]:
    return [
        {
            "id": 1,
            "sender": "anna kovalenko",
            "region": "West",
            "delivery_parts": [50, 30, 20],
        },
        {
            "id": 2,
            "sender": "mark petrenko",
            "region": "East",
            "delivery_parts": [40, 30],
        },
        {
            "id": 3,
            "sender": "oleg shevchenko",
            "region": "West",
            "delivery_parts": [80, 50],
        },
        {
            "id": 4,
            "sender": "sofia melnyk",
            "region": "North",
            "delivery_parts": [60, 20],
        },
        {
            "id": 5,
            "sender": "ivan bondar",
            "region": "West",
            "delivery_parts": [30, 20],
        },
        {
            "id": 6,
            "sender": "daria kravets",
            "region": "East",
            "delivery_parts": [100, 50],
        },
    ]


def test_top_n():
    result = build_pipeline(top_n=3)(sample_parcels())

    assert [parcel["id"] for parcel in result] == [6, 3, 1]


def test_no_mutation():
    parcels = sample_parcels()
    original = deepcopy(parcels)

    build_pipeline()(parcels)

    assert parcels == original


def test_reduce_stats():
    result = build_pipeline()(sample_parcels())
    stats = reduce_stats(result)

    assert stats["count"] == 3
    assert stats["delivery_sum"] == 403.0
    assert abs(stats["avg_delivery"] - 134.3333333333) < 0.0001


def test_compose():
    add_one = lambda value: value + 1
    double = lambda value: value * 2

    combined = compose(add_one, double)

    assert combined(3) == 7


def test_region_coefficient_and_threshold():
    result = build_pipeline(
        top_n=10,
        region="West",
        factor=1.1,
        threshold=100,
    )(sample_parcels())

    assert all(parcel["delivery_cost"] >= 100 for parcel in result)
    assert result[0]["delivery_cost"] == 143.0
    assert result[1]["delivery_cost"] == 110.00000000000001