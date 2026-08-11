from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .candidate import load_candidate_facts


class MediaRequirement(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNKNOWN_NOT_INSPECTED = "UNKNOWN_NOT_INSPECTED"
    INACCESSIBLE = "INACCESSIBLE"


@dataclass(frozen=True, slots=True)
class MediaResolution:
    media_type: str
    requirement: MediaRequirement
    available: bool
    asset_path: Path | None
    action: str
    reason_code: str | None = None

    @property
    def blocks_readiness(self) -> bool:
        return self.action == "HOLD"


def canonical_photo_path(repository_root: Path = Path(".")) -> Path:
    photo = load_candidate_facts()["candidate_media"]["photo"]
    return repository_root / str(photo["private_asset_path"])


def resolve_candidate_media(
    media_type: str,
    requirement: MediaRequirement,
    *,
    repository_root: Path = Path("."),
    optional_use_approved: bool = False,
) -> MediaResolution:
    facts = load_candidate_facts()["candidate_media"]
    normalized = media_type.casefold().replace("-", "_").replace(" ", "_")

    if normalized in {"photo", "candidate_photo", "headshot"}:
        photo = facts["photo"]
        path = canonical_photo_path(repository_root)
        available = bool(photo["available"]) and path.is_file()
        if requirement == MediaRequirement.REQUIRED and not available:
            return MediaResolution(
                media_type="photo",
                requirement=requirement,
                available=False,
                asset_path=None,
                action="HOLD",
                reason_code="REQUIRED_CANDIDATE_PHOTO",
            )
        action = (
            "ATTACH"
            if available
            and (
                requirement == MediaRequirement.REQUIRED
                or (
                    requirement == MediaRequirement.OPTIONAL
                    and optional_use_approved
                )
            )
            else "NONE"
        )
        return MediaResolution(
            media_type="photo",
            requirement=requirement,
            available=available,
            asset_path=path if available else None,
            action=action,
        )

    if normalized in {"video", "introduction_video", "candidate_video"}:
        video = facts["introduction_video"]
        available = bool(video["available"])
        if requirement == MediaRequirement.REQUIRED and not available:
            behavior = facts["required_video_behavior"]
            return MediaResolution(
                media_type="introduction_video",
                requirement=requirement,
                available=False,
                asset_path=None,
                action=str(behavior["action"]),
                reason_code=str(behavior["reason_code"]),
            )
        return MediaResolution(
            media_type="introduction_video",
            requirement=requirement,
            available=available,
            asset_path=None,
            action="ATTACH" if available else "NONE",
        )

    raise ValueError(f"unsupported candidate media type: {media_type}")
