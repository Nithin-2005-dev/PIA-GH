from collections.abc import Mapping
from math import log2
from typing import Any


def observation(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    return payload.get(
        "observation",
        {},
    )


def commit_behavior(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    return (
        observation(payload)
        .get(
            "behavioral",
            {},
        )
        .get(
            "commit",
            {},
        )
    )


def artifact_files(
    payload: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    return list(
        observation(payload)
        .get(
            "artifact",
            {},
        )
        .get(
            "files",
            [],
        )
    )


def total_changes(
    payload: Mapping[str, Any],
) -> float:
    return float(
        commit_behavior(payload).get(
            "total_changes",
            payload.get(
                "total_changes",
                0,
            ),
        )
        or 0
    )


def additions(
    payload: Mapping[str, Any],
) -> float:
    return float(
        commit_behavior(payload).get(
            "total_additions",
            payload.get(
                "additions",
                0,
            ),
        )
        or 0
    )


def deletions(
    payload: Mapping[str, Any],
) -> float:
    return float(
        commit_behavior(payload).get(
            "total_deletions",
            payload.get(
                "deletions",
                0,
            ),
        )
        or 0
    )


def files_changed(
    payload: Mapping[str, Any],
) -> float:
    files = artifact_files(
        payload
    )

    if files:
        return float(
            len(files)
        )

    return float(
        commit_behavior(payload).get(
            "files_changed",
            0,
        )
        or 0
    )


def entropy(
    values: list[float],
) -> float:
    total = sum(
        value
        for value in values
        if value > 0
    )

    if total <= 0:
        return 0.0

    result = 0.0

    for value in values:
        if value <= 0:
            continue

        probability = value / total
        result -= probability * log2(
            probability
        )

    return result


