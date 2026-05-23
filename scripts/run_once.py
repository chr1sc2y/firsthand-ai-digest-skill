#!/usr/bin/env python3
"""Collect a source pack for the Firsthand AI Digest daily report.

The script is deliberately conservative: it discovers candidate item/detail pages
and original outbound links, fetches what is publicly accessible, and writes a
Markdown source pack for Codex or another analyst to turn into a final report.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


DEFAULT_SITE = "https://ai.prov1dence.top/"
USER_AGENT = "Mozilla/5.0 (compatible; ai-providence-daily-skill/1.0)"
SKIP_EXTENSIONS = (
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
    ".zip",
)
METADATA_ONLY_HOSTS = (
    "youtube.com",
    "youtu.be",
    "x.com",
    "twitter.com",
    "t.co",
    "linkedin.com",
    "lnkd.in",
    "spotify.com",
    "podcasts.apple.com",
    "simplecast.com",
)
SECONDARY_SKIP_HOSTS = (
    "github.com",
    "news.ycombinator.com",
    "fandf.co",
    "exe.dev",
)
SECONDARY_SKIP_TEXT = (
    "sponsor",
    "subscribe",
    "login",
    "register",
    "via",
    "about",
    "tag",
)


@dataclass
class FetchResult:
    url: str
    ok: bool
    status: int | None = None
    content_type: str = ""
    text: str = ""
    error: str = ""


@dataclass
class PageInfo:
    url: str
    title: str = ""
    description: str = ""
    text_excerpt: str = ""
    links: list[tuple[str, str]] = field(default_factory=list)
    published: str = ""
    fetch_error: str = ""


@dataclass
class DigestItem:
    url: str
    title: str = ""
    source_type: str = ""
    published: dt.datetime | None = None
    summary: str = ""


def digest_item_to_page(item: DigestItem, note: str = "") -> PageInfo:
    published = item.published.isoformat() if item.published else ""
    return PageInfo(
        url=item.url,
        title=item.title,
        description=item.summary,
        published=published,
        fetch_error=note,
    )


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.meta: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._capture_title = False
        self._link_href: str | None = None
        self._link_text: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._capture_title = True
        if tag == "meta":
            key = attrs_dict.get("property") or attrs_dict.get("name")
            content = attrs_dict.get("content")
            if key and content:
                self.meta[key.lower()] = html.unescape(content.strip())
        if tag == "a" and attrs_dict.get("href"):
            self._link_href = attrs_dict["href"]
            self._link_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._capture_title = False
        if tag == "a" and self._link_href:
            text = normalize_text(" ".join(self._link_text))
            self.links.append((self._link_href, text))
            self._link_href = None
            self._link_text = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._capture_title:
            self.title_parts.append(data)
        if self._link_href:
            self._link_text.append(data)
        cleaned = normalize_text(data)
        if cleaned:
            self.text_parts.append(cleaned)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def strip_tags(value: str) -> str:
    return normalize_text(re.sub(r"<[^>]+>", " ", value))


def parse_iso_datetime(value: str) -> dt.datetime | None:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def fetch(url: str, timeout: int = 8) -> FetchResult:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_000)
            content_type = response.headers.get("content-type", "")
            charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")
            return FetchResult(url=url, ok=True, status=response.status, content_type=content_type, text=text)
    except urllib.error.HTTPError as exc:
        return FetchResult(url=url, ok=False, status=exc.code, error=f"HTTP {exc.code}: {exc.reason}")
    except Exception as exc:  # noqa: BLE001 - report all fetch failures in source pack
        return FetchResult(url=url, ok=False, error=f"{type(exc).__name__}: {exc}")


def fetch_with_retries(url: str, timeout: int, attempts: int = 2) -> FetchResult:
    result = FetchResult(url=url, ok=False, error="not attempted")
    for attempt in range(attempts):
        result = fetch(url, timeout=timeout)
        if result.ok:
            return result
        if attempt + 1 < attempts:
            time.sleep(1)
    return result


def parse_page(url: str, fetch_result: FetchResult) -> PageInfo:
    page = PageInfo(url=url)
    if not fetch_result.ok:
        page.fetch_error = fetch_result.error
        return page

    parser = LinkExtractor()
    parser.feed(fetch_result.text)
    page.title = normalize_text(
        parser.meta.get("og:title")
        or parser.meta.get("twitter:title")
        or " ".join(parser.title_parts)
    )
    page.description = normalize_text(
        parser.meta.get("description")
        or parser.meta.get("og:description")
        or parser.meta.get("twitter:description")
    )
    page.published = first_nonempty(
        parser.meta.get("article:published_time"),
        parser.meta.get("date"),
        parser.meta.get("publishdate"),
        find_json_ld_date(fetch_result.text),
    )
    page.text_excerpt = normalize_text(" ".join(parser.text_parts))[:2500]
    page.links = normalize_links(url, parser.links)
    return page


def host_matches(url: str, host_patterns: tuple[str, ...]) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == pattern or host.endswith(f".{pattern}") for pattern in host_patterns)


def fetch_page_for_item(item: DigestItem, timeout: int, metadata_only_hosts: tuple[str, ...]) -> PageInfo:
    if host_matches(item.url, metadata_only_hosts):
        return digest_item_to_page(item, "metadata-only host; use browser/platform-specific access for full content")
    return parse_page(item.url, fetch(item.url, timeout=timeout))


def fetch_pages_parallel(
    urls: list[str],
    timeout: int,
    workers: int,
    metadata_only_hosts: tuple[str, ...],
) -> list[PageInfo]:
    def fetch_one(url: str) -> PageInfo:
        if host_matches(url, metadata_only_hosts):
            return PageInfo(url=url, fetch_error="metadata-only host; skipped raw HTML fetch")
        return parse_page(url, fetch(url, timeout=timeout))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(fetch_one, urls))


def fetch_items_parallel(
    items: list[DigestItem],
    timeout: int,
    workers: int,
    metadata_only_hosts: tuple[str, ...],
) -> list[PageInfo]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch_page_for_item, item, timeout, metadata_only_hosts) for item in items]
        return [future.result() for future in futures]


def first_nonempty(*values: str | None) -> str:
    for value in values:
        if value:
            return normalize_text(value)
    return ""


def find_json_ld_date(text: str) -> str:
    for match in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', text, re.I | re.S):
        blob = html.unescape(match.group(1)).strip()
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            item = stack.pop(0)
            if isinstance(item, dict):
                for key in ("datePublished", "dateCreated", "uploadDate"):
                    if item.get(key):
                        return str(item[key])
                for value in item.values():
                    if isinstance(value, (dict, list)):
                        stack.extend(value if isinstance(value, list) else [value])
    return ""


def normalize_links(base_url: str, links: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for href, text in links:
        absolute = urllib.parse.urljoin(base_url, href)
        parsed = urllib.parse.urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        clean = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))
        if clean.lower().endswith(SKIP_EXTENSIONS):
            continue
        if clean not in seen:
            seen.add(clean)
            out.append((clean, text))
    return out


def parse_digest_items(base_url: str, text: str, since: dt.datetime, until: dt.datetime) -> list[DigestItem]:
    items: list[DigestItem] = []
    for card_match in re.finditer(r'<article class="card">(.*?)</article>', text, re.S | re.I):
        card = card_match.group(1)
        time_match = re.search(r'data-iso="([^"]+)"', card)
        href_match = re.search(r'<a[^>]+class="[^"]*card-link[^"]*"[^>]+href="([^"]+)"', card, re.S | re.I)
        if not time_match or not href_match:
            continue
        published = parse_iso_datetime(html.unescape(time_match.group(1)))
        if not published or published < since or published > until:
            continue
        title_match = re.search(r'<div class="card-title">(.*?)</div>', card, re.S | re.I)
        summary_match = re.search(r'<div class="card-summary">(.*?)</div>', card, re.S | re.I)
        badge_match = re.search(r'<span class="card-badge[^"]*">(.*?)</span>', card, re.S | re.I)
        items.append(
            DigestItem(
                url=urllib.parse.urljoin(base_url, html.unescape(href_match.group(1))),
                title=strip_tags(title_match.group(1)) if title_match else "",
                source_type=strip_tags(badge_match.group(1)) if badge_match else source_kind(href_match.group(1)),
                published=published,
                summary=strip_tags(summary_match.group(1)) if summary_match else "",
            )
        )
    return items


def same_host(url: str, site: str) -> bool:
    return urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(site).netloc


def is_secondary_candidate(url: str, text: str, site: str, source_host: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    label = normalize_text(text).lower()
    if not host or host == source_host or same_host(url, site):
        return False
    if host_matches(url, SECONDARY_SKIP_HOSTS):
        return False
    if any(word in label for word in SECONDARY_SKIP_TEXT):
        return False
    if path in {"", "/"} or path.startswith(("/about", "/tags", "/tag", "/archive")):
        return False
    return True


def source_kind(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    path = urllib.parse.urlparse(url).path.lower()
    if "youtube.com" in host or "youtu.be" in host or "vimeo.com" in host or "bilibili.com" in host:
        return "video"
    if "podcasts.apple.com" in host or "spotify.com" in host or "podcast" in host or "transistor.fm" in host:
        return "podcast"
    if host in {"x.com", "twitter.com"} or host.endswith(".x.com") or host.endswith(".twitter.com"):
        return "x-post"
    if "arxiv.org" in host or path.endswith(".pdf"):
        return "paper"
    if "github.com" in host:
        return "code"
    if any(word in host for word in ("openai", "anthropic", "google", "microsoft", "meta", "nvidia")):
        return "official/blog"
    return "web"


def rank_detail_link(url: str, text: str, site: str) -> int:
    if not same_host(url, site):
        return -1
    parsed = urllib.parse.urlparse(url)
    score = len(parsed.path)
    if re.search(r"\d{4}|\d{2}", parsed.path):
        score += 20
    if text and len(text) > 12:
        score += 10
    if parsed.path in {"", "/"}:
        score -= 100
    return score


def write_report(
    path: Path,
    site: str,
    hours: int,
    homepage: PageInfo,
    detail_pages: list[PageInfo],
    digest_items: list[DigestItem],
    originals: list[PageInfo],
    secondary_sources: list[PageInfo],
) -> None:
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    start = now - dt.timedelta(hours=hours)
    lines: list[str] = []
    lines.append(f"# Firsthand AI Digest Source Pack")
    lines.append("")
    lines.append(f"- Generated: {now.isoformat(timespec='seconds')}")
    lines.append(f"- Intended coverage window: {start.isoformat(timespec='seconds')} to {now.isoformat(timespec='seconds')}")
    lines.append(f"- Index site: {site}")
    lines.append(f"- Firsthand AI Digest items in window: {len(digest_items)}")
    lines.append(f"- Detail pages fetched: {len(detail_pages)}")
    lines.append(f"- First-layer original sources fetched/listed: {len(originals)}")
    lines.append(f"- Original sources with fetched page text: {sum(1 for page in originals if not page.fetch_error)}")
    lines.append(f"- Metadata-only original sources: {sum(1 for page in originals if page.fetch_error.startswith('metadata-only'))}")
    lines.append(f"- Other limited original sources: {sum(1 for page in originals if page.fetch_error and not page.fetch_error.startswith('metadata-only'))}")
    lines.append(f"- Secondary source candidates fetched/listed: {len(secondary_sources)}")
    lines.append("")
    lines.append("This is a collection aid, not the final analysis. Open primary sources directly before writing final claims.")
    lines.append("")

    lines.append("## Index Page")
    lines.append("")
    lines.extend(format_page(homepage))

    lines.append("## Firsthand AI Digest Items In Window")
    lines.append("")
    for idx, item in enumerate(digest_items, 1):
        published = item.published.isoformat() if item.published else "unknown"
        lines.append(f"### {idx}. {item.title or item.url}")
        lines.append("")
        lines.append(f"- URL: {item.url}")
        lines.append(f"- Type: {item.source_type or source_kind(item.url)}")
        lines.append(f"- Published: {published}")
        if item.summary:
            lines.append(f"- Digest summary: {item.summary[:800]}")
        lines.append("")

    lines.append("## Firsthand AI Digest Detail Pages")
    lines.append("")
    for idx, page in enumerate(detail_pages, 1):
        lines.append(f"### {idx}. {page.title or page.url}")
        lines.append("")
        lines.extend(format_page(page))

    lines.append("## Original Sources")
    lines.append("")
    for idx, page in enumerate(originals, 1):
        lines.append(f"### {idx}. {page.title or page.url}")
        lines.append("")
        lines.append(f"- Type: {source_kind(page.url)}")
        lines.extend(format_page(page))

    if secondary_sources:
        lines.append("## Secondary Source Candidates")
        lines.append("")
        lines.append("These links were discovered from first-layer sources. Use them to reach primary material when the first-layer source is commentary or a link blog.")
        lines.append("")
        for idx, page in enumerate(secondary_sources, 1):
            lines.append(f"### {idx}. {page.title or page.url}")
            lines.append("")
            lines.append(f"- Type: {source_kind(page.url)}")
            lines.extend(format_page(page))

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_page(page: PageInfo) -> list[str]:
    lines = [f"- URL: {page.url}"]
    if page.fetch_error:
        lines.append(f"- Fetch status: limited ({page.fetch_error})")
        lines.append("")
        return lines
    if page.title:
        lines.append(f"- Title: {page.title}")
    if page.published:
        lines.append(f"- Published: {page.published}")
    if page.description:
        lines.append(f"- Description: {page.description}")
    if page.links:
        lines.append("- Links:")
        for link, text in page.links[:20]:
            label = f" - {text}" if text else ""
            lines.append(f"  - {link}{label}")
    if page.text_excerpt:
        lines.append("")
        lines.append("Excerpt:")
        lines.append("")
        lines.append(page.text_excerpt)
    lines.append("")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect ai.prov1dence.top daily report sources.")
    parser.add_argument("--site", default=DEFAULT_SITE, help="Firsthand AI Digest index URL")
    parser.add_argument("--hours", type=int, default=24, help="Intended lookback window for the report")
    parser.add_argument("--output", default="ai-providence-source-pack.md", help="Markdown output path")
    parser.add_argument("--max-detail-pages", type=int, default=20, help="Maximum same-site detail pages to fetch")
    parser.add_argument("--max-original-sources", type=int, default=80, help="Maximum outbound original sources to fetch")
    parser.add_argument("--max-secondary-sources", type=int, default=10, help="Maximum source links discovered from first-layer sources")
    parser.add_argument("--index-timeout", type=int, default=20, help="HTTP timeout for the required Firsthand AI Digest index page")
    parser.add_argument("--timeout", type=int, default=8, help="HTTP timeout per fetched URL")
    parser.add_argument("--workers", type=int, default=8, help="Parallel fetch workers")
    parser.add_argument("--fetch-heavy-hosts", action="store_true", help="Also raw-fetch YouTube/X/LinkedIn/short-link style hosts")
    args = parser.parse_args()

    site = args.site
    until = dt.datetime.now(dt.timezone.utc)
    since = until - dt.timedelta(hours=args.hours)
    metadata_only_hosts = () if args.fetch_heavy_hosts else METADATA_ONLY_HOSTS
    homepage_result = fetch_with_retries(site, timeout=args.index_timeout, attempts=2)
    homepage = parse_page(site, homepage_result)
    if not homepage_result.ok:
        print(f"Failed to fetch {site}: {homepage_result.error}", file=sys.stderr)
        return 1

    digest_items = parse_digest_items(site, homepage_result.text, since, until)
    digest_urls = [item.url for item in digest_items]

    detail_candidates = sorted(homepage.links, key=lambda item: rank_detail_link(item[0], item[1], site), reverse=True)
    detail_urls: list[str] = []
    for url, _ in detail_candidates:
        if rank_detail_link(url, "", site) <= 0:
            continue
        if url not in detail_urls:
            detail_urls.append(url)
        if len(detail_urls) >= args.max_detail_pages:
            break

    detail_pages: list[PageInfo] = []
    original_urls: list[str] = []
    for page in fetch_pages_parallel(detail_urls, args.timeout, args.workers, metadata_only_hosts):
        detail_pages.append(page)
        for link, _ in page.links:
            if not same_host(link, site) and link in digest_urls and link not in original_urls:
                original_urls.append(link)

    if digest_urls:
        original_urls = digest_urls[:]
    elif not original_urls:
        for link, _ in homepage.links:
            if not same_host(link, site) and link not in original_urls:
                original_urls.append(link)

    item_by_url = {item.url: item for item in digest_items}
    original_items = [item_by_url[url] for url in original_urls[: args.max_original_sources] if url in item_by_url]
    missing_item_urls = [url for url in original_urls[: args.max_original_sources] if url not in item_by_url]
    originals = fetch_items_parallel(original_items, args.timeout, args.workers, metadata_only_hosts)
    originals.extend(fetch_pages_parallel(missing_item_urls, args.timeout, args.workers, metadata_only_hosts))

    secondary_urls: list[str] = []
    for page in originals:
        page_host = urllib.parse.urlparse(page.url).netloc
        for link, text in page.links:
            if not is_secondary_candidate(link, text, site, page_host):
                continue
            if link not in original_urls and link not in secondary_urls:
                secondary_urls.append(link)

    secondary_sources: list[PageInfo] = []
    secondary_sources = fetch_pages_parallel(
        secondary_urls[: args.max_secondary_sources],
        args.timeout,
        args.workers,
        metadata_only_hosts,
    )

    output_path = Path(args.output)
    write_report(output_path, site, args.hours, homepage, detail_pages, digest_items, originals, secondary_sources)
    print(
        f"Wrote {output_path} with {len(detail_pages)} detail pages, "
        f"{len(originals)} original sources, and {len(secondary_sources)} secondary sources."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
