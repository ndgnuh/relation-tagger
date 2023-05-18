# Relation tagger

## Installation

```bash
pip install "git+https://github.com/ndgnuh/relation-tagger"
```

## Run

Start
```bash
relation-tagger
relation-tagger run
```

Start with a dataset
```bash
relation-tagger run --data data.json
```

Update
```bash
relation-tagger update
relation-tagger update --ref <git commit>
```

Create data
```bash
relation-tagger create --o dataset.json sample1.json sample2.json -c 'class1,class2,class3'
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
