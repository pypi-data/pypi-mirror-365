# 📁🌳 wintree

[![PyPI Downloads](https://static.pepy.tech/badge/wintree)](https://pepy.tech/projects/wintree)

This library was born out of the limitations of the default Windows tree command.
`wintree` is a Python library that displays the directory structure in a tree format for any specified path.
It can be easily used from the command line and supports features like emoji-based visual tree rendering and directory exclusion.
Additionally, it can output the tree structure as JSON, making it suitable for integration with GUI applications.

## 🔋 Install

```bash
pip install wintree
```

## 🚀 Usage

### 📚️ As a Library

```py
import wintree

print(wintree.tree())
```

```bash
# sample output
📂 root: .
├── 📄 .gitignore
├── 📄 README.md
├── 📄 pyproject.toml
├── 📁 src/
│   ├── 📁 assets/
│   │   ├── 📄 icon.png
│   │   └── 📄 splash_android.png
│   └── 📄 main.py
└── 📁 storage/
    ├── 📁 data/
    └── 📁 temp/
```

With arguments:

```py
from wintree import tree

print(tree(root_dir="/path/to/project", use_emoji=True, ignore_dirs=[".git", "__pycache__"], filter_exts=[".py",".txt"]))
```

| Argument    | Type      | Description                                                                                         |
| ----------- | --------- | --------------------------------------------------------------------------------------------------- |
| root_dir    | str       | Path to the root directory to start displaying the tree. Default is the current directory "."       |
| use_emoji   | bool      | Whether to use emojis in the tree view. If True, adds icons to folders and files.                   |
| ignore_dirs | List[str] | List of directory names to exclude from the tree (partial match). Example: [".git", "node_modules"] |
| filter_ext  | List[str] | File extensions to include. Example: [".py", "txt"]                                                 |

Get or save as JSON

```py
# Get as a dictionary
data = wintree.tree_to_dict(show_meta=True)

# Save as a JSON file
wintree.tree_to_json(root_dir="path/to/project" ,save_path="path/to/project_tree.json")
```

You can also list file paths vertically as relative or absolute paths from the root directory, instead of using a tree structure.

```py
import wintree

print(wintree.list_files())
```

### ⚙️ Usage from CLI

```bash
wintree /path/to/project --exclude .git __pycache__
```

#### Options

| Option        | Description                                                         |
| ------------- | ------------------------------------------------------------------- |
| path          | Path to the root directory                                          |
| --no-emoji    | Disable emoji display                                               |
| --exclude     | Specify directory names to exclude (partial match, space-separated) |
| --ext         | File extensions to include                                          |
| --no-tree     | List absolute paths instead of a tree structure                     |
| --abs         | Output absolute file paths                                          |
| --json-output | Path to save the file hierarchy in                                  |
| --show-meta   | Include timestamp and file size in JSON output                      |

## 📌 Features

- Emoji-based tree view for better visibility
- Flexible exclusion of target directories
- Supports Windows/macOS/Linux
- Pure Python, no external dependencies

## 🧪 For Developers

This library can also be used as a base for directory visualization tools. Integration with GUI tools or IDE plugins is also possible.

## 📄 License

MIT License

# 🌐 Language

- [English](./README.en.md)
- [日本語](./README.ja.md)
