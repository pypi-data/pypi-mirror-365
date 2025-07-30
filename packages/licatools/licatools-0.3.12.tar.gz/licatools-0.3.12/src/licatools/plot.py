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

import logging
from math import ceil, sqrt

# Typing hints
from argparse import ArgumentParser, Namespace


# ---------------------
# Third-party libraries
# ---------------------

from astropy import visualization
from lica.cli import execute

# ------------------------
# Own modules and packages
# ------------------------

from ._version import __version__
from .utils.mpl.plotter import (
    Director,
    SingleTableColumnBuilder,
    SingleTableColumnsBuilder,
    SingleTablesColumnBuilder,
    SingleTablesColumnsBuilder,
    SingleTablesMixedColumnsBuilder,
    MultiTablesColumnBuilder,
    MultiTablesColumnsBuilder,
    TableFromFile,
    TablesFromFiles,
    BasicPlotter,
)


from .utils import parser as prs

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__)

# -----------------
# Matplotlib styles
# -----------------


# -------------------
# Auxiliary functions
# -------------------


# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================


def cli_single_table_column(args: Namespace):
    tb_builder = TableFromFile(
        path=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=args.resample,
        lica_trim=args.lica,
    )
    builder = SingleTableColumnBuilder(
        builder=tb_builder,
        title=args.title,
        xlabel=args.x_label,
        ylabel=args.y_label,
        legend=args.label,
        marker=args.marker,
        linestyle=args.line_style,
    )
    director = Director(builder)

    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    log.info("YC = %s", ycns_grp)
    with visualization.quantity_support():
        with visualization.quantity_support():
            plotter = BasicPlotter(
                xcn=xcn,
                ycns_grp=ycns_grp,
                tables=tables,
                titles=titles,
                xlabels=xlabels,
                ylabels=ylabels,
                legends_grp=legends_grp,
                markers_grp=markers_grp,
                linestyles_grp=linestyles_grp,
                changes=args.changes,
                percent=args.percent,
                linewidth=1 if args.lines else 0,
                nrows=1,
                ncols=1,
                save_path=args.save_figure_path,
                save_dpi=args.save_figure_dpi,
                log_y=args.log_y,
            )
            plotter.plot()


def cli_single_table_columns(args: Namespace):
    tb_builder = TableFromFile(
        path=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=None,
        lica_trim=args.lica,
    )
    builder = SingleTableColumnsBuilder(
        builder=tb_builder,
        title=args.title,
        xlabel=args.x_label,
        ylabel=args.y_label,
        legends=args.labels,
        markers=args.markers,
        linestyles=args.line_styles,
    )
    director = Director(builder)
    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    with visualization.quantity_support():
        plotter = BasicPlotter(
            xcn=xcn,
            ycns_grp=ycns_grp,
            tables=tables,
            titles=titles,
            xlabels=xlabels,
            ylabels=ylabels,
            legends_grp=legends_grp,
            markers_grp=markers_grp,
            linestyles_grp=linestyles_grp,
            changes=args.changes,
            percent=args.percent,
            linewidth=1 if args.lines else 0,
            nrows=1,
            ncols=1,
            save_path=args.save_figure_path,
            save_dpi=args.save_figure_dpi,
            log_y=args.log_y,
            # markers_type: EnumType = Marker
        )
        plotter.plot()


def cli_single_tables_column(args: Namespace):
    tb_builder = TablesFromFiles(
        paths=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=args.resample,
        lica_trim=args.lica,
    )
    builder = SingleTablesColumnBuilder(
        builder=tb_builder,
        title=args.title,
        xlabel=args.x_label,
        ylabel=args.y_label,
        legends=args.labels,
        markers=args.markers,
        linestyles=args.line_styles,
    )
    director = Director(builder)
    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    with visualization.quantity_support():
        plotter = BasicPlotter(
            xcn=xcn,
            ycns_grp=ycns_grp,
            tables=tables,
            titles=titles,
            xlabels=xlabels,
            ylabels=ylabels,
            legends_grp=legends_grp,
            markers_grp=markers_grp,
            linestyles_grp=linestyles_grp,
            changes=args.changes,
            percent=args.percent,
            linewidth=1 if args.lines else 0,
            nrows=1,
            ncols=1,
            save_path=args.save_figure_path,
            save_dpi=args.save_figure_dpi,
            log_y=args.log_y,
            # markers_type: EnumType = Marker
        )
        plotter.plot()


