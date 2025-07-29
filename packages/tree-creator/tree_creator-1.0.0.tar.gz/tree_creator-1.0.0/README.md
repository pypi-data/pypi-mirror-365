以下は、アップロードされた `core.py`、`setup.py` を基に作成した `README.md` の内容です。

---

# 📁 Tree Creator

🌐 言語:  [English version](./README.md) | [日本語はこちら](./README.ja.md)

Create directory and file structures from tree-like text representations — just like the output of the `tree` command.

## ✨ Features

* Parse text-based tree structures and generate corresponding directories and files.
* Dry-run support (simulate without creating files).
* CLI and API support.
* Helpful logging for debugging and auditing.
* Zero external dependencies.

## 📦 Installation

```bash
pip install tree-creator
```

or (for development)

```bash
git clone https://github.com/jack-low/tree-creator
cd tree-creator
pip install -e ".[dev]"
```

## 🚀 Usage

### ✨ Example (Python API)

```python
from tree_creator import TreeCreator

tree_text = '''
project/
├── src/
│   ├── main.py
│   └── utils.py
└── README.md
'''

creator = TreeCreator()
creator.create_from_text(tree_text, base_dir='./my_project')
```

### 💻 CLI
### 🧪 Example using Here Document (EOF)

You can also provide multi-line tree structure input via standard input like this:

```bash
tree-creator -b ./output-dir -d - <<EOF
myapp/
├── index.html
└── static/
    └── style.css
EOF
```

- `-d` enables dry-run mode (no files will actually be created)
- `-b ./output-dir` specifies the target directory
- `-` means the input is read from stdin


```bash
tree-creator tree.txt --base-dir ./my_project
tree-creator tree.txt --dry-run
echo "dir/\n└── file.txt" | tree-creator -
```

#### Options

| Option           | Description                                |
| ---------------- | ------------------------------------------ |
| `-b, --base-dir` | Target base directory (default: `.`)       |
| `-e, --encoding` | Encoding for input file (default: `utf-8`) |
| `-d, --dry-run`  | Simulate without file creation             |
| `-v, --verbose`  | Verbose log output                         |

## 📄 Tree Format

A valid tree structure should follow the conventions similar to the `tree` command output:

```
project/
├── src/
│   ├── main.py
│   └── utils.py
└── README.md
```

* Directories end with `/`
* Indentation and characters: `├──`, `└──`, `│`

## 🧪 Development

Run tests with:

```bash
pytest
```

Code formatting and checks:

```bash
black .
flake8 .
mypy tree_creator
```

## 📜 License

MIT License © [Jack3Low](mailto:xapa.pw@gmail.com)

## 🔗 Links

* [Source Code](https://github.com/jack-low/tree-creator)
* [Issue Tracker](https://github.com/jack-low/tree-creator/issues)
* [Documentation](https://github.com/jack-low/tree-creator#readme)


