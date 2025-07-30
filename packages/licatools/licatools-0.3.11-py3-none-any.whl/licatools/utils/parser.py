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
from argparse import ArgumentParser

# ---------------------
# Third-party libraries
# ---------------------

import astropy.units as u

from lica.validators import vfile, vdir, vnat
from lica.lab import BENCH
from lica.lab.photodiode import PhotodiodeModel
from lica.lab.ndfilters import NDFilter

# ------------------------
# Own modules and packages
# ------------------------

from .validators import vecsvfile, vfigext
from .mpl.plotter import Marker, LineStyle

# ------------------------
# Plotting Related parsers
# ------------------------


def title(title: str, purpose: str) -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        nargs="+",
        default=title,
        help=f"{purpose} title",
    )
    return parser


def titles(title: str, purpose: str) -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-t",
        "--title",
        dest="titles",
        type=str,
        nargs="+",
        default=title,
        help=f"{purpose} title",
    )
    return parser


def xlabel() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-xl",
        "--x-label",
        type=str,
        nargs="+",
        default=None,
        help="Plot X label",
    )
    return parser


def xlabels() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-xl",
        "--x-label",
        dest="x_labels",
        type=str,
        nargs="+",
        default=None,
        help="Plot X labels",
    )
    return parser


def ylabel() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-yl",
        "--y-label",
        type=str,
        nargs="+",
        default=None,
        help="Plot Y label",
    )
    return parser


def ylabels() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-yl",
        "--y-label",
        dest="y_labels",
        type=str,
        nargs="+",
        default=None,
        help="Plot Y labels",
    )
    return parser


def marker() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-m",
        "--marker",
        type=Marker,
        default=None,
        help="Plot line marker, defaults to %(default)s",
    )
    return parser


def markers() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-m",
        "--marker",
        dest="markers",
        type=Marker,
        nargs="+",
        default=None,
        help="Plot line markers, defaults to %(default)s",
    )
    return parser


def linstyl() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ls",
        "--line-style",
        type=LineStyle,
        default=None,
        help="Plot line style, defaults to %(default)s",
    )
    return parser


def linstyls() -> ArgumentParser:
    """Common options for plotting"""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ls",
        "--line-style",
        dest="line_styles",
        type=LineStyle,
        nargs="+",
        default=None,
        help="Plot line styles, defaults to %(default)s",
    )
    return parser


def label(purpose: str) -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-l",
        "--label",
        type=str,
        nargs="+",
        help=f"Label for {purpose} purposes",
    )
    return parser


def labels(purpose: str) -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-l",
        "--label",
        dest="labels",
        type=str,
        nargs="+",
        help=f"One or more labels for {purpose} purposes",
    )
    return parser


def ncols() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-nc",
        "--num-cols",
        type=vnat,
        default=None,
        help="Number of plotting Axes",
    )
    return parser


def xcn() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-xcn",
        "--x-col-num",
        type=vnat,
        metavar="<N>",
        default=1,
        help="X column number (1-based), defaults to %(default)d",
    )
    return parser


def ycn() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ycn",
        "--y-col-num",
        type=vnat,
        metavar="<N>",
        default=2,
        help="Y column number (1-based), defaults to %(default)d",
    )
    return parser


def ycns() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ycn",
        "--y-col-num",
        type=vnat,
        nargs="+",
        metavar="<N>",
        default=None,
        help="Y column numbers (1-based) in CSV/ECSV, defaults to %(default)d",
    )
    return parser


def auxlines() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--changes",
        action="store_true",
        default=False,
        help="Plot Monocromator filter changes (default: %(default)s)",
    )
    parser.add_argument(
        "--lines",
        default=False,
        action="store_true",
        help="Connect dots with lines (default: %(default)s)",
    )
    return parser


def percent() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-%",
        "--percent",
        action="store_true",
        default=False,
        help="Y axis as a percentage (default: %(default)s)",
    )
    return parser


def logy() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--log-y",
        action="store_true",
        default=False,
        help="Y axis in logaritmic scale (default: %(default)s)",
    )
    return parser


# ----------------------
# Building Table parsers
# ----------------------


