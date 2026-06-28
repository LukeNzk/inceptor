#!/usr/bin/env python3
"""Static blog generator CLI: build / clean / serve / new."""

from __future__ import annotations

import argparse
import http.server
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from functools import partial
from pathlib import Path

import markdown as md_lib
from jinja2 import Environment, FileSystemLoader
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
DIST_DIR = ROOT / "dist"
TEMPLATES_DIR = ROOT / "templates"
POSTS_XML = ROOT / "posts.xml"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    front = text[4:end]
    body = text[end + 5:]
    meta: dict[str, str] = {}
    for line in front.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, body.strip()


def render_markdown(text: str) -> str:
    return md_lib.markdown(
        text,
        extensions=["fenced_code", "codehilite", "tables", "toc"],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": True}
        },
    )


def get_excerpt(html: str) -> str:
    m = re.search(r"<p>(.*?)</p>", html, re.DOTALL)
    return m.group(1) if m else ""


def load_posts() -> list[dict]:
    if not POSTS_XML.exists():
        raise FileNotFoundError("posts.xml not found")
    tree = ET.parse(POSTS_XML)
    posts: list[dict] = []
    for el in tree.getroot().findall("post"):
        file_attr = el.get("file", "")
        slug = el.get("slug", "")
        if not file_attr or not slug:
            raise ValueError("<post> element missing 'file' or 'slug' attribute")
        md_path = POSTS_DIR / file_attr
        if not md_path.exists():
            raise FileNotFoundError(f"Missing post file: {md_path}")
        raw = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        content = render_markdown(body)
        posts.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "date": meta.get("date", ""),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "content": content,
            "excerpt": get_excerpt(content),
        })
    return posts


def build(verbose: bool = False) -> None:
    posts = load_posts()
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    pygments_css = HtmlFormatter(style="monokai").get_style_defs(".highlight")

    DIST_DIR.mkdir(exist_ok=True)
    (DIST_DIR / "posts").mkdir(exist_ok=True)

    ctx = {"pygments_css": pygments_css}

    index_html = env.get_template("index.html").render(posts=posts, site_root="", **ctx)
    (DIST_DIR / "index.html").write_text(index_html, encoding="utf-8")
    if verbose:
        print("  index.html")

    post_tmpl = env.get_template("post.html")
    for post in posts:
        post_dir = DIST_DIR / "posts" / post["slug"]
        post_dir.mkdir(exist_ok=True)
        html = post_tmpl.render(post=post, site_root="../../", **ctx)
        (post_dir / "index.html").write_text(html, encoding="utf-8")
        if verbose:
            print(f"  posts/{post['slug']}/index.html")

    print(f"Built {len(posts)} post(s) → {DIST_DIR}")


def clean() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print(f"Removed {DIST_DIR}")
    else:
        print("Nothing to clean.")


def serve(port: int = 8000) -> None:
    if not DIST_DIR.exists():
        print("No dist/ found — run 'build' first.")
        return
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST_DIR))
    with http.server.HTTPServer(("", port), handler) as httpd:
        print(f"Serving http://localhost:{port}/  (Ctrl+C to stop)")
        httpd.serve_forever()


def new_post(title: str) -> None:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    file_name = f"{slug}.md"
    md_path = POSTS_DIR / file_name
    if md_path.exists():
        print(f"Already exists: {md_path}")
        return
    POSTS_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    md_path.write_text(
        f"---\ntitle: {title}\ndate: {today}\ntags: \n---\n\n# {title}\n\nWrite your post here.\n",
        encoding="utf-8",
    )
    root: ET.Element
    if POSTS_XML.exists():
        root = ET.parse(POSTS_XML).getroot()
    else:
        root = ET.Element("posts")
    el = ET.SubElement(root, "post")
    el.set("file", file_name)
    el.set("slug", slug)
    ET.indent(root, space="  ")
    POSTS_XML.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    print(f"Created: posts/{file_name}")
    print(f"Updated: posts.xml")


def main() -> None:
    parser = argparse.ArgumentParser(prog="build.py", description="Static blog generator")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("build", help="Generate static site in dist/")
    sub.add_parser("clean", help="Delete dist/")
    sp = sub.add_parser("serve", help="Serve dist/ locally")
    sp.add_argument("--port", type=int, default=8000)
    np = sub.add_parser("new", help="Create a new post")
    np.add_argument("title")

    args = parser.parse_args()
    match args.cmd:
        case "build":
            build(verbose=True)
        case "clean":
            clean()
        case "serve":
            serve(args.port)
        case "new":
            new_post(args.title)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
