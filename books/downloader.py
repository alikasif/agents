import re
import os
import requests
from urllib.parse import urlparse
from pathlib import Path
from typing import List


def extract_links_from_md(md_path: str) -> List[str]:
    """Extract all http(s) links from a markdown file where the link text starts with 'Chapter '."""
    links = []
    pattern = re.compile(r'\[(Chapter [^\]]+)\]\((https?://[^)]+)\)')
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            for match in pattern.findall(line):
                # match[0] is the link text, match[1] is the url
                links.append((match[0], match[1]))
    return links


def sanitize_filename_from_url(url: str) -> str:
    """Create a safe filename from a URL (chapter name or last path segment)."""
    parsed = urlparse(url)
    # Use last path segment or netloc
    name = Path(parsed.path).stem or parsed.netloc
    # Remove unsafe chars
    name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    if not name:
        name = 'chapter'
    return name + ".pdf"


def download_pdf(url: str, out_path: str):
    """Download a PDF from a URL to the given path."""
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def download_all_chapter_pdfs(md_path: str, out_dir: str = "./books/chapters"):
    """Read the markdown, extract chapter links (only 'Chapter '), download each as a PDF."""
    os.makedirs(out_dir, exist_ok=True)
    links = extract_links_from_md(md_path)
    for link_text, url in links:
        fname = sanitize_filename_from_url(link_text)
        out_path = os.path.join(out_dir, fname)
        print(f"Downloading {link_text}: {url} -> {out_path}")
        try:
            download_pdf(url, out_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")


if __name__ == "__main__":
    md_file = os.path.join(os.path.dirname(__file__), "Agentic Design Patterns.md")
    download_all_chapter_pdfs(md_file)
