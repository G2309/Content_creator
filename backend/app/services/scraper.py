from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PWTimeout
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

MAX_PAGES_TO_VISIT = 8
PAGE_TIMEOUT_MS = 18000
SETTLE_DELAY_MS = 700
MIN_PAGE_TEXT_LENGTH = 80
MAX_TOTAL_CHARS = 50000

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

NOISE_TAGS = (
    "script", "style", "noscript", "iframe", "svg", "form",
    "header", "footer", "nav",
)

PRIORITY_PATH_HINTS = (
    "about", "sobre-nosotros", "sobre", "quienes-somos", "nosotros", "company",
    "servicios", "services", "productos", "products", "soluciones", "solutions",
    "precios", "pricing", "plans", "planes",
    "contacto", "contact",
    "industrias", "industries", "casos", "clientes", "customers",
)

PRIORITY_KEYWORDS = (
    "about", "sobre", "quien", "nosotros", "company",
    "servic", "product", "soluc", "precio", "pricing",
    "industr", "casos", "cliente", "customer",
)


@dataclass
class ScrapedPage:
    url: str
    title: str
    text: str


@dataclass
class ScrapeResult:
    origin_url: str
    site_title: str = ""
    meta_description: str = ""
    pages: list[ScrapedPage] = field(default_factory=list)

    @property
    def combined_text(self) -> str:
        chunks: list[str] = []
        if self.site_title:
            chunks.append(f"SITIO: {self.site_title}")
        if self.meta_description:
            chunks.append(f"META DESCRIPTION: {self.meta_description}")
        for p in self.pages:
            chunks.append(f"\n=== PÁGINA: {p.url}")
            if p.title:
                chunks.append(f"TÍTULO: {p.title}")
            chunks.append(p.text)
        return "\n".join(chunks)[:MAX_TOTAL_CHARS]


class ScraperError(Exception):
    pass


def normalize_url(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise ScraperError("URL vacía")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if not parsed.netloc:
        raise ScraperError("URL inválida")
    if parsed.scheme not in ("http", "https"):
        raise ScraperError("Solo se aceptan URLs http o https")
    return raw


def _canonical_key(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return f"{parsed.netloc}{path}".lower()


def _looks_priority(url: str) -> bool:
    lower = url.lower()
    return any(kw in lower for kw in PRIORITY_KEYWORDS)


def _is_same_site(url: str, base_netloc: str) -> bool:
    try:
        netloc = urlparse(url).netloc.lower()
    except Exception:
        return False
    base = base_netloc.lower()
    return netloc == base or netloc.endswith("." + base) or base.endswith("." + netloc)


def _is_useful_link(url: str) -> bool:
    if not url:
        return False
    url = url.split("#")[0]
    lower = url.lower()
    bad_ext = (
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
        ".zip", ".rar", ".tar", ".gz",
        ".mp4", ".mp3", ".mov", ".avi",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".css", ".js",
    )
    if any(lower.endswith(ext) for ext in bad_ext):
        return False
    bad_proto = ("mailto:", "tel:", "javascript:", "data:", "whatsapp:")
    if any(lower.startswith(bp) for bp in bad_proto):
        return False
    return True


def _parse_html(html: str, current_url: str) -> tuple[str, str, str, list[str]]:
    soup = BeautifulSoup(html, "lxml")

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()
    if not meta_desc:
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and og_desc.get("content"):
            meta_desc = og_desc["content"].strip()

    links: list[str] = []
    for a in soup.find_all("a", href=True):
        absolute = urljoin(current_url, a["href"])
        if _is_useful_link(absolute):
            links.append(absolute)

    for tag in soup(NOISE_TAGS):
        tag.decompose()

    main_blocks = soup.find_all(["main", "article"])
    if main_blocks:
        text_source = "\n".join(b.get_text(separator="\n", strip=True) for b in main_blocks)
    else:
        text_source = soup.get_text(separator="\n", strip=True)

    text = re.sub(r"[ \t]+", " ", text_source)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, meta_desc, text.strip(), links


async def _fetch_page(context, url: str) -> tuple[str, str, str, list[str]]:
    page = await context.new_page()
    try:
        try:
            await page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
        except PWTimeout:
            raise ScraperError(f"Tiempo agotado al cargar {url}")

        await page.wait_for_timeout(SETTLE_DELAY_MS)
        html = await page.content()
        return _parse_html(html, url)
    finally:
        await page.close()


async def scrape_site(raw_url: str) -> ScrapeResult:
    url = normalize_url(raw_url)
    base_parsed = urlparse(url)
    base_netloc = base_parsed.netloc
    base_origin = f"{base_parsed.scheme}://{base_netloc}"

    result = ScrapeResult(origin_url=url)
    visited: set[str] = set()

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
        except Exception as e:
            logger.exception("No se pudo iniciar Chromium")
            raise ScraperError("No se pudo iniciar el navegador del scraper") from e

        try:
            ctx = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 800},
                locale="es-ES",
                java_script_enabled=True,
            )

            try:
                title, meta_desc, text, links = await _fetch_page(ctx, url)
            except ScraperError:
                raise
            except Exception as e:
                logger.exception("Fallo al cargar la URL principal")
                raise ScraperError("No se pudo cargar la página principal") from e

            visited.add(_canonical_key(url))
            result.site_title = title
            result.meta_description = meta_desc
            if text and len(text) >= MIN_PAGE_TEXT_LENGTH:
                result.pages.append(ScrapedPage(url=url, title=title, text=text))

            candidates: list[str] = []
            seen_candidates: set[str] = set()

            for hint in PRIORITY_PATH_HINTS:
                cand = urljoin(base_origin, "/" + hint)
                key = _canonical_key(cand)
                if key not in seen_candidates and key not in visited:
                    seen_candidates.add(key)
                    candidates.append(cand)

            internal_links = [l for l in links if _is_same_site(l, base_netloc)]
            internal_links.sort(key=lambda u: (0 if _looks_priority(u) else 1, len(u)))

            for link in internal_links:
                key = _canonical_key(link)
                if key in seen_candidates or key in visited:
                    continue
                seen_candidates.add(key)
                candidates.append(link)

            for cand in candidates:
                if len(result.pages) >= MAX_PAGES_TO_VISIT:
                    break
                key = _canonical_key(cand)
                if key in visited:
                    continue
                visited.add(key)
                try:
                    p_title, _, p_text, _ = await _fetch_page(ctx, cand)
                    if p_text and len(p_text) >= MIN_PAGE_TEXT_LENGTH:
                        result.pages.append(ScrapedPage(url=cand, title=p_title, text=p_text))
                except Exception as e:
                    logger.debug("Saltando %s: %s", cand, e)
                    continue
        finally:
            await browser.close()

    return result