def cli_single_tables_columns(args: Namespace):
    tb_builder = TablesFromFiles(
        paths=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=None,
        lica_trim=args.lica,
    )
    builder = SingleTablesColumnsBuilder(
        builder=tb_builder,
        title=args.title,
        xlabel=args.x_label,
        ylabel=args.y_label,
        legends=args.labels,
        markers=args.markers,
        linestyles=args.line_styles,
    )
    director = Director(builder)
    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    with visualization.quantity_support():
        plotter = BasicPlotter(
            xcn=xcn,
            ycns_grp=ycns_grp,
            tables=tables,
            titles=titles,
            xlabels=xlabels,
            ylabels=ylabels,
            legends_grp=legends_grp,
            markers_grp=markers_grp,
            linestyles_grp=linestyles_grp,
            changes=args.changes,
            percent=args.percent,
            linewidth=1 if args.lines else 0,
            nrows=1,
            ncols=1,
            save_path=args.save_figure_path,
            save_dpi=args.save_figure_dpi,
            log_y=args.log_y,
            # markers_type: EnumType = Marker
        )
        plotter.plot()


def cli_single_tables_mixed(args: Namespace):
    tb_builder = TablesFromFiles(
        paths=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=None,
        lica_trim=args.lica,
    )
    builder = SingleTablesMixedColumnsBuilder(
        builder=tb_builder,
        title=args.title,
        xlabel=args.x_label,
        ylabel=args.y_label,
        legends=args.labels,
        markers=args.markers,
        linestyles=args.line_styles,
    )
    director = Director(builder)
    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    with visualization.quantity_support():
        plotter = BasicPlotter(
            xcn=xcn,
            ycns_grp=ycns_grp,
            tables=tables,
            titles=titles,
            xlabels=xlabels,
            ylabels=ylabels,
            legends_grp=legends_grp,
            markers_grp=markers_grp,
            linestyles_grp=linestyles_grp,
            changes=args.changes,
            percent=args.percent,
            linewidth=1 if args.lines else 0,
            nrows=1,
            ncols=1,
            save_path=args.save_figure_path,
            save_dpi=args.save_figure_dpi,
            log_y=args.log_y,
            # markers_type: EnumType = Marker
        )
        plotter.plot()


def cli_multi_tables_column(args: Namespace):
    tb_builder = TablesFromFiles(
        paths=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=args.resample,
        lica_trim=args.lica,
    )
    builder = MultiTablesColumnBuilder(
        builder=tb_builder,
        titles=args.titles,
        xlabels=args.x_labels,
        ylabels=args.y_labels,
        legend=args.labels,
        marker=args.markers,
        linestyle=args.line_styles,
    )
    director = Director(builder)
    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    ncols = args.num_cols if args.num_cols is not None else int(ceil(sqrt(len(tables))))
    nrows = int(ceil(len(tables) / ncols))
    with visualization.quantity_support():
        plotter = BasicPlotter(
            xcn=xcn,
            ycns_grp=ycns_grp,
            tables=tables,
            titles=titles,
            xlabels=xlabels,
            ylabels=ylabels,
            legends_grp=legends_grp,
            markers_grp=markers_grp,
            linestyles_grp=linestyles_grp,
            changes=args.changes,
            percent=args.percent,
            linewidth=1 if args.lines else 0,
            nrows=nrows,
            ncols=ncols,
            save_path=args.save_figure_path,
            save_dpi=args.save_figure_dpi,
            log_y=args.log_y,
            # markers_type: EnumType = Marker
        )
        plotter.plot()


