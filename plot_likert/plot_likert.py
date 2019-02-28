"""
Plot Likert-style data from Pandas using Matplotlib

Initially based on code from Austin Cory Bart
https://stackoverflow.com/a/41384812
"""

import logging
from warnings import warn

import numpy
import pandas


try:
    import matplotlib.axes
    import matplotlib.pyplot as plt
except RuntimeError as err:
    logging.error(
        "Couldn't import matplotlib, likely because this package is running in an environment that doesn't support it (i.e., without a graphical output). See error for more information."
    )
    raise err

from plot_likert.scales import Scale

likert_colors = [
    "white",
    "firebrick",
    "lightcoral",
    "gainsboro",
    "cornflowerblue",
    "darkblue",
]


def plot_counts(
    counts: pandas.DataFrame, scale: Scale, figsize=None
) -> matplotlib.axes.Axes:
    # Pad each row/question from the left, so that they're centered around the middle (Neutral) response
    scale_middle = len(scale) // 2
    middles = (
        counts.iloc[:, 0:scale_middle].sum(axis=1) + counts.iloc[:, scale_middle] / 2
    )
    center = middles.max()

    padding_values = (middles - center).abs()
    padded_counts = pandas.concat([padding_values, counts], axis=1)
    # hack to "hide" the label for the padding
    padded_counts = padded_counts.rename({0: "Legend"}, axis=1)

    # Reverse rows to keep the questions in order
    # (Otherwise, the plot function shows the last one at the top.)
    reversed_rows = padded_counts.iloc[::-1]

    # Start putting together the plot
    ax = reversed_rows.plot.barh(stacked=True, color=likert_colors, figsize=figsize)

    # Draw center line
    center_line = plt.axvline(center, linestyle="--", color="black", alpha=0.5)
    center_line.set_zorder(-1)

    # Compute and show x labels
    max_width = int(round(padded_counts.sum(axis=1).max()))
    right_edge = max_width - center
    interval = ax.xaxis.get_tick_space()
    right_labels = numpy.arange(0, right_edge, interval)
    right_values = center + right_labels
    left_labels = numpy.arange(0, center + 1, interval)
    left_values = center - left_labels
    xlabels = numpy.concatenate([left_labels, right_labels])
    xvalues = numpy.concatenate([left_values, right_values])

    xlabels = [int(l) for l in xlabels if round(l) == l]

    ax.set_xticks(xvalues)
    ax.set_xticklabels(xlabels)

    # Control legend
    plt.legend(bbox_to_anchor=(1.05, 1))

    return ax


def likert_counts(df: pandas.DataFrame, scale: Scale) -> pandas.DataFrame:
    """
    Given a dataframe of Likert-style responses, returns a count of each response,
    validating them against the provided scale.
    """

    def validate(value):
        if (value not in scale) and (not pandas.isna(value)):
            raise ValueError(f"{value} is not in the scale")

    df.applymap(validate)

    counts_unordered = df.apply(lambda row: row.value_counts())
    counts = counts_unordered.reindex(scale).T
    counts = counts.fillna(0)
    return counts


def likert_percentages(df: pandas.DataFrame, scale: Scale) -> pandas.DataFrame:
    """
    Given a dataframe of Likert-style responses, returns a new one
    reporting the percentage of respondents that chose each response.
    Percentages are rounded to integers.
    """
    counts = likert_counts(df, scale)

    # Warn if the rows have different counts
    # If they do, the percentages shouldn't be compared.
    responses_per_question = counts.sum(axis=1)
    responses_to_first_question = responses_per_question[0]
    responses_same = responses_per_question == responses_to_first_question
    if not responses_same.all():
        warn(
            "Not all (sub)questions have the same number of responses. Therefore, percentages aren't directly comparable."
        )

    return counts.apply(lambda row: row / row.sum(), axis=1).applymap(
        lambda v: int(round(100 * v))
    )
