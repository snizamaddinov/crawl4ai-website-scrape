import asyncio
import json
import os
import re
import fnmatch
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter, ContentTypeFilter, URLPatternFilter
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

TARGET_DOMAIN = "ugurokullari.k12.tr"
START_URL = f"https://{TARGET_DOMAIN}/"

MAX_PAGES = 10
MAX_DEPTH = 3

PAGE_TIMEOUT = 60000
DELAY_BEFORE_SCRAPE = 3.0
WAIT_FOR = "css:body"

CONTENT_SELECTOR = "section"

REMOVE_SELECTORS = [
    ".container-fluid",
    ".col-lg-6",
    ".box-5",
    ".box2",
    ".box4",
    ".box5",
    "#homepage_news",
    "nav",
    "header",
    "footer",
    ".breadcrumb",
    "script",
    "style",
    "noscript",
]

SKIP_URL_PATTERNS = [
    "*on-kayit*",
    "*iletisim*",
    "*kvkk*",
    "*login*",
    "*blog*",
    "*okul-kiyafetleri*",
    "*yonetim*",
    "*haber-ve-duyuru*",
    "*ugurlu-olmak*",
    "*okullarimiz*",
    "*.docx*",
    "*.pdf*",
    "*hakkimizda/yonetim*",
    "*basin-odasi"
]

OUTPUT_DIR = "output"
MARKDOWN_DIR = os.path.join(OUTPUT_DIR, "markdown")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "crawl_index.json")


def sanitize_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    
    if not path:
        path = "index"
    
    filename = path.replace("/", "_")
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    
    if not filename.endswith('.md'):
        filename += '.md'
    
    return filename


def ensure_dirs():
    os.makedirs(MARKDOWN_DIR, exist_ok=True)


def should_skip_url(url: str) -> bool:
    for pattern in SKIP_URL_PATTERNS:
        if fnmatch.fnmatch(url, pattern):
            return True
    return False


def clean_html_and_convert_to_markdown(html: str, content_selector: str = None, remove_selectors: list = None) -> str:
    if not html:
        return ""
    
    soup = BeautifulSoup(html, 'html.parser')

    if remove_selectors:
        for selector in remove_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    if content_selector:
        content_elements = soup.select(content_selector)
        if content_elements:
            combined_html = ''.join(str(el) for el in content_elements)
            soup = BeautifulSoup(combined_html, 'html.parser')
        else:
            return ""
    
    markdown_content = md(str(soup), heading_style="ATX", strip=['a'])
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
    markdown_content = markdown_content.strip()

    return markdown_content


async def main():
    ensure_dirs()

    domain_filter = DomainFilter(
        allowed_domains=[TARGET_DOMAIN],
        blocked_domains=[]
    )

    content_type_filter = ContentTypeFilter(allowed_types=["text/html"])

    url_skip_filter = URLPatternFilter(
        patterns=SKIP_URL_PATTERNS,
        reverse=True
    )

    filter_chain = FilterChain([domain_filter, content_type_filter, url_skip_filter])
    
    deep_crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=MAX_DEPTH,
        include_external=False,
        max_pages=MAX_PAGES,
        filter_chain=filter_chain
    )

    config = CrawlerRunConfig(
        deep_crawl_strategy=deep_crawl_strategy,
        scraping_strategy=LXMLWebScrapingStrategy(),
        page_timeout=PAGE_TIMEOUT,
        delay_before_return_html=DELAY_BEFORE_SCRAPE,
        wait_for=WAIT_FOR,
        verbose=True
    )

    print(f"Starting crawl of {START_URL}")
    print(f"Max pages: {'Unlimited' if MAX_PAGES is None else MAX_PAGES}, Max depth: {MAX_DEPTH}")
    print(f"Domain: {TARGET_DOMAIN}")
    print(f"Skip patterns: {len(SKIP_URL_PATTERNS)} patterns (excluded at crawl-time)")

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(url=START_URL, config=config)

        print(f"\nCrawl complete! Fetched {len(results)} pages")
        print("Filtering and processing...")

        output_data = {
            "crawl_info": {
                "start_url": START_URL,
                "target_domain": TARGET_DOMAIN,
                "max_pages": MAX_PAGES,
                "max_depth": MAX_DEPTH,
                "skip_url_patterns": SKIP_URL_PATTERNS,
                "total_pages_fetched": len(results),
                "crawl_timestamp": datetime.now().isoformat()
            },
            "pages": []
        }

        saved_count = 0
        skipped_count = 0

        for i, result in enumerate(results):
            if should_skip_url(result.url):
                skipped_count += 1
                print(f"Skipped (post-filter): {result.url}")
                continue

            filename = sanitize_filename(result.url)
            base_name = filename[:-3]
            final_filename = filename
            file_path = os.path.join(MARKDOWN_DIR, final_filename)

            counter = 1
            while os.path.exists(file_path):
                final_filename = f"{base_name}_{counter}.md"
                file_path = os.path.join(MARKDOWN_DIR, final_filename)
                counter += 1

            raw_html = getattr(result, 'html', '') or ''
            cleaned_markdown = clean_html_and_convert_to_markdown(
                html=raw_html,
                content_selector=CONTENT_SELECTOR,
                remove_selectors=REMOVE_SELECTORS
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"url: {result.url}\n")
                f.write(f"title: {getattr(result, 'title', '')}\n")
                f.write(f"depth: {result.metadata.get('depth', 0)}\n")
                f.write(f"scraped_at: {datetime.now().isoformat()}\n")
                f.write(f"---\n\n")
                f.write(cleaned_markdown)

            page_data = {
                "url": result.url,
                "depth": result.metadata.get('depth', 0),
                "title": getattr(result, 'title', ''),
                "markdown_file": file_path,
                "markdown_file_relative": os.path.join("markdown", final_filename),
                "content_length": len(cleaned_markdown),
                "has_content": len(cleaned_markdown) > 0,
            }
            output_data["pages"].append(page_data)
            saved_count += 1

            status = "✓" if page_data["has_content"] else "✗"
            print(f"  {status} Depth {page_data['depth']}: {result.url}")
            print(f"    → {final_filename} ({len(cleaned_markdown)} chars)")

        output_data["crawl_info"]["total_pages_saved"] = saved_count
        output_data["crawl_info"]["total_pages_skipped"] = skipped_count

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\nJSON index: {OUTPUT_FILE}")
        print(f"Markdown files: {MARKDOWN_DIR}/")
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total fetched: {len(results)}")
        print(f"Saved: {saved_count}")
        print(f"Skipped: {skipped_count}")


if __name__ == "__main__":
    asyncio.run(main())