def cli_multi_tables_columns(args: Namespace):
    tb_builder = TablesFromFiles(
        paths=args.input_file,
        delimiter=args.delimiter,
        columns=args.columns,
        xcn=args.x_col_num,
        ycn=args.y_col_num,
        xlow=args.x_low,
        xhigh=args.x_high,
        xlunit=args.x_limits_unit,
        resolution=None,
        lica_trim=args.lica,
    )
    builder = MultiTablesColumnsBuilder(
        builder=tb_builder,
        titles=args.titles,
        xlabels=args.x_labels,
        ylabels=args.y_labels,
        legends=args.labels,
        markers=args.markers,
        linestyles=args.line_styles,
    )
    director = Director(builder)
    elements = director.build_elements()
    log.debug(elements)
    xcn, ycns_grp, tables, titles, xlabels, ylabels, legends_grp, markers_grp, linestyles_grp = (
        elements
    )
    ncols = args.num_cols if args.num_cols is not None else int(ceil(sqrt(len(tables))))
    nrows = int(ceil(len(tables) / ncols))
    with visualization.quantity_support():
        plotter = BasicPlotter(
            xcn=xcn,
            ycns_grp=ycns_grp,
            tables=tables,
            titles=titles,
            xlabels=xlabels,
            ylabels=ylabels,
            legends_grp=legends_grp,
            markers_grp=markers_grp,
            linestyles_grp=linestyles_grp,
            changes=args.changes,
            percent=args.percent,
            linewidth=1 if args.lines else 0,
            nrows=nrows,
            ncols=ncols,
            save_path=args.save_figure_path,
            save_dpi=args.save_figure_dpi,
            log_y=args.log_y,
            # markers_type: EnumType = Marker
        )
        plotter.plot()


