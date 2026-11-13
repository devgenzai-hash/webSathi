"""
Web crawler service — crawls a URL and indexes every page as a document.
Phase 1 feature.
"""
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import CrawlJob, Document
from app.services.rag_service import process_document_for_rag


async def start_crawl(db: Session, job_id: str, root_url: str, site_id: str) -> None:
    """Background task: crawl root_url and index all discovered pages."""
    job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
    if not job:
        return

    job.status = "running"
    db.commit()

    try:
        visited: set[str] = set()
        to_visit: list[tuple[str, int]] = [(root_url, 0)]
        parsed_root = urlparse(root_url)
        pages_crawled = 0

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            while to_visit and pages_crawled < settings.CRAWLER_MAX_PAGES:
                url, depth = to_visit.pop(0)
                if url in visited:
                    continue
                visited.add(url)

                try:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        continue
                    if "html" not in resp.headers.get("content-type", ""):
                        continue

                    html = resp.text
                    text = _extract_text_from_html(html)
                    if not text.strip():
                        continue

                    title = _extract_title(html) or url
                    content_bytes = text.encode("utf-8")

                    doc = Document(
                        site_id=site_id,
                        filename=f"{title[:80]} [{url}]",
                        file_type="txt",
                        file_size=len(content_bytes),
                        file_path=f"crawled:{url}",
                        status="processing",
                    )
                    db.add(doc)
                    db.commit()
                    db.refresh(doc)

                    try:
                        chunk_count = await process_document_for_rag(
                            document_id=doc.id,
                            site_id=site_id,
                            file_path=doc.file_path,
                            file_type="txt",
                            content=content_bytes,
                        )
                        doc.status = "ready"
                        doc.chunk_count = chunk_count 
                    except Exception as e:
                        doc.status = "failed"
                        doc.error_message = str(e)[:500]

                    db.commit()
                    pages_crawled += 1

                    if depth < settings.CRAWLER_MAX_DEPTH:
                        links = _extract_links(html, parsed_root.netloc, url)
                        for link in links:
                            if link not in visited:
                                to_visit.append((link, depth + 1))

                except Exception:
                    continue

        job.status = "done"
        job.pages_crawled = pages_crawled
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)[:500]
        job.completed_at = datetime.utcnow()
        db.commit()


def _extract_text_from_html(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()


def _extract_title(html: str) -> Optional[str]:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def _extract_links(html: str, allowed_netloc: str, current_url: str) -> list[str]:
    try:
        from scrapling.fetchers import StealthyFetcher
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        print(soup)
        links: list[str] = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            full_url = urljoin(current_url, href)
            parsed = urlparse(full_url)
            if parsed.netloc != allowed_netloc:
                continue
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean not in links:
                links.append(clean)
        return links[:100]
    except Exception:
        return []
