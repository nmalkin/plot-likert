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


class PlotLikertError(ValueError):
    pass


def plot_counts(
    counts: pd.DataFrame,
    scale: Scale,
    plot_percentage: typing.Optional[bool] = None,
    colors: colors.Colors = colors.default,
    figsize=None,
    xtick_interval: typing.Optional[int] = None,
    compute_percentages: bool = False,
) -> matplotlib.axes.Axes:
    """
    Plot the given counts of Likert responses.


    Parameters
    ----------
    counts : pd.DataFrame
        The given DataFrame should contain the pre-computed counts of responses to a set of Likert-style questions.
        Its columns represent the total counts in each category, while each row is a different question.
    scale : list of str
        The scale used for the plot: an ordered list of strings for each of the answer options.
    plot_percentage : bool, optional
        DEPRECATED: use `compute_percentages` instead.
        If true, the counts are assumed to be percentages and % marks will be added to the x-axis labels.
    colors : list of str
        A list of colors in hex string or RGB tuples to use for plotting.
        Attention: if your colormap doesn't work right try appending transparent ("#ffffff00") in the first place.
    figsize : tuple of (int, int)
        A tuple (width, heigth) that controls size of the final figure - similarly to matplotlib
    xtick_interval : int, optional
        Controls the interval between x-axis ticks.
    compute_percentages: bool = False,
        Convert the given response counts to percentages and display the counts as percentages in the plot.

    Returns
    -------
    matplotlib.axes.Axes
        The axes of the generated Likert plot

    See Also
    --------
    plot_likert : aggregate raw responses then plot them. Most often, you'll want to use that function instead of calling this one directly.
    """
    if plot_percentage is not None:
        warn(
            "parameter `plot_percentage` for `plot_likert.likert_counts` is deprecated, set it to None and use `compute_percentages` instead",
            FutureWarning,
        )
        counts_are_percentages = plot_percentage
    else:
        # Re-compute counts as percentages, if requested
        if compute_percentages:
            counts = _compute_counts_percentage(counts)
            counts_are_percentages = True
        else:
            counts_are_percentages = False

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
    center_line = ax.axvline(center, linestyle="--", color="black", alpha=0.5)
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

    if counts_are_percentages:
        xlabels = [str(label) + "%" if label != "" else "" for label in xlabels]

    ax.set_xticks(xvalues)
    ax.set_xticklabels(xlabels)
    if counts_are_percentages is True:
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
            raise PlotLikertError(
                f"A response was found with value `{value}`, which is not one of the values in the provided scale: {scale}. If this is unexpected, you might want to double-check for extra whitespace, capitalization, spelling, or type (int versus str)."
            )

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

    # This internal function is no longer used; it is therefore deprecated and may be removed in future versions.
    warn(
        "plot_likert internal function `likert_percentages` may be removed in future versions",
        FutureWarning,
    )

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


def _compute_counts_percentage(counts: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of response counts, return a new one
    with the response counts converted to percentages.
    """
    # Warn if the rows have different counts
    # If they do, the percentages shouldn't be compared.
    responses_per_question = counts.sum(axis="columns")
    responses_to_first_question = responses_per_question[0]
    responses_same = responses_per_question == responses_to_first_question
    if not responses_same.all():
        warn(
            "In your data, not all questions have the same number of responses. i.e., different numbers of people answered each question. Therefore, the percentages aren't directly comparable: X% for one question represents a different number of responses than X% for another question, yet they will appear the same in the percentage graph. This may be misleading to your reader."
        )
    return counts.divide(counts.sum(axis="columns"), axis="rows") * 100


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
    xtick_interval: typing.Optional[int] = None,
) -> matplotlib.axes.Axes:
    """
    Plot the given Likert-type dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe with questions in column names and answers recorded as cell values.
    plot_scale : list
        The scale used for the actual plot: a list of strings in order for answer options.
    plot_percentage : bool
        Normalize the answer counts.
    format_scale : list of str
        Optional scale used to reformat the responses: \
        if your responses are numeric values, you can pass in this scale to replace them with text. \
        If your dataset has NA values, this list must have a corresponding 0/empty value at the beginning.
    colors : list of str
        A list of colors in hex string or RGB tuples to use for plotting. Attention: if your \
        colormap doesn't work right try appending transparent ("#ffffff00") in the first place.
    label_max_width : int
        The character wrap length of the y-axis labels.
    drop_zeros : bool
        Indicates whether the data have NA values that should be dropped (True) or not (False).
    figsize : tuple of (int, int)
        A tuple (width, heigth) that controls size of the final figure - \
        similarly to matplotlib
    xtick_interval : int
        Controls the interval between x-axis ticks.

    Returns
    -------
    matplotlib.axes.Axes
        Likert plot
    """
    if format_scale:
        df_fixed = likert_response(df, format_scale)
    else:
        df_fixed = df
        format_scale = plot_scale

    counts = likert_counts(df_fixed, format_scale, label_max_width, drop_zeros)

    if drop_zeros:
        plot_scale = plot_scale[1:]

    return plot_counts(
        counts=counts,
        scale=plot_scale,
        colors=colors,
        figsize=figsize,
        xtick_interval=xtick_interval,
        compute_percentages=plot_percentage,
    )


def raw_scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    The purpose of this function is to determine the scale(s) used in the dataset.
    """
    df_m = df.melt()
    scale = df_m["value"].drop_duplicates()
    return scale
