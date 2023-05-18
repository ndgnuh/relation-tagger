import json
from argparse import ArgumentParser
from .app import main as main_gui
from .data import Sample, Dataset


def main_update(args):
    from subprocess import run

    remote = "https://github.com/ndgnuh/relation-tagger"
    ref = args.ref or ""
    # ref = "@92ad8964504909be753a4bd771854cec1c853515"
    run(["pip", "install", f"git+{remote}{ref}"])


def main_create(args):

    # Classes
    classes = args.classes.split(",")
    classes = [cls.strip() for cls in classes]
    classes = [cls for cls in classes if len(cls) > 0]

    # Create samples
    samples = []
    for input_ in args.inputs:
        with open(input_, "r") as fp:
            sample = json.load(fp)
        samples.append(sample)

    # Create and save dataset
    dataset = dict(path=args.output, classes=classes, samples=samples)
    dataset = Dataset.from_dict(dataset)
    dataset.save()


def main():
    mapping = {
        None: main_gui,
        "update": main_update,
        "run": main_gui,
        "create": main_create
    }

    parser: ArgumentParser = ArgumentParser()
    action = parser.add_subparsers(dest="action")

    run_parser = action.add_parser("run")
    run_parser.add_argument("--data", dest="data", default=None)
    run_parser.add_argument("--font-size", dest="font_size", type=int, default=16)

    update_parser = action.add_parser("update")
    update_parser.add_argument("--ref")

    create_parser = action.add_parser("create")
    create_parser.add_argument("--output", "-o", required=True)
    create_parser.add_argument("--classes", "-c", required=True, help="Delimiter = ','")
    create_parser.add_argument("inputs", nargs="+")

    args = parser.parse_args()
    if args.action is None:
        args = parser.parse_args(["run"])
    mapping[args.action](args)


if __name__ == "__main__":
    main()
