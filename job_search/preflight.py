from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .media import MediaRequirement, resolve_candidate_media


@dataclass(frozen=True, slots=True)
class ApplicationPreflight:
    can_prepare: bool
    queue_status: str | None
    blockers: tuple[str, ...]
    declarations: tuple[str, ...]


def evaluate_application_preflight(
    fields: Iterable[Mapping[str, object]],
    *,
    video_requirement: MediaRequirement = MediaRequirement.UNKNOWN_NOT_INSPECTED,
    photo_requirement: MediaRequirement = MediaRequirement.UNKNOWN_NOT_INSPECTED,
) -> ApplicationPreflight:
    blockers: list[str] = []
    declarations: list[str] = []
    for field in fields:
        label = str(field.get("label", "")).casefold()
        required = bool(field.get("required", False))
        if required and any(term in label for term in ("captcha", "human verification", "identity verification")):
            blockers.append("HUMAN_VERIFICATION_REQUIRED")
        if required and any(term in label for term in ("record a video", "video introduction", "video intro")):
            video_requirement = MediaRequirement.REQUIRED
        if required and any(term in label for term in ("profile photo", "headshot", "candidate photo")):
            photo_requirement = MediaRequirement.REQUIRED
        if any(term in label for term in ("declaration", "certify", "confidential", "assign ownership")):
            declarations.append(str(field.get("label", "")).strip())

    video = resolve_candidate_media("video", video_requirement)
    photo = resolve_candidate_media("photo", photo_requirement)
    for resolution in (video, photo):
        if resolution.blocks_readiness and resolution.reason_code:
            blockers.append(resolution.reason_code)
    queue_status = "VIDEO_REQUIRED" if "REQUIRED_VIDEO_INTRO" in blockers else ("HOLD" if blockers else None)
    return ApplicationPreflight(not blockers, queue_status, tuple(blockers), tuple(declarations))
