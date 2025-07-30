#!/usr/bin/env python3
"""
PLTools 命令行入口点
"""

import sys
import argparse
from . import gittools
from . import __version__


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog="pltools", description="PLTools - Python 开发工具集合"
    )

    parser.add_argument(
        "--version", 
        action="version", 
        version=f"PLTools {__version__}"
    )
    parser.add_argument("--set-git-local-proxy", action="store_true")
    parser.add_argument("--unset-git-local-proxy", action="store_true")

    args = parser.parse_args()

    if args.set_git_local_proxy:
        gittools.set_git_local_proxy()
    elif args.unset_git_local_proxy:
        gittools.unset_git_local_proxy()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
