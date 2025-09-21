import re
import os
import requests

def extract_links_with_titles(md_file):
    """Extract titles + URLs from markdown file."""
    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Matches like: [Chapter 1: Prompt Chaining](https://docs...)
    pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)')
    return pattern.findall(text)

def sanitize_filename(name):
    """Clean text to be a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_-]+', '_', name).strip('_')

def download_google_doc_as_pdf(url, output_path):
    """Download Google Doc as PDF using export endpoint."""
    match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        return False
    doc_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"

    response = requests.get(export_url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved: {output_path}")
        return True
    else:
        print(f"❌ Failed: {url} (status {response.status_code})")
        return False

def download_all_from_md(md_file, base_dir="books"):
    links = extract_links_with_titles(md_file)

    for title, url in links:
        # Decide subfolder
        title_lower = title.lower()
        if "chapter" in title_lower:
            folder = os.path.join(base_dir, "chapters")
        elif "appendix" in title_lower:
            folder = os.path.join(base_dir, "appendix")
        elif "conclusion" in title_lower:
            folder = os.path.join(base_dir, "conclusion")
        elif "glossary" in title_lower:
            folder = os.path.join(base_dir, "glossary")
        elif "index" in title_lower:
            folder = os.path.join(base_dir, "index")
        else:
            folder = os.path.join(base_dir, "misc")

        os.makedirs(folder, exist_ok=True)

        if "docs.google.com/document" in url:
            filename = sanitize_filename(title) + ".pdf"
            output_path = os.path.join(folder, filename)
            download_google_doc_as_pdf(url, output_path)
        else:
            print(f"⚠️ Skipping non-Google Doc link: {url}")

# Example usage
download_all_from_md("books\Agentic Design Patterns.md")
