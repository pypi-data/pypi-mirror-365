# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) 2021
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import os
import glob
import logging
from argparse import Namespace

# ---------------------
# Third-party libraries
# ---------------------

from lica.cli import execute
from lica.lab import BENCH
from lica.lab.ndfilters import NDFilter

# ------------------------
# Own modules and packages
# ------------------------

from ._version import __version__
from .utils import processing
from .utils import parser as prs

# ----------------
# Module constants
# ----------------

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__)

# -----------------
# Matplotlib styles
# -----------------

# ------------------
# Auxiliary fnctions
# ------------------

# --------------------------------------------------
# Python API
#
# The Python API can be used within Jupyter Notebook
# --------------------------------------------------


def process(dir_path: str, save_flag: bool, ndf: NDFilter) -> None:
    log.info("Classifying files in directory %s", dir_path)
    dir_iterable = glob.iglob(os.path.join(dir_path, "*.ecsv"))
    photodiode_dict, filter_dict = processing.classify(dir_iterable)
    filter_dict = processing.passive_process(photodiode_dict, filter_dict, ndf)
    if save_flag:
        processing.save(filter_dict, dir_path)


def photodiode(
    photod_path: str,
    model: str,
    tag: str,
    title: str | None = None,
    label: str | None = None,
    x_low: int = BENCH.WAVE_START,
    x_high: int = BENCH.WAVE_END,
) -> None:
    """Returns the path of the newly created ECSV"""
    log.info("Converting to an Astropy Table: %s", photod_path)
    x_low, x_high = min(x_low, x_high), max(x_low, x_high)
    return processing.photodiode_ecsv(
        path=photod_path, model=model, title=title, label=label, tag=tag, x_low=x_low, x_high=x_high
    )


def filters(
    input_path: str,
    tag: str = "",
    title: str | None = None,
    label: str | None = None,
    x_low: int = BENCH.WAVE_START,
    x_high: int = BENCH.WAVE_END,
) -> None:
    """Returns the path of the newly created ECSV"""
    log.info("Converting to an Astropy Table: %s", input_path)
    return processing.filter_ecsv(
        path=input_path, label=label, title=title, tag=tag, x_low=x_low, x_high=x_high
    )


def one_filter(
    input_path: str,
    photod_path: str,
    model: str,
    label: str,
    title: str,
    tag: str,
    x_low: int,
    x_high: int,
    ndf: NDFilter,
) -> str:
    x_low, x_high = min(x_low, x_high), max(x_low, x_high)
    tag = tag or processing.random_tag()
    processing.photodiode_ecsv(
        path=photod_path, model=model, title=None, label=None, tag=tag, x_low=x_low, x_high=x_high
    )
    result = processing.filter_ecsv(
        path=input_path, label=label, title=title, tag=tag, x_low=x_low, x_high=x_high
    )
    dir_path = os.path.dirname(input_path)
    just_name = processing.name_from_file(input_path)
    log.info("Classifying files in directory %s", dir_path)
    dir_iterable = glob.iglob(os.path.join(dir_path, "*.ecsv"))
    photodiode_dict, filter_dict = processing.classify(dir_iterable, just_name)
    processing.review(photodiode_dict, filter_dict)
    filter_dict = processing.passive_process(photodiode_dict, filter_dict, ndf)
    processing.save(filter_dict, dir_path)
    return result


# -----------------------
# AUXILIARY MAIN FUNCTION
# -----------------------


def cli_process(args: Namespace) -> None:
    process(args.directory, args.save, args.ndf)


def cli_photodiode(args: Namespace) -> None:
    title = " ".join(args.title) if args.title is not None else None
    label = " ".join(args.title) if args.title is not None else None
    photodiode(
        photod_path=args.photod_file,
        model=args.model,
        tag=args.tag,
        title=title,
        label=label,
        x_low=args.x_low,
        x_high=args.x_high,
    )


def cli_filters(args: Namespace) -> None:
    label = " ".join(args.label) if args.label else ""
    filters(
        input_path=args.input_file,
        tag=args.tag,
        title=None,
        label=label,
        x_low=args.x_low,
        x_high=args.x_high,
    )


def cli_one_filter(args: Namespace) -> None:
    label = " ".join(args.label) if args.label else ""
    one_filter(
        input_path=args.input_file,
        photod_path=args.photod_file,
        model=args.model,
        label=label,
        title=None,
        tag=args.tag,
        x_low=args.x_low,
        x_high=args.x_high,
        ndf=args.ndf,
    )


def cli_review(args: Namespace):
    log.info("Reviewing files in directory %s", args.directory)
    dir_iterable = glob.iglob(os.path.join(args.directory, "*.ecsv"))
    photodiode_dict, filter_dict = processing.classify(dir_iterable)
    processing.review(photodiode_dict, filter_dict)


# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================


def add_args(parser):
    subparser = parser.add_subparsers(dest="command")
    parser_one = subparser.add_parser(
        "one",
        parents=[
            prs.photod(),
            prs.ifile(),
            prs.label("metadata"),
            prs.tag(),
            prs.xlim(),
            prs.ndf(),
        ],
        help="Process one CSV filter file with one CSV photodiode file",
    )
    parser_one.set_defaults(func=cli_one_filter)

    parser_classif = subparser.add_parser("classif", help="Classification commands")
    parser_passive = subparser.add_parser(
        "process", parents=[prs.folder(), prs.save(), prs.ndf()], help="Process command"
    )
    parser_passive.set_defaults(func=cli_process)

    subsubparser = parser_classif.add_subparsers(dest="subcommand")
    parser_photod = subsubparser.add_parser(
        "photod",
        parents=[
            prs.photod(),
            prs.tag(),
            prs.xlim(),
            prs.title(None, "Plotting"),
            prs.label("plotting"),
        ],
        help="photodiode subcommand",
    )
    parser_photod.set_defaults(func=cli_photodiode)
    parser_filter = subsubparser.add_parser(
        "filter",
        parents=[prs.ifile(), prs.label("metadata"), prs.tag(), prs.xlim()],
        help="filter subcommand",
    )
    parser_filter.set_defaults(func=cli_filters)
    parser_review = subsubparser.add_parser(
        "review", parents=[prs.folder()], help="review classification subcommand"
    )
    parser_review.set_defaults(func=cli_review)


# ================
# MAIN ENTRY POINT
# ================


def cli_main(args: Namespace) -> None:
    args.func(args)


def main():
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description="Filters spectral response",
    )
