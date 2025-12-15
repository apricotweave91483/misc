# clink

`clink.py` is a tiny C “linker” (really: a concatenator) that lets you keep reusable C helper
code in a `C_Utils` folder and then generate a single final `.c` file.

---

## Setup (recommended)

For convenience, alias clink to the Python script in your shell config:
alias clink="python3 /full/path/to/clink.py"

## How it works

Given a command like:

```bash
clink cmp lb main.c -o test.c
```

The script does the following:

1. Any argument that does **not** end in `.c` (and is not `-o`) is treated as a utility name.  
   Example: `cmp` → `cmp.c`

2. Utility files are searched for inside:

```text
~/C_Utils/
```

(The folder name is configurable inside `clink.py`.)

3. The **first** argument that *does* end in `.c` is treated as the main file.

4. All utility files are read first (in the order you typed them),
   then the main file is read last.

5. All `#include ...` lines across every file are collected into a set.
   This removes duplicate includes.

6. The output file is written as:
   - all unique `#include` lines at the top
   - followed by all remaining code lines from each file, in order
   - original `#include` lines are skipped during body writing

7. The output filename defaults to:

```text
_final.c
```

but can be overridden using `-o <filename>`.

---

## Expected folder layout

Example:

```text
~/C_Utils/
    cmp.c
    lb.c

project/
    clink.py
    main.c
```
but really the clink.py script can be stored anywhere

---

## Usage

### Basic

```bash
clink <util1> <util2> ... <main.c>
```

Example:

```bash
clink cmp lb main.c
```

This generates:

```text
_final.c
```

### Custom output name

```bash
clink cmp lb main.c -o test.c
```

---

## Notes 

- `#include` order is **not preserved** (they are stored in a Python set)
- Only the **first** `.c` argument is treated as the main file
- This is pure concatenation, so symbol order matters

---

## Why I made it

- I wanted a place to store data structs / algos for puzzles that needed them , and I wanted to avoid manual copy/paste