def add_args(parser: ArgumentParser):
    sub_s = parser.add_subparsers(required=True)
    p_s = sub_s.add_parser("single", help="Single Axes plot")
    p_m = sub_s.add_parser("multi", help="Multiple Axes plot")

    # ================
    # Single Axes case
    # ================

    sub_s_t = p_s.add_subparsers(required=True)

    # ---------------------------------------------
    # Single Axes, Single Table, Single Column case
    # ---------------------------------------------
    p_s_t = sub_s_t.add_parser("table", help="Single Axes, single table plot")
    sub_s_t_c = p_s_t.add_subparsers(required=True)
    par_s_t_c = sub_s_t_c.add_parser(
        "column",
        parents=[
            prs.ifile(),
            prs.logy(),
            prs.xlim(),
            prs.resample(),
            prs.lica(),
            prs.xcn(),
            prs.ycn(),
            prs.title(None, "plotting"),
            prs.xlabel(),
            prs.ylabel(),
            prs.label("plotting"),
            prs.auxlines(),
            prs.percent(),
            prs.marker(),
            prs.linstyl(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Single Axes, single table, single column plot",
    )
    par_s_t_c.set_defaults(func=cli_single_table_column)

    # ------------------------------------------------
    # Single Axes, Single Table, Multiple Columns case
    # ------------------------------------------------
    par_s_t_cc = sub_s_t_c.add_parser(
        "columns",
        parents=[
            prs.ifile(),
            prs.logy(),
            prs.xlim(),
            prs.lica(),
            prs.xcn(),
            prs.ycns(),
            prs.title(None, "Plotting"),
            prs.xlabel(),
            prs.ylabel(),
            prs.labels("plotting"),  # Column labels
            prs.auxlines(),
            prs.percent(),
            prs.markers(),
            prs.linstyls(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Single Axes, single table, multiple columns plot",
    )
    par_s_t_cc.set_defaults(func=cli_single_table_columns)

    p_s_tt = sub_s_t.add_parser("tables", help="Single Axes, multiple tables plot")
    sub_s_tt = p_s_tt.add_subparsers(required=True)

    # ------------------------------------------------
    # Single Axes, Multiple Tables, Single Column case
    # ------------------------------------------------
    par_s_tt_c = sub_s_tt.add_parser(
        "column",
        parents=[
            prs.ifiles(),
            prs.logy(),
            prs.xlim(),
            prs.resample(),
            prs.lica(),
            prs.xcn(),
            prs.ycn(),
            prs.title(None, "plotting"),
            prs.xlabel(),
            prs.ylabel(),
            prs.labels("plotting"),
            prs.auxlines(),
            prs.percent(),
            prs.markers(),
            prs.linstyls(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Single Axes, multiple tables, single column plot",
    )
    par_s_tt_c.set_defaults(func=cli_single_tables_column)

    # ---------------------------------------------------
    # Single Axes, Multiple Tables, Multiple Columns case
    # ---------------------------------------------------
    par_s_tt_cc = sub_s_tt.add_parser(
        "columns",
        parents=[
            prs.ifiles(),
            prs.xlim(),
            prs.logy(),
            prs.lica(),
            prs.xcn(),
            prs.ycns(),
            prs.title(None, "Plotting"),
            prs.xlabel(),
            prs.ylabel(),
            prs.labels("plotting"),  # Column labels
            prs.auxlines(),
            prs.percent(),
            prs.markers(),
            prs.linstyls(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Single Axes, multiple tables, multiple columns plot",
    )
    par_s_tt_cc.set_defaults(func=cli_single_tables_columns)

    # ---------------------------------------------------
    # Single Axes, Multiple Tables, Multiple Columns case
    # ---------------------------------------------------
    par_s_tt_cx = sub_s_tt.add_parser(
        "mixed",
        parents=[
            prs.ifiles(),
            prs.xlim(),
            prs.logy(),
            prs.lica(),
            prs.xcn(),
            prs.ycns(),
            prs.title(None, "Plotting"),
            prs.xlabel(),
            prs.ylabel(),
            prs.labels("plotting"),  # Column labels
            prs.auxlines(),
            prs.percent(),
            prs.markers(),
            prs.linstyls(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Single Axes, multiple tables, mixed 1 column/table  plot",
    )
    par_s_tt_cx.set_defaults(func=cli_single_tables_mixed)

    # =============
    # Multiple Axes
    # =============

    sub_m_t = p_m.add_subparsers(required=True)

    p_m_tt = sub_m_t.add_parser("tables", help="Mulitple Axes, multiple tables plot")
    sub_m_tt_c = p_m_tt.add_subparsers(required=True)

    # ---------------------------------------------------
    # Multiplea Axes, Multiple Tables, Single Column case
    # ---------------------------------------------------
    par_m_tt_c = sub_m_tt_c.add_parser(
        "column",
        parents=[
            prs.ncols(),
            prs.ifiles(),
            prs.logy(),
            prs.xlim(),
            prs.lica(),
            prs.xcn(),
            prs.ycn(),
            prs.titles(None, "Plotting"),
            prs.xlabels(),
            prs.ylabels(),
            prs.labels("plotting"),
            prs.resample(),
            prs.auxlines(),
            prs.percent(),
            prs.markers(),
            prs.linstyls(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Mulitple Axes, multiple tables, single column plot",
    )
    par_m_tt_c.set_defaults(func=cli_multi_tables_column)

    # ------------------------------------------------------
    # Multiplea Axes, Multiple Tables, Multiple Columns case
    # ------------------------------------------------------
    par_m_tt_cc = sub_m_tt_c.add_parser(
        "columns",
        parents=[
            prs.ncols(),
            prs.ifiles(),
            prs.logy(),
            prs.xlim(),
            prs.lica(),
            prs.xcn(),
            prs.ycns(),
            prs.titles(None, "Plotting"),
            prs.xlabels(),
            prs.ylabels(),
            prs.labels("plotting"),  # Column labels
            prs.auxlines(),
            prs.percent(),
            prs.markers(),
            prs.linstyls(),
            prs.savefig(),
            prs.dpifig(),
        ],
        help="Mulitple Axes, multiple tables, multiple columns plot",
    )
    par_m_tt_cc.set_defaults(func=cli_multi_tables_columns)


# ================
# MAIN ENTRY POINT
# ================


def cli_plot(args):
    args.func(args)


def main():
    execute(
        main_func=cli_plot,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description="Plot CSV/ECSV files",
    )
