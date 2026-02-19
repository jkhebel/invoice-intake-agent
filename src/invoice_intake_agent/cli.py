import argparse
from .app import run


def main() -> int:
    parser = argparse.ArgumentParser()
    # parser.add_argument("--input", required=False)
    args = parser.parse_args()

    # run(args.input)
    run()
    return 0
