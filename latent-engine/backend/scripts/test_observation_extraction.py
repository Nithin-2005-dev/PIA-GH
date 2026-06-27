import json
import os
from pathlib import Path

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import GitHubRestGateway
from app.ports.event_query import EventQuery


def main():

    token = os.environ["GITHUB_TOKEN"]

    gateway = GitHubRestGateway(token)
    adapter = GitHubAdapter(gateway)

    query = EventQuery(
        identifier="facebook/react",
        filters={
            "per_page": 1,
        },
    )

    event = adapter.collect(query)[0]

    observation = event.payload["observation"]

    output_dir = Path("scripts/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(
        output_dir / "observation.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            observation,
            f,
            indent=4,
            default=str,
        )

    print("=" * 80)
    print("M31 OBSERVATION EXTRACTION TEST")
    print("=" * 80)

    print(f"Commit SHA : {event.payload['sha']}")
    print()

    print("Observation Categories")

    for category in observation.keys():
        print(f"✓ {category}")

    print()

    print("Category Summary")

    for category, value in observation.items():

        if isinstance(value, dict):
            print(f"{category:15} : {len(value)} entries")

        elif isinstance(value, list):
            print(f"{category:15} : {len(value)} items")

        else:
            print(f"{category:15} : {type(value).__name__}")

    print()

    print("Observation saved to:")
    print(output_dir / "observation.json")

    print("=" * 80)


if __name__ == "__main__":
    main()