import tkinter as tk
from tkinter import messagebox, filedialog
import os

def parse_tree(tree_str, base_path):
    path_stack = []
    for line in tree_str.strip().splitlines():
        line = line.rstrip()

        # Sanitize line to skip malformed entries
        if not any(c in line for c in ('├', '└', '│', '─')) and '/' not in line and '.' not in line:
            continue

        # Remove tree drawing characters
        stripped = line.lstrip('│├└─ ')
        indent = (len(line) - len(stripped)) // 4

        is_dir = stripped.endswith('/')
        name = stripped.rstrip('/')

        # Validate name
        if not name or any(char in name for char in '*<>?"|'):
            continue  # Skip invalid names

        while len(path_stack) > indent:
            path_stack.pop()

        path_stack.append(name)
        full_path = os.path.join(base_path, *path_stack)

        try:
            if is_dir:
                os.makedirs(full_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    pass
        except Exception as e:
            print(f"Failed to create {full_path}: {e}")

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        base_path_var.set(folder)

def on_create():
    tree_str = text_area.get("1.0", tk.END)
    base_path = base_path_var.get()

    if not base_path:
        messagebox.showwarning("Missing Folder", "Please choose a base folder.")
        return

    if not tree_str.strip():
        messagebox.showwarning("Empty Input", "Please paste a tree structure.")
        return

    try:
        parse_tree(tree_str, base_path)
        messagebox.showinfo("Success", "Filesystem created successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    global root, text_area, base_path_var  # declare global so handlers access

    root = tk.Tk()
    root.title("mktr - Create Filesystem from Tree")

    tk.Label(root, text="Paste Tree Structure:").pack(anchor='w', padx=10, pady=(10, 0))
    text_area = tk.Text(root, width=70, height=20)
    text_area.pack(padx=10, pady=5)

    frame = tk.Frame(root)
    frame.pack(fill='x', padx=10, pady=5)

    base_path_var = tk.StringVar()

    tk.Entry(frame, textvariable=base_path_var, width=50).pack(side='left', expand=True, fill='x')
    tk.Button(frame, text="Choose Folder", command=choose_folder).pack(side='left', padx=5)

    tk.Button(root, text="Create Filesystem", command=on_create).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
