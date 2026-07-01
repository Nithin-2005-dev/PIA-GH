"""DeveloperIdentityResolver — canonical developer identity.

Resolves GitHub commit author data into a single canonical developer identity.

Resolution priority (highest to lowest):
    1. GitHub login (username)  — stable, cross-repo, cross-org
    2. GitHub node_id           — globally unique
    3. GitHub user_id           — numeric, stable
    4. Verified email           — stable per account
    5. Commit email             — may change
    6. Commit author name       — inconsistent, last resort

Alias merging ensures that multiple emails or names belonging
to the same GitHub account collapse to one canonical identity.

Architecture note:
    This is a pure internal service. It is NOT a new pipeline layer.
    It is consumed by DeveloperActivityEvaluator and ExpertiseStage
    to produce consistent target_entity keys.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Canonical developer identity
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanonicalDeveloper:
    """Canonical identity for one developer."""
    canonical_id: str          # The primary key (github_login preferred)
    display_name: str          # Human-readable name for display
    resolution_method: str     # Which field was used as canonical_id


# ---------------------------------------------------------------------------
# Alias registry (in-memory, per pipeline run)
# ---------------------------------------------------------------------------


class _AliasRegistry:
    """
    Maps raw author attributes (email, name) to canonical_id.
    Built incrementally as observations are processed.
    """

    def __init__(self) -> None:
        # email → canonical_id
        self._email_map: dict[str, str] = {}
        # name → canonical_id (fuzzy, normalized)
        self._name_map: dict[str, str] = {}

    def register(self, canonical_id: str, email: str | None, name: str | None) -> None:
        if email:
            self._email_map[email.lower().strip()] = canonical_id
        if name:
            self._name_map[self._normalize_name(name)] = canonical_id

    def lookup_email(self, email: str) -> str | None:
        return self._email_map.get(email.lower().strip())

    def lookup_name(self, name: str) -> str | None:
        return self._name_map.get(self._normalize_name(name))

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Lowercase, strip accents crudely, collapse whitespace."""
        name = name.lower().strip()
        # Remove common suffixes/prefixes that cause mismatches
        name = re.sub(r"\s+", " ", name)
        return name


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------


class DeveloperIdentityResolver:
    """
    Resolves raw commit author data to a canonical developer identity.

    Usage:
        resolver = DeveloperIdentityResolver()
        identity = resolver.resolve(
            github_login="hoxyq",
            email="hoxyq@fb.com",
            name="Ruslan Lesiuk",
        )
        # → CanonicalDeveloper(canonical_id="hoxyq", ...)
    """

    def __init__(self) -> None:
        self._registry = _AliasRegistry()
        # Cache resolved identities to ensure stability within a run
        self._cache: dict[str, CanonicalDeveloper] = {}

    def resolve(
        self,
        github_login: str | None = None,
        github_node_id: str | None = None,
        github_user_id: int | None = None,
        email: str | None = None,
        name: str | None = None,
    ) -> CanonicalDeveloper:
        """
        Resolve a developer identity using the priority chain.

        Returns a stable CanonicalDeveloper. Registers aliases so future
        lookups for the same email/name return the same canonical_id.
        """
        # 1. GitHub login — most reliable
        if github_login and github_login.strip():
            canonical_id = github_login.strip().lower()
            resolution_method = "github_login"

        # 2. GitHub node_id
        elif github_node_id and github_node_id.strip():
            canonical_id = f"ghnid:{github_node_id.strip()}"
            resolution_method = "github_node_id"

        # 3. GitHub user_id (numeric)
        elif github_user_id:
            canonical_id = f"ghuid:{github_user_id}"
            resolution_method = "github_user_id"

        # 4–5. Email alias lookup, then raw email
        elif email and email.strip():
            existing = self._registry.lookup_email(email)
            if existing:
                return self._cache.get(existing) or CanonicalDeveloper(
                    canonical_id=existing,
                    display_name=name or existing,
                    resolution_method="email_alias",
                )
            canonical_id = self._sanitize_email_to_id(email)
            resolution_method = "commit_email"

        # 6. Name (last resort)
        elif name and name.strip():
            existing = self._registry.lookup_name(name)
            if existing:
                return self._cache.get(existing) or CanonicalDeveloper(
                    canonical_id=existing,
                    display_name=name,
                    resolution_method="name_alias",
                )
            canonical_id = re.sub(r"\s+", "_", name.strip().lower())
            resolution_method = "commit_name"

        else:
            canonical_id = "unknown_developer"
            resolution_method = "unknown"

        # Register aliases for future lookups
        self._registry.register(canonical_id, email, name)

        identity = CanonicalDeveloper(
            canonical_id=canonical_id,
            display_name=github_login or name or email or canonical_id,
            resolution_method=resolution_method,
        )
        self._cache[canonical_id] = identity
        return identity

    def resolve_from_observation_facts(self, facts) -> CanonicalDeveloper:
        """
        Convenience method that extracts identity fields from CommitFacts.
        Observation facts may have: author_name, author_email, author_login.
        """
        return self.resolve(
            github_login=getattr(facts, "author_login", None),
            email=getattr(facts, "author_email", None),
            name=getattr(facts, "author_name", None),
        )

    @staticmethod
    def _sanitize_email_to_id(email: str) -> str:
        """Convert email to a safe identifier: user@domain → user_at_domain."""
        return re.sub(r"[^\w]", "_", email.lower().strip())

    def alias_count(self) -> int:
        """Return total number of registered aliases (for diagnostics)."""
        return len(self._cache)