def ifile() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-i",
        "--input-file",
        type=vfile,
        required=True,
        metavar="<File>",
        help="CSV/ECSV input file",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default=",",
        help="CSV column delimiter. (defaults to %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--columns",
        type=str,
        default=None,
        nargs="+",
        metavar="<NAME>",
        help="Optional ordered list of CSV column names, if necessary (default %(default)s)",
    )
    return parser


def ifiles() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-i",
        "--input-file",
        type=vecsvfile,
        required=True,
        nargs="+",
        metavar="<File>",
        help="CSV/ECSV input files",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default=",",
        help="CSV column delimiter. (defaults to %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--columns",
        type=str,
        default=None,
        nargs="+",
        metavar="<NAME>",
        help="Optional ordered list of CSV column names, if necessary (default %(default)s)",
    )
    return parser


def xlim() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-xll",
        "--x-low-limit",
        dest="x_low",
        type=int,
        metavar="<LOW>",
        default=BENCH.WAVE_START.value,
        help="X axis lower limit, defaults to %(default)s",
    )
    parser.add_argument(
        "-xhl",
        "--x-high-limit",
        dest="x_high",
        type=int,
        metavar="<HIGH>",
        default=BENCH.WAVE_END.value,
        help="X axis upper limit, defaults to %(default)s",
    )
    parser.add_argument(
        "-xu",
        "--x-limits-unit",
        type=u.Unit,
        metavar="<Unit>",
        default=u.nm,
        help="X limits units (ie. nm, A/W, etc.), defaults to %(default)s",
    )
    return parser


def lica() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--lica",
        action="store_true",
        help="Trims wavelength to LICA Optical Bench range [350nm-1050nm]",
    )
    return parser


### ONLY USED IN THE CASE OF  SINGLE COLUMN PLOTS
def resample() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-r",
        "--resample",
        choices=tuple(range(1, 11)),
        type=vnat,
        metavar="<N nm>",
        default=None,
        help="Resample wavelength to N nm step size, defaults to %(default)s",
    )
    return parser


def resol() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=tuple(range(1, 11)),
        default=1,
        metavar="<N nm>",
        help="Resolution (defaults to %(default)d nm)",
    )
    return parser


# -------------
# Other parsers
# -------------


def folder() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-d",
        "--directory",
        type=vdir,
        required=True,
        metavar="<Dir>",
        help="ECSV input directory",
    )
    return parser


def idir() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-i",
        "--input-dir",
        type=vdir,
        default=os.getcwd(),
        metavar="<Dir>",
        help="Input ECSV directory (default %(default)s)",
    )
    return parser


def odir() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-o",
        "--output-dir",
        type=vdir,
        default=os.getcwd(),
        metavar="<Dir>",
        help="Output ECSV directory (default %(default)s)",
    )
    return parser


def glob() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-fp",
        "--file-pattern",
        type=str,
        default="*.ecsv",
        help="Input files glob pattern (default %(default)s)",
    )
    return parser


def tag() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-g",
        "--tag",
        type=str,
        metavar="<tag>",
        default="A",
        help="File tag. Sensor/filter tags should match a photodiode tag, defaults value = '%(default)s'",
    )
    return parser


def photod() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        choices=[model for model in PhotodiodeModel],
        default=PhotodiodeModel.OSI,
        help="Photodiode model, defaults to %(default)s",
    )
    parser.add_argument(
        "-p",
        "--photod-file",
        type=vfile,
        required=True,
        metavar="<File>",
        help="CSV photodiode input file",
    )
    return parser


def save() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save processing file to ECSV",
    )
    return parser


def savefig() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-sf",
        "--save-figure-path",
        type=vfigext,
        default=None,
        metavar="<File>",
        help=".png or .pdf figure file path, defaults to %(default)s",
    )
    return parser


def dpifig() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-sd",
        "--save-figure-dpi",
        type=int,
        default=None,
        help="Saved figure resolution in DPI %(default)s",
    )
    return parser


def ndf() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-n",
        "--ndf",
        type=NDFilter,
        choices=NDFilter,
        default=None,
        help="Neutral Density Filter model, defaults to %(default)s",
    )
    return parser
