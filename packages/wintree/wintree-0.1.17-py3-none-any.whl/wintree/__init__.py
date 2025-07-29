import os
import datetime
from typing import List


def tree(
    root_dir: str = ".",
    use_emoji: bool = True,
    ignore_dirs: List[str] = [],
    filter_exts: List[str] = [],
):
    """
    Display the directory structure as a tree.

    Args:
        root_dir (str, optional): Path to the root directory to display. Defaults to "." (current directory).
        use_emoji (bool, optional): If True, display emojis for folders and files. Defaults to True.
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the tree. Defaults to [].
        filter_exts (List[str], optional): List of file extensions to include. If empty, all files are included.

    Example:
        ```
        print(tree(root_dir="/path/to/project", use_emoji=True, ignore_dirs=[".git", "__pycache__"]))
        ```
    """
    __root_validation(root_dir)
    root_str = f"{'📂 ' if use_emoji else ''}root: {root_dir}"
    tree = __make_tree(
        root_dir, use_emoji=use_emoji, exclude_dirs=ignore_dirs, filter_exts=filter_exts
    )
    return (
        f"{root_str}\n{tree}"
        if tree
        else f"{root_str}\n(No files or directories found)"
    )


def tree_cli(
    root_dir: str = ".",
    use_emoji: bool = True,
    ignore_dirs: List[str] = [],
    filter_exts: List[str] = [],
):
    """
    Display the directory structure as a tree.

    Args:
        root_dir (str, optional): Path to the root directory to display. Defaults to "." (current directory).
        use_emoji (bool, optional): If True, display emojis for folders and files. Defaults to True.
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the tree. Defaults to [].
        filter_exts (List[str], optional): List of file extensions to include. If empty, all files are included.

    Example:
        ```
        print(tree(root_dir="/path/to/project", use_emoji=True, ignore_dirs=[".git", "__pycache__"]))
        ```
    """
    __root_validation(root_dir)
    print(f"{'📂 ' if use_emoji else ''}root: {root_dir}")
    tree = __print_tree(
        root_dir, use_emoji=use_emoji, exclude_dirs=ignore_dirs, filter_exts=filter_exts
    )
    if tree == "Permission denied":
        print(tree)
        return
    if tree == "No files or directories found":
        print("No files or directories found")


def tree_to_json(
    root_dir: str = ".",
    save_path: str = "",
    ignore_dirs: List[str] = [],
    filter_exts: List[str] = [],
    show_meta: bool = False,
):
    """
    Generate a JSON representation of the directory structure.

    Args:
        root_dir (str, optional): Path to the root directory to display. Defaults to "." (current directory).
        save_path (str, optional): Path to save the JSON file. If not provided, defaults to "<root_dir>_tree.json".
        filter_exts (List[str], optional): List of file extensions to include. If empty, all files are included.
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the tree. Defaults to [].
        show_meta (bool, optional): If True, include file size and last modified time in the JSON output. Defaults to False.

    Example:
        ```
        tree_to_json(root_dir="/path/to/project", ignore_dirs=[".git", "__pycache__"])
        ```
    """
    __root_validation(root_dir)
    if not save_path:
        dir_name = os.path.basename(os.path.abspath(root_dir))
        save_path = os.path.join(os.path.abspath(root_dir), f"{dir_name}_tree.json")

    elif not save_path.endswith(".json"):
        raise ValueError("Save path must end with '.json'.")

    if not os.path.exists(os.path.dirname(os.path.abspath(save_path))):
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    import json

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            __make_tree_json(
                root_dir,
                exclude_dirs=ignore_dirs,
                exclude_files=[os.path.basename(save_path)],
                filter_exts=filter_exts,
                show_meta=show_meta,
            ),
            f,
            ensure_ascii=False,
            indent=4,
        )
    return __make_tree_json(
        root_dir,
        exclude_dirs=ignore_dirs,
        exclude_files=[os.path.basename(save_path)],
        filter_exts=filter_exts,
        show_meta=show_meta,
    )


def tree_to_dict(
    root_dir: str = ".",
    ignore_dirs: List[str] = [],
    filter_exts: List[str] = [],
    show_meta: bool = False,
):
    """
    Generate a dictionary representation of the directory structure.

    Args:
        root_dir (str, optional): Path to the root directory to display. Defaults to "." (current directory).
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the tree. Defaults to [].
        filter_exts (List[str], optional): List of file extensions to include. If empty, all files are included.

    Example:
        ```
        tree_to_dict(root_dir="/path/to/project", ignore_dirs=[".git", "__pycache__"])
        ```
    """
    __root_validation(root_dir)
    return __make_tree_json(
        root_dir, exclude_dirs=ignore_dirs, filter_exts=filter_exts, show_meta=show_meta
    )


def list_files(
    root_dir: str = ".",
    ignore_dirs: List[str] = [],
    filter_exts: List[str] = [],
    absolute_paths: bool = False,
):
    """
    Recursively list all files under the specified directory, excluding specified directories.

    Args:
        root_dir (str, optional): Path to the root directory to search. Defaults to "." (current directory).
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the search. Defaults to [].
        filter_exts (List[str], optional): List of file extensions to include. If empty, all files are included.
        absolute_paths (bool, optional): If True, return absolute paths; otherwise, return relative paths. Defaults to False.

    Example:
        ```
        print(list_files(root_dir="/path/to/project", ignore_dirs=[".git", "__pycache__"]))
        ```
    """
    __root_validation(root_dir)
    return __list_files_recursive(
        root_dir, root_dir, ignore_dirs, filter_exts, absolute_paths
    )


