from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.event import Event
from app.domain.event_type import EventType

from app.ports.event_query import EventQuery
from app.ports.event_source_port import EventSourcePort

from app.adapters.github.gateway import GitHubGateway


class GitHubAdapter(EventSourcePort):

    def __init__(
        self,
        gateway: GitHubGateway,
    ):
        self._gateway = gateway

    def collect(
        self,
        query: EventQuery,
    ) -> list[Event]:

        owner, repo = query.identifier.split("/")

        raw_commits = self._gateway.fetch_commits(query)

        events = []

        for raw_commit in raw_commits:

            sha = raw_commit["sha"]

            details = self._gateway.fetch_commit_details(
                owner=owner,
                repo=repo,
                sha=sha,
            )

            events.append(
                self._normalize_commit(
                    raw_commit,
                    details,
                )
            )

        return events

    def _normalize_commit(
        self,
        raw: dict,
        details: dict,
    ) -> Event:

        return Event(
            id=self._event_id(raw),

            type=EventType.COMMIT,

            actor_ref=self._actor(raw),

            target_refs=self._targets(details),

            occurred_at=self._occurred_at(raw),

            payload=self._payload(
                raw,
                details,
            ),

            metadata=self._metadata(),
        )

    def _event_id(
        self,
        raw: dict,
    ):

        sha = raw["sha"]

        return uuid5(
            NAMESPACE_URL,
            sha,
        )

    def _actor(
        self,
        raw: dict,
    ) -> EntityRef:

        author = raw.get("author")

        if author is None:
            return EntityRef(
                id="unknown",
                type=EntityType.DEVELOPER,
            )

        return EntityRef(
            id=author["login"],
            type=EntityType.DEVELOPER,
        )

    def _targets(
        self,
        details: dict,
    ) -> tuple[EntityRef, ...]:

        files = details.get(
            "files",
            [],
        )

        targets = []

        for file in files:

            targets.append(
                EntityRef(
                    id=file["filename"],
                    type=EntityType.FILE,
                )
            )

        return tuple(targets)

    def _occurred_at(
        self,
        raw: dict,
    ) -> datetime:

        timestamp = raw["commit"]["author"]["date"]

        return datetime.fromisoformat(
            timestamp.replace(
                "Z",
                "+00:00",
            )
        )

    def _payload(
        self,
        raw: dict,
        details: dict,
    ) -> dict:

        stats = details.get(
            "stats",
            {},
        )

        observation = {

            # ------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------
            "identity": {

                "commit_sha": raw["sha"],

                "commit_node_id": raw.get(
                    "node_id",
                ),

                "tree_sha": raw.get(
                    "commit",
                    {},
                ).get(
                    "tree",
                    {},
                ).get(
                    "sha",
                ),

                "parent_shas": [

                    parent.get("sha")

                    for parent in raw.get(
                        "parents",
                        [],
                    )

                ],

                "commit_url": raw.get(
                    "url",
                ),

                "html_url": raw.get(
                    "html_url",
                ),

            },

            # ------------------------------------------------------------
            # Temporal
            # ------------------------------------------------------------
            "temporal": {

    # ------------------------------------------------------------
    # Commit timestamps
    # ------------------------------------------------------------

            "author": {

                "timestamp": raw.get(
                    "commit",
                    {},
                ).get(
                    "author",
                    {},
                ).get(
                    "date",
                ),

                "name": raw.get(
                    "commit",
                    {},
                ).get(
                    "author",
                    {},
                ).get(
                    "name",
                ),

                "email": raw.get(
                    "commit",
                    {},
                ).get(
                    "author",
                    {},
                ).get(
                    "email",
                ),
            },

            "committer": {

                "timestamp": raw.get(
                    "commit",
                    {},
                ).get(
                    "committer",
                    {},
                ).get(
                    "date",
                ),

                "name": raw.get(
                    "commit",
                    {},
                ).get(
                    "committer",
                    {},
                ).get(
                    "name",
                ),

                "email": raw.get(
                    "commit",
                    {},
                ).get(
                    "committer",
                    {},
                ).get(
                    "email",
                ),
            },

            # ------------------------------------------------------------
            # Derived deterministic facts
            # ------------------------------------------------------------

            "author_equals_committer_time":
                (
                    raw.get("commit", {})
                    .get("author", {})
                    .get("date")
                    ==
                    raw.get("commit", {})
                    .get("committer", {})
                    .get("date")
                ),
        },

            # ------------------------------------------------------------
            # Actor
            # ------------------------------------------------------------
            "actor": {

                "author": {

                    "login": (
                        raw.get("author") or {}
                    ).get("login"),

                    "id": (
                        raw.get("author") or {}
                    ).get("id"),

                    "node_id": (
                        raw.get("author") or {}
                    ).get("node_id"),

                    "type": (
                        raw.get("author") or {}
                    ).get("type"),

                    "site_admin": (
                        raw.get("author") or {}
                    ).get("site_admin"),
                },

                "committer": {

                    "login": (
                        raw.get("committer") or {}
                    ).get("login"),

                    "id": (
                        raw.get("committer") or {}
                    ).get("id"),

                    "node_id": (
                        raw.get("committer") or {}
                    ).get("node_id"),

                    "type": (
                        raw.get("committer") or {}
                    ).get("type"),

                    "site_admin": (
                        raw.get("committer") or {}
                    ).get("site_admin"),
                },

                "is_author_same_as_committer":
                    (
                        (raw.get("author") or {}).get("id")
                        ==
                        (raw.get("committer") or {}).get("id")
                    ),
            },

            # ------------------------------------------------------------
            # Artifact
            # ------------------------------------------------------------
            "artifact": {

            "files": [

                {

                    # --------------------------------------------------------
                    # Identity
                    # --------------------------------------------------------

                    "filename": file.get("filename"),

                    "previous_filename": file.get("previous_filename"),

                    "sha": file.get("sha"),

                    # --------------------------------------------------------
                    # Structural
                    # --------------------------------------------------------

                    "status": file.get("status"),

                    # added / modified / removed / renamed

                    # --------------------------------------------------------
                    # Change Facts
                    # --------------------------------------------------------

                    "additions": file.get("additions", 0),

                    "deletions": file.get("deletions", 0),

                    "changes": file.get("changes", 0),

                    # --------------------------------------------------------
                    # Raw Engineering Information
                    # --------------------------------------------------------

                    "patch": file.get("patch"),

                    "blob_url": file.get("blob_url"),

                    "raw_url": file.get("raw_url"),

                    "contents_url": file.get("contents_url"),
                }

                for file in details.get(
                    "files",
                    [],
                )

            ]
        },

            # ------------------------------------------------------------
            # Behavioral
            # ------------------------------------------------------------
            "behavioral": {

    # ------------------------------------------------------------
    # Commit-level behavior
    # ------------------------------------------------------------

                "commit": {

                    "files_changed": len(
                        details.get(
                            "files",
                            [],
                        )
                    ),

                    "total_additions": details.get(
                        "stats",
                        {},
                    ).get(
                        "additions",
                        0,
                    ),

                    "total_deletions": details.get(
                        "stats",
                        {},
                    ).get(
                        "deletions",
                        0,
                    ),

                    "total_changes": details.get(
                        "stats",
                        {},
                    ).get(
                        "total",
                        0,
                    ),
                },

                # ------------------------------------------------------------
                # File-level actions
                # ------------------------------------------------------------

                "operations": [

                    {

                        "filename": file.get("filename"),

                        "operation": file.get("status"),

                        "changes": file.get("changes", 0),

                    }

                    for file in details.get(
                        "files",
                        [],
                    )

                ],
            },

            # ------------------------------------------------------------
            # Semantic
            # ------------------------------------------------------------
            "semantic": {

                # ------------------------------------------------------------
                # Commit Message
                # ------------------------------------------------------------

                "commit": {

                    "message": raw.get(
                        "commit",
                        {},
                    ).get(
                        "message",
                    ),

                },

                # ------------------------------------------------------------
                # File Semantics
                # ------------------------------------------------------------

                "files": [

                    {

                        "filename": file.get(
                            "filename",
                        ),

                        "patch": file.get(
                            "patch",
                        ),

                    }

                    for file in details.get(
                        "files",
                        [],
                    )

                ],

            },

            # ------------------------------------------------------------
            # Process
            # ------------------------------------------------------------
            "process": {

                "parents": [

                    {

                        "sha": parent.get("sha"),

                        "url": parent.get("url"),

                        "html_url": parent.get("html_url"),

                    }

                    for parent in raw.get(
                        "parents",
                        [],
                    )

                ],

            },

            # ------------------------------------------------------------
            # Provenance
            # ------------------------------------------------------------
            "provenance": {

            "platform": "github",

            "gateway": "rest",

            "api_version": "v3",

            "normalized_by": "GitHubAdapter",

            "event_type": EventType.COMMIT.value,

        },

            # ------------------------------------------------------------
            # Integrity
            # ------------------------------------------------------------
            "integrity": {

            "verification": {

                "verified": details.get(
                    "commit",
                    {},
                ).get(
                    "verification",
                    {},
                ).get(
                    "verified",
                ),

                "reason": details.get(
                    "commit",
                    {},
                ).get(
                    "verification",
                    {},
                ).get(
                    "reason",
                ),

                "signature": details.get(
                    "commit",
                    {},
                ).get(
                    "verification",
                    {},
                ).get(
                    "signature",
                ),

                "payload": details.get(
                    "commit",
                    {},
                ).get(
                    "verification",
                    {},
                ).get(
                    "payload",
                ),
            }

        },

            # ------------------------------------------------------------
            # Raw Observation
            # ------------------------------------------------------------
            "raw": {

            "commit": raw,

            "details": details,

        },
        }

        return {

            # ============================================================
            # Backward Compatibility
            # ============================================================

            "sha": raw["sha"],

            "message": raw["commit"]["message"],

            "additions": stats.get(
                "additions",
                0,
            ),

            "deletions": stats.get(
                "deletions",
                0,
            ),

            "total_changes": stats.get(
                "total",
                0,
            ),

            # ============================================================
            # Rich Observation Model
            # ============================================================

            "observation": observation,
        }

    def _metadata(
        self,
    ) -> dict:

        return {
            "source": "github",
            "gateway": "rest",
        }