---
title: Hello World
date: 2026-06-28
tags: python, static-site, programming
---

# Hello World

Welcome to **blog-inceptor** — a minimal static blog generator written in Python. No Node.js, no frameworks, no CMS. Just Markdown, Jinja2 templates, and clean HTML.

## How it works

Posts are written in Markdown with front matter and listed in `posts.xml`. The build command converts them to static HTML pages ready for GitHub Pages.

```xml
<posts>
  <post file="hello-world.md" slug="hello-world" />
</posts>
```

## CLI usage

```bash
python build.py build        # generate dist/
python build.py serve        # local preview at localhost:8000
python build.py new "Title"  # scaffold a new post
python build.py clean        # remove dist/
```

## Code highlighting

Python, JavaScript, Go, Rust, Bash, and C/C++ are all highlighted automatically via Pygments:

```python
from pathlib import Path

def load_post(slug: str) -> str:
    path = Path("posts") / f"{slug}.md"
    return path.read_text(encoding="utf-8")
```

```go
func greet(name string) string {
    return fmt.Sprintf("Hello, %s!", name)
}
```

```rust
fn main() {
    println!("Hello, world!");
}
```

## What's next?

Run `python build.py new "Your Post Title"` to write your first post.