def __make_tree(
    current_dir, prefix="", use_emoji=True, exclude_dirs=None, filter_exts=None
):
    output_str = ""

    if exclude_dirs is None:
        exclude_dirs = []
    if filter_exts is None:
        filter_exts = []

    try:
        entries = sorted(os.listdir(current_dir))
        entries = sorted(
            entries,
            key=lambda e: (
                not os.path.isdir(os.path.join(current_dir, e)),
                e.lower(),
            ),
        )
    except PermissionError:
        return ""

    entries = [
        e
        for e in entries
        if not any(ex in os.path.join(current_dir, e) for ex in exclude_dirs)
    ]

    for idx, entry in enumerate(entries):
        full_path = os.path.join(current_dir, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        icon_folder = "📁 " if use_emoji else ""
        icon_file = "📄 " if use_emoji else ""

        if os.path.isdir(full_path):
            output_str += f"{prefix}{connector}{icon_folder}{entry}/\n"
            extension = "    " if idx == len(entries) - 1 else "│   "
            output_str += __make_tree(
                full_path, prefix + extension, use_emoji, exclude_dirs, filter_exts
            )
        else:
            _, ext = os.path.splitext(entry)
            if filter_exts and ext.lower() not in [e.lower() for e in filter_exts]:
                continue
            output_str += f"{prefix}{connector}{icon_file}{entry}\n"

    return output_str


def __print_tree(
    current_dir, prefix="", use_emoji=True, exclude_dirs=None, filter_exts=None
):
    if exclude_dirs is None:
        exclude_dirs = []
    if filter_exts is None:
        filter_exts = []

    try:
        entries = sorted(os.listdir(current_dir))
        entries = sorted(
            entries,
            key=lambda e: (
                not os.path.isdir(os.path.join(current_dir, e)),
                e.lower(),
            ),
        )
    except PermissionError:
        return "Permission denied"
    
    if not entries:
        return "No files or directories found"

    entries = [
        e
        for e in entries
        if not any(ex in os.path.join(current_dir, e) for ex in exclude_dirs)
    ]

    for idx, entry in enumerate(entries):
        full_path = os.path.join(current_dir, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        icon_folder = "📁 " if use_emoji else ""
        icon_file = "📄 " if use_emoji else ""

        if os.path.isdir(full_path):
            print(f"{prefix}{connector}{icon_folder}{entry}/")
            extension = "    " if idx == len(entries) - 1 else "│   "
            __print_tree(
                full_path, prefix + extension, use_emoji, exclude_dirs, filter_exts
            )
        else:
            _, ext = os.path.splitext(entry)
            if filter_exts and ext.lower() not in [e.lower() for e in filter_exts]:
                continue
            print(f"{prefix}{connector}{icon_file}{entry}")


def __list_files_recursive(
    current_dir, root_dir, exclude_dirs=None, filter_exts=None, absolute_paths=False
):
    output_str = ""

    if exclude_dirs is None:
        exclude_dirs = []
    if filter_exts is None:
        filter_exts = []

    try:
        entries = sorted(os.listdir(current_dir))
        entries = sorted(
            entries,
            key=lambda e: (
                not os.path.isdir(os.path.join(current_dir, e)),
                e.lower(),
            ),
        )
    except PermissionError:
        return

    for entry in entries:
        full_path = os.path.join(current_dir, entry)

        if any(ex in full_path for ex in exclude_dirs):
            continue

        if os.path.isdir(full_path):
            child = __list_files_recursive(
                full_path, root_dir, exclude_dirs, filter_exts, absolute_paths
            )
            output_str += child if child else ""
        else:
            _, ext = os.path.splitext(entry)
            if filter_exts and ext.lower() not in [e.lower() for e in filter_exts]:
                continue

            file_path = os.path.abspath(full_path)
            if not absolute_paths:
                file_path = os.path.relpath(file_path, root_dir)

            output_str += file_path + "\n"

    return output_str


def __make_tree_json(
    current_dir,
    exclude_dirs=None,
    exclude_files=None,
    filter_exts=None,
    show_meta=False,
):
    output_dict = {
        "name": os.path.basename(current_dir),
        "type": "directory",
        "children": [],
    }

    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    if filter_exts is None:
        filter_exts = []

    try:
        entries = sorted(os.listdir(current_dir))
        entries = sorted(
            entries,
            key=lambda e: (
                not os.path.isdir(os.path.join(current_dir, e)),
                e.lower(),
            ),
        )
    except PermissionError:
        return None

    for entry in entries:
        full_path = os.path.join(current_dir, entry)

        if any(ex in full_path for ex in exclude_dirs):
            continue

        if entry in exclude_files:
            continue

        if os.path.isdir(full_path):
            child = __make_tree_json(
                full_path, exclude_dirs, exclude_files, filter_exts, show_meta
            )
            if child:
                output_dict["children"].append(child)
        else:
            _, ext = os.path.splitext(entry)
            if filter_exts and ext.lower() not in [e.lower() for e in filter_exts]:
                continue

            file_dict = {"name": entry, "type": "file"}

            if show_meta:
                try:
                    size = os.path.getsize(full_path)
                    mtime = os.path.getmtime(full_path)
                    timestamp = datetime.datetime.fromtimestamp(mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    file_dict["size"] = size
                    file_dict["updated"] = timestamp
                except OSError:
                    pass

            output_dict["children"].append(file_dict)

    return output_dict


def __root_validation(root_dir):
    if not os.path.exists(root_dir):
        raise ValueError(f"Root directory '{root_dir}' does not exist.")
    if not os.path.isdir(root_dir):
        raise ValueError(f"Root path '{root_dir}' is not a directory.")

if __name__ == "__main__":
    tree_cli()