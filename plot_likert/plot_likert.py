"""
Plot Likert-style data from Pandas using Matplotlib

Initially based on code from Austin Cory Bart
https://stackoverflow.com/a/41384812


Note:
the data must be strings
for a float: scores.applymap(int).applymap(str)
"""


import logging
import typing
from warnings import warn
from textwrap import wrap

import numpy as np
import pandas as pd


try:
    import matplotlib.axes
    import matplotlib.pyplot as plt
except RuntimeError as err:
    logging.error(
        "Couldn't import matplotlib, likely because this package is running in an environment that doesn't support it (i.e., without a graphical output). See error for more information."
    )
    raise err

from plot_likert.scales import Scale
import plot_likert.colors as colors
import plot_likert.interval as interval_helper

HIDE_EXCESSIVE_TICK_LABELS = True
PADDING_LEFT = 0.05  # fraction of the total width to use as padding


def plot_counts(
    counts: pd.DataFrame,
    scale: Scale,
    plot_percentage: bool = False,
    colors: colors.Colors = colors.default,
    figsize=None,
    xtick_interval: typing.Optional[int] = None,
) -> matplotlib.axes.Axes:
    # Pad each row/question from the left, so that they're centered around the middle (Neutral) response
    scale_middle = len(scale) // 2

    if scale_middle == len(scale) / 2:
        middles = counts.iloc[:, 0:scale_middle].sum(axis=1)
    else:
        middles = (
            counts.iloc[:, 0:scale_middle].sum(axis=1)
            + counts.iloc[:, scale_middle] / 2
        )

    padding_left = PADDING_LEFT * counts.sum(axis="columns").max()
    center = middles.max() + padding_left

    padding_values = (middles - center).abs()
    padded_counts = pd.concat([padding_values, counts], axis=1)
    # Hide the padding row from the legend
    padded_counts = padded_counts.rename({0: ""}, axis=1)

    # Reverse rows to keep the questions in order
    # (Otherwise, the plot function shows the last one at the top.)
    reversed_rows = padded_counts.iloc[::-1]

    # Start putting together the plot
    ax = reversed_rows.plot.barh(stacked=True, color=colors, figsize=figsize)

    # Draw center line
    center_line = plt.axvline(center, linestyle="--", color="black", alpha=0.5)
    center_line.set_zorder(-1)

    # Compute and show x labels
    max_width = int(round(padded_counts.sum(axis=1).max()))
    if xtick_interval is None:
        num_ticks = ax.xaxis.get_tick_space()
        interval = interval_helper.get_interval_for_scale(num_ticks, max_width)
    else:
        interval = xtick_interval

    right_edge = max_width - center
    right_labels = np.arange(interval, right_edge + interval, interval)
    right_values = center + right_labels
    left_labels = np.arange(0, center + 1, interval)
    left_values = center - left_labels
    xlabels = np.concatenate([left_labels, right_labels])
    xvalues = np.concatenate([left_values, right_values])

    xlabels = [int(l) for l in xlabels if round(l) == l]

    # Ensure tick labels don't exceed number of participants
    # (or, in the case of percentages, 100%) since that looks confusing
    if HIDE_EXCESSIVE_TICK_LABELS:
        # Labels for tick values that are too high are hidden,
        # but the tick mark itself remains displayed.
        total_max = counts.sum(axis="columns").max()
        xlabels = ["" if label > total_max else label for label in xlabels]

    if plot_percentage:
        xlabels = [str(label) + "%" if label != "" else "" for label in xlabels]

    ax.set_xticks(xvalues)
    ax.set_xticklabels(xlabels)
    if plot_percentage is True:
        ax.set_xlabel("Percentage of Responses")
    else:
        ax.set_xlabel("Number of Responses")

    # Control legend
    plt.legend(bbox_to_anchor=(1.05, 1))

    return ax


def likert_counts(
    df: pd.DataFrame, scale: Scale, label_max_width=30, drop_zeros=False
) -> pd.DataFrame:
    """
    Given a dataframe of Likert-style responses, returns a count of each response,
    validating them against the provided scale.
    """

    def validate(value):
        if (value not in scale) and (not pd.isna(value)):
            raise ValueError(f"{value} is not in the scale")

    df.applymap(validate)

    # fix long questions for printing
    old_labels = list(df)
    new_labels = ["\n".join(wrap(str(l), label_max_width)) for l in old_labels]
    df = df.set_axis(new_labels, axis=1, inplace=False)

    counts_unordered = df.apply(lambda row: row.value_counts())
    counts = counts_unordered.reindex(scale).T
    counts = counts.fillna(0)

    # remove NA scores
    if drop_zeros == True:
        counts = counts.drop("0", axis=1)

    return counts


def likert_percentages(
    df: pd.DataFrame, scale: Scale, width=30, zero=False
) -> pd.DataFrame:
    """
    Given a dataframe of Likert-style responses, returns a new one
    reporting the percentage of respondents that chose each response.
    Percentages are rounded to integers.
    """
    counts = likert_counts(df, scale, width, zero)

    # Warn if the rows have different counts
    # If they do, the percentages shouldn't be compared.
    responses_per_question = counts.sum(axis=1)
    responses_to_first_question = responses_per_question[0]
    responses_same = responses_per_question == responses_to_first_question
    if not responses_same.all():
        warn(
            "In your data, not all questions have the same number of responses. i.e., different numbers of people answered each question. Therefore, the percentages aren't directly comparable: X% for one question represents a different number of responses than X% for another question, yet they will appear the same in the percentage graph. This may be misleading to your reader."
        )

    return counts.apply(lambda row: row / row.sum(), axis=1).applymap(lambda v: 100 * v)


def likert_response(df: pd.DataFrame, scale: Scale) -> pd.DataFrame:
    """
    This function replaces values in the original dataset to match one of the plot_likert
    scales in scales.py. Note that you should use a '_0' scale if there are NA values in the
    orginal data.
    """
    for i in range(0, len(scale)):
        df = df.applymap(lambda x: scale[i] if str(i) in x else x)
    return df


def plot_likert(
    df: pd.DataFrame,
    plot_scale: Scale,
    plot_percentage: bool = False,
    format_scale: Scale = None,
    colors: colors.Colors = colors.default,
    label_max_width: int = 30,
    drop_zeros: bool = False,
    figsize=None,
) -> matplotlib.axes.Axes:
    """
    The purpose of this function is to combine all of the steps into one 'simple' function.
    format_scale is the scale used to reformat the responses (with '_0' for a dataset with NA values).
    plot_scale is the scale used for the actual plot.
    label_max_width is the character wrap length for the Y axis.
    drop_zeros indicates whether the data have NA values that should be dropped (True) or not (False).
    """
    if format_scale:
        df_fixed = likert_response(df, format_scale)
    else:
        df_fixed = df
        format_scale = plot_scale

    if plot_percentage:
        counts = likert_percentages(df_fixed, format_scale, label_max_width, drop_zeros)
    else:
        counts = likert_counts(df_fixed, format_scale, label_max_width, drop_zeros)

    return plot_counts(counts, plot_scale, plot_percentage, colors, figsize=figsize)


def raw_scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    The purpose of this function is to determine the scale(s) used in the dataset.
    """
    df_m = df.melt()
    scale = df_m["value"].drop_duplicates()
    return scale
