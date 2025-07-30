# mktr

Simple Python tool to create a filesystem from a pasted tree structure via a GUI.

## Features

- Paste tree-like structure
- Choose target folder via dialog
- Create corresponding folders and files
- Lightweight Tkinter GUI (no extra dependencies)

## Installation

```bash
pip install mktr
````

## Usage

Run the tool from command line:

```bash
mktr
```

Paste your tree structure into the window, select or enter a base folder, then click "Create Filesystem".

Example tree structure:

```
project/
├── src/
│   ├── main.py
│   └── utils.py
├── README.md
└── setup.py
```

## License

MIT License


