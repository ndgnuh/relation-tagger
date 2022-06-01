from spade_label_tool.state import create_state, State
import pandas as pd
from lenses import bind


def main():
    state = create_state()
    print(state.data.get())
    print(type(state))
    df = pd.read_csv("site/data-275.csv")
    state = bind(state.data.set(df))
    print(type(state))


if __name__ == "__main__":
    main()
