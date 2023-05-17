# Relation tagger

## Installation

```bash
pip install "git+https://github.com/ndgnuh/relation-tagger"
```

## Run

Start
```bash
relation-tagger
```

Start with a dataset
```bash
relation-tagger --data data.json
```

Update
```bash
relation-tagger --udate
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
1-9                  | Set node class
0                    | Remove node class
Tab                  | Toggle image preview

Mouse:

Action               | Function
:---                 | :---
Click                | Select node
Ctrl + Click         | Select multiple nodes
Click drag           | Select multiple nodes, discard previous selections
Ctrl + Click drag    | Select multiple nodes, append selections
Right click drag     | Move canvas
Mouse wheel          | Zoom in/out

## Data format

See `data.json` or `label_tool/data.py` for the schema.
