import os
import pickle
import sys
sys.path.append(os.getcwd())

if len(sys.argv) < 3:
    print("USAGE:")
    print(f"\t{sys.argv[0]} <session file.pkl> <output.csv>")
    sys.exit(0)

session_file = sys.argv[1]
with open(session_file, 'rb') as f:
    data = pickle.load(f).data

if data is None:
    print("This session has no data")


def pcall(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        print(e, type(e))
        return None


def default(a, b):
    if a is None:
        return b
    else:
        return a


def adj_info(i, g):
    print(f"data point: {i}")
    return g.adj


for c in data.columns:
    if c.startswith('Unnamed'):
        data = default(pcall(data.drop, c, axis=1), data)

data = default(pcall(data.drop, 'rel_g', axis=1), data)
data = default(pcall(data.drop, 'rel_s', axis=1), data)
data = default(pcall(data.drop, 'img_bbox_hashes', axis=1), data)

print('columns:', list(data.columns))


print("---------- rel g -------------")
data['rel_g'] = [adj_info(i, g)
                 for (i, g) in enumerate(data['graph_g'])]
print("---------- rel s -------------")
data['rel_s'] = [adj_info(i, g)
                 for (i, g) in enumerate(data['graph_s'])]
print("---------- save --------------")
output = sys.argv[2]
data.to_csv(output)
print(f"File saved to {output}")
