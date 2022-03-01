import os
import pickle
import sys
import pandas as pd
sys.path.append(os.getcwd())

if len(sys.argv) < 3:
    print("USAGE:")
    print(f"\t{sys.argv[0]} <session file.pkl> <labels.txt>")
    sys.exit(0)


session_file = sys.argv[1]
with open(session_file, 'rb') as f:
    labels = pickle.load(f).labels
    labels = '\n'.join(labels)

with open(sys.argv[2], 'w', encoding='utf-8') as f:
    f.write(labels)
