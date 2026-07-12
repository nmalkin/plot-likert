import unittest
import warnings

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plot_likert
from plot_likert.plot_likert import PADDING_LEFT, PADDING_RIGHT, PlotLikertError

SCALE = ["Disagree", "Neutral", "Agree"]


def make_counts(values_per_question):
    return pd.DataFrame.from_dict(values_per_question, orient="index", columns=SCALE)


class TestXRange(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_fixed_range_sets_ticks_labels_and_limits(self):
        # One question, already summing to 100:
        # middles = 30 + 20/2 = 40, so the center line sits at x=40
        counts = make_counts({"Q1": [30, 20, 50]})

        axes = plot_likert.plot_counts(
            counts,
            SCALE,
            compute_percentages=True,
            x_range=(40, 40),
            xtick_interval=20,
        )

        ticks = sorted(axes.get_xticks())
        self.assertEqual(ticks, [0, 20, 40, 60, 80])

        labels = [label.get_text() for label in axes.get_xticklabels()]
        self.assertEqual(sorted(labels), sorted(["40%", "20%", "0%", "20%", "40%"]))

        expected_xlim = (0 - 80 * PADDING_LEFT, 80 + 80 * PADDING_RIGHT)
        np.testing.assert_allclose(axes.get_xlim(), expected_xlim)

    def test_plots_sharing_x_range_get_identical_axes(self):
        counts_a = make_counts({"Q1": [10, 10, 80]})
        counts_b = make_counts({"Q1": [60, 20, 20]})

        spans = []
        relative_ticks = []
        labels = []
        for counts, center in ((counts_a, 15), (counts_b, 70)):
            axes = plot_likert.plot_counts(
                counts,
                SCALE,
                compute_percentages=True,
                x_range=100,
                xtick_interval=25,
            )
            x_min, x_max = axes.get_xlim()
            spans.append(x_max - x_min)
            relative_ticks.append(sorted(tick - center for tick in axes.get_xticks()))
            labels.append(sorted(label.get_text() for label in axes.get_xticklabels()))

        self.assertEqual(spans[0], spans[1])
        self.assertEqual(relative_ticks[0], relative_ticks[1])
        self.assertEqual(labels[0], labels[1])

    def test_single_number_is_symmetric(self):
        counts = make_counts({"Q1": [30, 20, 50]})

        axes_scalar = plot_likert.plot_counts(
            counts, SCALE, compute_percentages=True, x_range=60, xtick_interval=25
        )
        axes_pair = plot_likert.plot_counts(
            counts, SCALE, compute_percentages=True, x_range=(60, 60), xtick_interval=25
        )

        np.testing.assert_allclose(axes_scalar.get_xlim(), axes_pair.get_xlim())
        np.testing.assert_allclose(axes_scalar.get_xticks(), axes_pair.get_xticks())

    def test_works_with_raw_counts(self):
        counts = make_counts({"Q1": [4, 2, 4]})

        axes = plot_likert.plot_counts(counts, SCALE, x_range=(5, 5), xtick_interval=5)

        labels = [label.get_text() for label in axes.get_xticklabels()]
        self.assertEqual(sorted(labels), sorted(["5", "0", "5"]))

    def test_passes_through_plot_likert(self):
        responses = pd.DataFrame({"Q1": ["Agree", "Disagree", "Agree", "Neutral"]})

        axes = plot_likert.plot_likert(
            responses, SCALE, plot_percentage=True, x_range=100
        )

        x_min, x_max = axes.get_xlim()
        expected_span = 200 + 200 * PADDING_LEFT + 200 * PADDING_RIGHT
        self.assertAlmostEqual(x_max - x_min, expected_span)

    def test_invalid_values_are_rejected(self):
        counts = make_counts({"Q1": [30, 20, 50]})

        for bad_x_range in (-10, (40, -10), (10, 20, 30), (0, 0)):
            with self.assertRaises(PlotLikertError):
                plot_likert.plot_counts(
                    counts, SCALE, compute_percentages=True, x_range=bad_x_range
                )

    def test_warns_when_bars_exceed_range(self):
        counts = make_counts({"Q1": [30, 20, 50]})

        with self.assertWarns(UserWarning):
            plot_likert.plot_counts(
                counts, SCALE, compute_percentages=True, x_range=(20, 60)
            )

    def test_no_warning_when_bars_fit(self):
        counts = make_counts({"Q1": [30, 20, 50]})

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            plot_likert.plot_counts(
                counts, SCALE, compute_percentages=True, x_range=(40, 60)
            )
        self.assertEqual([str(w.message) for w in caught], [])


if __name__ == "__main__":
    unittest.main()
