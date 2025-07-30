# mktr

Simple Python tool to create a filesystem from a pasted tree structure in current working directory via a GUI.

Use cases include:

- Quickly scaffold project directories
- Reproduce predefined file layouts
- Automate template-based setups

## Features

- Paste a tree-like folder structure
- Create corresponding folders and files in the **current working directory**
- Lightweight Tkinter GUI — no external dependencies
- CLI entry point: just run `mktr` after installation

## Installation

```bash
pip install mktr
````

## Usage

From your terminal:

```bash
mktr
```

Then paste a structure like this into the GUI:

```css
project/
├── src/
│   ├── main.py
│   └── utils.py
├── README.md
└── setup.py
```
Click "Create Filesystem" — and the structure will be created in your current working directory.

## License

MIT License


