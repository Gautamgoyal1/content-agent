"""Web page fetcher and article text extractor."""

import re
from typing import Any
import httpx
from bs4 import BeautifulSoup

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False


class PageFetcher:
    """Fetches web pages and extracts readable clean text."""

    def __init__(self, timeout: float = 10.0, user_agent: str | None = None):
        self.timeout = timeout
        self.headers = {
            "User-Agent": user_agent
            or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def fetch_text(self, url: str) -> dict[str, Any]:
        """Fetch a URL and return extracted title, readable text, and metadata."""
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return {
                        "url": url,
                        "success": False,
                        "status_code": resp.status_code,
                        "title": "",
                        "text": "",
                        "error": f"HTTP {resp.status_code}",
                    }

                html = resp.text

                # Use trafilatura if available
                extracted_text = ""
                if HAS_TRAFILATURA:
                    try:
                        extracted_text = trafilatura.extract(html, include_links=False, include_images=False) or ""
                    except Exception:
                        extracted_text = ""

                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else ""

                if not extracted_text:
                    # Fallback to BeautifulSoup clean text extraction
                    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                        tag.decompose()
                    extracted_text = soup.get_text(separator="\n")
                    extracted_text = re.sub(r"\n\s*\n+", "\n\n", extracted_text).strip()

                return {
                    "url": url,
                    "success": True,
                    "status_code": resp.status_code,
                    "title": title or "Untitled Document",
                    "text": extracted_text[:5000],
                    "error": None,
                }
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "status_code": 0,
                "title": "",
                "text": "",
                "error": str(e),
            }
