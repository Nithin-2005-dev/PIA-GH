from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnifiedDeveloperIdentity:
    developer_id: str
    display_name: str
    aliases: tuple[str, ...]


class UnifiedIdentityResolver:
    def __init__(
        self,
    ):
        self._aliases: dict[tuple[str, str], UnifiedDeveloperIdentity] = {}

    def register(
        self,
        provider: str,
        external_id: str,
        developer_id: str,
        display_name: str | None = None,
        aliases: tuple[str, ...] = (),
    ) -> UnifiedDeveloperIdentity:
        identity = UnifiedDeveloperIdentity(
            developer_id=developer_id,
            display_name=display_name or developer_id,
            aliases=aliases,
        )
        self._aliases[
            (
                provider,
                external_id,
            )
        ] = identity
        return identity

    def resolve(
        self,
        provider: str,
        external_id: str | None,
    ) -> UnifiedDeveloperIdentity | None:
        if external_id is None:
            return None
        return self._aliases.get(
            (
                provider,
                external_id,
            ),
            UnifiedDeveloperIdentity(
                developer_id=external_id,
                display_name=external_id,
                aliases=(external_id,),
            ),
        )

