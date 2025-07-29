import argparse
from . import tree, list_files, tree_to_json

def main():
    parser = argparse.ArgumentParser(description="A tool to display directory trees or file listings")
    parser.add_argument("path", help="Path to the root directory")
    parser.add_argument("--no-emoji", action="store_true", help="Hide emojis")
    parser.add_argument("--exclude", nargs="*", default=[], help="Names of directories to exclude (partial match)")
    parser.add_argument("--ext", nargs="*", default=[], help="File extensions to filter (e.g., .py, .txt)")
    parser.add_argument("--no-tree", action="store_true", help="Print file paths only (no tree view)")
    parser.add_argument("--json-output", help="Path to save JSON file. If specified, saves tree to JSON.")

    args = parser.parse_args()

    if args.json_output:
        tree_to_json(
            root_dir=args.path,
            save_path=args.json_output,
            ignore_dirs=args.exclude,
            filter_exts=args.ext,
            show_meta=True
        )
        print(f"✅ JSON saved to {args.json_output}")
    elif args.no_tree:
        print(list_files(args.path, ignore_dirs=args.exclude, filter_exts=args.ext))
    else:
        print(tree(args.path, use_emoji=not args.no_emoji, ignore_dirs=args.exclude, filter_exts=args.ext))

if __name__ == "__main__":
    main()