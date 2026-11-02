import argparse
import json
from pathlib import Path
from typing import cast

from core import (
    Parcel,
    ProcessedParcel,
    build_pipeline,
    reduce_stats,
)


def load_parcels() -> list[Parcel]:
    data_path = Path(__file__).with_name("sample_data.json")

    with data_path.open("r", encoding="utf-8") as file:
        return cast(list[Parcel], json.load(file))


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Parcel delivery cost analysis"
    )
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--boost-region", default="West")
    parser.add_argument("--factor", type=float, default=1.1)
    parser.add_argument("--threshold", type=float, default=75.0)

    args = parser.parse_args()

    parcels = load_parcels()

    pipeline = build_pipeline(
        top_n=args.top,
        region=args.boost_region,
        factor=args.factor,
        threshold=args.threshold,
    )

    result: list[ProcessedParcel] = pipeline(parcels)
    stats = reduce_stats(result)

    print("Parcel delivery report")
    print("-" * 35)

    for parcel in result:
        print(
            f"Parcel {parcel['id']}: "
            f"{parcel['sender']} | "
            f"{parcel['region']} | "
            f"{parcel['delivery_cost']:.2f} UAH"
        )

    print("-" * 35)
    print(f"Number of parcels: {stats['count']}")
    print(f"Total delivery cost: {stats['delivery_sum']:.2f} UAH")
    print(f"Average delivery cost: {stats['avg_delivery']:.2f} UAH")


if __name__ == "__main__":
    run()