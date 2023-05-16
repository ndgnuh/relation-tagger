# Relation tagger

## Installation

```bash
pip install "git+https://github.com/ndgnuh/spade-label-tool@1fadc1cf1764e84b5645347a4250483cee2a63d1"
```

## Run

```bash
relation-tagger
relation-tagger --data data.json
```

## Shortcuts

Keyboard:

Key                  | Function
:---                 | :---
Ctrl + s             | Save dataset
f                    | Zoom to full view
s                    | Link selected nodes
r                    | Delete links between selected nodes
a                    | Previous sample
d                    | Next sample

Mouse:

Action               | Function
:---                 | :---
Click                | Select node
Ctrl + Shift + Click | Select multiple nodes
Click drag           | Select multiple nodes
Right click drag     | Move canvas
Mouse wheel          | Zoom in/out

## Data format

See `data.json` or `label_tool/data.py` for the schema.
