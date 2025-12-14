# mac_texter

A small **macOS-only command-line tool** for sending Messages texts using GUI automation.

## requirements

- macOS
- Python 3
- `pyautogui`
- Accessibility permissions enabled for your terminal app

This script is intended to be run from a **Python virtual environment (venv)**.  

You should install dependencies using the venv’s `pip3` and reference the venv’s `python3` binary in the shebang.

## setup (Recommended: Python venv)

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies **using the venv pip**:
```bash
pip3 install pyautogui
```

At the top of the script, set the shebang to the **venv python binary**:
```bash
#!/full/path/to/venv/bin/python3
```

Make the script executable:
```bash
chmod +x texter
```

## usage

```bash
./texter {name} {other_name} ... -MSG "your message here"
```

## example

```bash
./texter Alice Bob -MSG "Running late, be there soon"
```

this will:
1. open Spotlight
2. launch the Messages app
3. create new conversations for each provided name
4. send the provided message

## notes

- macOS only
- fragile by nature (GUI automation depends on timing and UI state)
- assumes:
  - spotlight is enabled
  - messages app responds normally
  - contact names are resolvable by Messages
