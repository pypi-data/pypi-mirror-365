import argparse
import logging

from pyprojroot import here

from annular.coupling import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_files",
        nargs="*",
        type=str,
        help="Configuration files to run simulations for.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    for config_file in args.config_files:
        main(here(config_file))
