#!/usr/bin/env python3

from __future__ import annotations

import argparse

from inceptor import build, clean, new_post, serve


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
