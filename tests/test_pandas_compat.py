"""
Regression tests for the data-handling functions and for compatibility with
current pandas versions (2.1+ and 3.x: DataFrame.map instead of applymap,
positional Series lookups via .iloc, the new default string dtype,
and no deprecated keyword arguments).
"""

import unittest
import warnings

import matplotlib

matplotlib.use("Agg")  # no GUI needed for the tests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plot_likert
from plot_likert.scales import agree


def sample_responses(index=None):
    return pd.DataFrame(
        {
            "Q1": [agree[0], agree[1], agree[2], agree[3], agree[4], agree[4]],
            "Q2": [agree[4], agree[4], agree[3], agree[2], agree[2], agree[0]],
        },
        index=index,
    )


class PandasWarningsAsErrors(unittest.TestCase):
    """Fail on any deprecation warning raised while running a test."""

    def setUp(self):
        self._warnings = warnings.catch_warnings()
        self._warnings.__enter__()
        warnings.simplefilter("error", DeprecationWarning)
        warnings.simplefilter("error", FutureWarning)
        try:  # pandas 3 has its own deprecation warning classes
            from pandas.errors import PandasChangeWarning

            warnings.simplefilter("error", PandasChangeWarning)
        except ImportError:
            pass

    def tearDown(self):
        self._warnings.__exit__(None, None, None)
        plt.close("all")


class TestLikertCounts(PandasWarningsAsErrors):
    def test_counts_dataframe(self):
        counts = plot_likert.likert_counts(sample_responses(), agree)
        self.assertEqual(list(counts.columns), list(agree))
        self.assertEqual(list(counts.index), ["Q1", "Q2"])
        self.assertEqual(counts.loc["Q1"].tolist(), [1, 1, 1, 1, 2])
        self.assertEqual(counts.loc["Q2"].tolist(), [1, 0, 2, 1, 2])

    def test_counts_series(self):
        counts = plot_likert.likert_counts(sample_responses()["Q1"], agree)
        self.assertEqual(counts.loc["Q1"].tolist(), [1, 1, 1, 1, 2])

    def test_counts_with_missing_values(self):
        df = sample_responses()
        df.loc[0, "Q1"] = np.nan
        counts = plot_likert.likert_counts(df, agree)
        self.assertEqual(counts.loc["Q1"].tolist(), [0, 1, 1, 1, 2])

    def test_counts_explicit_string_dtype(self):
        counts = plot_likert.likert_counts(sample_responses().astype("string"), agree)
        self.assertEqual(counts.loc["Q2"].tolist(), [1, 0, 2, 1, 2])

    def test_long_labels_are_wrapped(self):
        df = sample_responses().rename(columns={"Q1": "a " * 30})
        counts = plot_likert.likert_counts(df, agree, label_max_width=10)
        self.assertIn("\n", counts.index[0])

    def test_input_is_not_modified(self):
        df = sample_responses()
        plot_likert.likert_counts(df, agree, label_max_width=1)
        self.assertEqual(list(df.columns), ["Q1", "Q2"])

    def test_invalid_value_raises(self):
        df = sample_responses()
        df.loc[0, "Q1"] = "Maybe"
        with self.assertRaises(plot_likert.PlotLikertError):
            plot_likert.likert_counts(df, agree)

    def test_numeric_responses_with_numeric_scale(self):
        df = pd.DataFrame({"Q1": [1, 2, 3, 4, 5, 5]})
        counts = plot_likert.likert_counts(df, [1, 2, 3, 4, 5])
        self.assertEqual(counts.loc["Q1"].tolist(), [1, 1, 1, 1, 2])


class TestLikertPercentages(PandasWarningsAsErrors):
    def test_percentages(self):
        pct = plot_likert.likert_percentages(sample_responses(), agree)
        self.assertAlmostEqual(pct.loc["Q1", agree[4]], 100 * 2 / 6)
        np.testing.assert_allclose(pct.sum(axis=1).to_numpy(), [100, 100])

    def test_percentages_non_integer_index(self):
        # pandas 3: Series[0] is a label lookup, so the first row must be read with .iloc
        df = sample_responses(index=list("abcdef"))
        pct = plot_likert.likert_percentages(df, agree)
        np.testing.assert_allclose(pct.sum(axis=1).to_numpy(), [100, 100])

    def test_unequal_response_counts_warn(self):
        df = sample_responses()
        df.loc[0, "Q1"] = np.nan
        with self.assertWarns(UserWarning):
            plot_likert.likert_percentages(df, agree)


class TestLikertResponse(PandasWarningsAsErrors):
    def test_numeric_codes_replaced_by_scale(self):
        df = pd.DataFrame({"Q1": ["1", "2", "3"], "Q2": ["3", "3", "1"]})
        result = plot_likert.likert_response(df, ["zero", "one", "two", "three"])
        self.assertEqual(result["Q1"].tolist(), ["one", "two", "three"])
        self.assertEqual(result["Q2"].tolist(), ["three", "three", "one"])


class TestPlotting(PandasWarningsAsErrors):
    def test_plot_likert(self):
        ax = plot_likert.plot_likert(sample_responses(), agree)
        self.assertEqual(len(ax.patches), 2 * (len(agree) + 1))

    def test_plot_likert_percentages_and_bar_labels(self):
        ax = plot_likert.plot_likert(
            sample_responses(), agree, plot_percentage=True, bar_labels=True
        )
        self.assertEqual(ax.get_xlabel(), "Percentage of Responses")

    def test_plot_likert_series(self):
        ax = plot_likert.plot_likert(sample_responses()["Q2"], agree)
        self.assertEqual(len(ax.patches), len(agree) + 1)

    def test_plot_likert_format_scale(self):
        df = pd.DataFrame({"Q1": ["1", "2", "3", "4", "5"]})
        ax = plot_likert.plot_likert(df, agree, format_scale=["NA"] + list(agree))
        self.assertEqual(ax.get_xlabel(), "Number of Responses")

    def test_plot_counts_non_integer_index(self):
        counts = pd.DataFrame(
            [[1, 2, 4, 2, 1], [2, 2, 2, 2, 2]],
            columns=agree,
            index=["first question", "second question"],
        )
        ax = plot_likert.plot_counts(counts, agree, compute_percentages=True)
        self.assertEqual(ax.get_xlabel(), "Percentage of Responses")


if __name__ == "__main__":
    unittest.main()
