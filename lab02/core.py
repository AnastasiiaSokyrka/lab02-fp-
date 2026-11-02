from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import Any, TypedDict, cast


class Parcel(TypedDict):
    id: int
    sender: str
    region: str
    delivery_parts: list[float]


class ProcessedParcel(Parcel):
    delivery_cost: float


class DeliveryStats(TypedDict):
    count: int
    delivery_sum: float
    avg_delivery: float


Pipeline = Callable[[Iterable[Parcel]], list[ProcessedParcel]]


def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def composed(value: Any) -> Any:
        for function in reversed(functions):
            value = function(value)
        return value

    return composed


def normalize_senders(
    parcels: Iterable[Parcel],
) -> Iterator[Parcel]:
    return map(
        lambda parcel: cast(
            Parcel,
            {**parcel, "sender": parcel["sender"].strip().title()},
        ),
        parcels,
    )


def with_delivery_cost(
    parcels: Iterable[Parcel],
) -> Iterator[ProcessedParcel]:
    return map(
        lambda parcel: cast(
            ProcessedParcel,
            {
                **parcel,
                "delivery_cost": float(sum(parcel["delivery_parts"])),
            },
        ),
        parcels,
    )


def apply_region_coefficient(
    region: str,
    factor: float,
) -> Callable[[Iterable[ProcessedParcel]], Iterator[ProcessedParcel]]:
    def transform(
        parcels: Iterable[ProcessedParcel],
    ) -> Iterator[ProcessedParcel]:
        return map(
            lambda parcel: cast(
                ProcessedParcel,
                {
                    **parcel,
                    "delivery_cost": (
                        parcel["delivery_cost"] * factor
                        if parcel["region"] == region
                        else parcel["delivery_cost"]
                    ),
                },
            ),
            parcels,
        )

    return transform


def only_above_threshold(
    threshold: float,
) -> Callable[[Iterable[ProcessedParcel]], Iterator[ProcessedParcel]]:
    return lambda parcels: filter(
        lambda parcel: parcel["delivery_cost"] >= threshold,
        parcels,
    )


def sort_by_delivery_desc(
    parcels: Iterable[ProcessedParcel],
) -> list[ProcessedParcel]:
    return sorted(
        parcels,
        key=lambda parcel: (-parcel["delivery_cost"], parcel["id"]),
    )


def take(
    count: int,
) -> Callable[[Iterable[ProcessedParcel]], list[ProcessedParcel]]:
    return lambda parcels: list(islice(parcels, max(0, count)))


def reduce_stats(
    parcels: Iterable[ProcessedParcel],
) -> DeliveryStats:
    count, delivery_sum = reduce(
        lambda acc, parcel: (
            acc[0] + 1,
            acc[1] + parcel["delivery_cost"],
        ),
        parcels,
        (0, 0.0),
    )

    average = delivery_sum / count if count else 0.0

    return {
        "count": count,
        "delivery_sum": delivery_sum,
        "avg_delivery": average,
    }


def build_pipeline(
    top_n: int = 3,
    region: str = "West",
    factor: float = 1.1,
    threshold: float = 75.0,
) -> Pipeline:
    pipeline = compose(
        take(top_n),
        sort_by_delivery_desc,
        only_above_threshold(threshold),
        apply_region_coefficient(region, factor),
        with_delivery_cost,
        normalize_senders,
    )

    return cast(Pipeline, pipeline)