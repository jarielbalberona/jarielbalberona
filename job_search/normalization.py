from __future__ import annotations

import hashlib
import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import Job


TRACKING_QUERY_KEYS = {
    "advn",
    "campaignid",
    "from",
    "fromage",
    "ref",
    "source",
    "src",
    "tracking",
    "trackingid",
}

SOURCE_KEY_ALIASES = {
    "indeedph": "indeed_ph",
    "indeed_ph": "indeed_ph",
    "greenhouse_direct": "greenhouse",
    "workable_direct": "workable",
    "employer_direct": "employer_direct",
}


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", ascii_text).strip().casefold()


def normalize_company(value: str) -> str:
    return "".join(ch for ch in normalize_text(value) if ch.isalnum())


def normalize_domain(value: str) -> str:
    raw = (value or "").strip().casefold()
    if "://" not in raw:
        raw = f"https://{raw}"
    hostname = urlsplit(raw).hostname or ""
    return hostname.removeprefix("www.").rstrip(".")


def normalize_role(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalize_text(value)).strip()


def normalize_source_key(value: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", normalize_text(value)).strip("_")
    compact = key.replace("_", "")
    return SOURCE_KEY_ALIASES.get(key, SOURCE_KEY_ALIASES.get(compact, key))


def fingerprint(kind: str, value: str) -> str:
    if kind == "company":
        normalized = normalize_company(value)
    elif kind == "domain":
        normalized = normalize_domain(value)
    else:
        normalized = normalize_text(value)
    return hashlib.sha256(f"{kind}:{normalized}".encode()).hexdigest()


def canonicalize_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    hostname = (parsed.hostname or "").casefold().removeprefix("www.")
    port = f":{parsed.port}" if parsed.port else ""
    path = re.sub(r"/{2,}", "/", parsed.path or "/").rstrip("/") or "/"
    filtered = []
    for key, item in parse_qsl(parsed.query, keep_blank_values=False):
        lowered = key.casefold()
        if lowered.startswith("utm_") or lowered in TRACKING_QUERY_KEYS:
            continue
        filtered.append((key, item))
    return urlunsplit((parsed.scheme.casefold() or "https", hostname + port, path, urlencode(sorted(filtered)), ""))


def description_hash(description: str) -> str:
    return hashlib.sha256(normalize_text(description).encode()).hexdigest()


def canonical_job_url(job: Job) -> str:
    """Prefer the resolved employer/ATS destination over an aggregator URL."""

    return canonicalize_url(job.destination_ats_url or job.original_url)


def content_fingerprint(job: Job) -> str:
    payload = "|".join(
        [normalize_company(job.employer), normalize_role(job.role), description_hash(job.description)]
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def application_id(job: Job) -> str:
    core = content_fingerprint(job)
    if not normalize_text(job.description):
        core = "|".join(
            [
                normalize_company(job.employer),
                normalize_role(job.role),
                job.source_posting_id or "",
                canonical_job_url(job),
            ]
        )
    digest = hashlib.blake2b(core.encode(), digest_size=10).hexdigest()
    return f"app_{digest}"
