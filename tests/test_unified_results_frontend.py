"""Behavioral tests for embedded charts and unified simulation results."""

from __future__ import annotations

import os
import tempfile
import unittest
from time import perf_counter
from unittest.mock import patch

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QSplitter, QTableView

from app.graphs import (
    linear_graph,
    linear_graph_maxs,
    plot_correlation_matrix,
    plot_superficie,
)
from app.screens.simulation_screen import (
    AnalysisPanel,
    ResultsTable,
    SimulationScreen,
)
from app.ui.theme import APP_STYLESHEET
from main import MainWindow


class UnifiedResultsFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.data = pd.DataFrame(
            {
                "A": [1.0, 1.5, 2.0, 2.5],
                "B": [2.0, 1.5, 1.0, 0.5],
                "A Initial": [1.0, 1.0, 2.0, 2.0],
                "Temperature": [300.0, 400.0, 300.0, 400.0],
                "Initial Temperature": [300.0, 400.0, 300.0, 400.0],
                "Pressure": [1.0, 1.0, 2.0, 2.0],
                "Equilibrium Temperature (K)": [500.0, 510.0, 520.0, 530.0],
            }
        )

    def tearDown(self):
        plt.close("all")

    def test_graph_builders_return_figures_without_opening_windows(self):
        """Regression: chart generation must not call pyplot.show()."""
        with patch.object(plt, "show", side_effect=AssertionError("external window")):
            figures = [
                plot_superficie(self.data, "Temperature", "Pressure", "A"),
                plot_correlation_matrix(self.data[["A", "B", "Temperature"]]),
                linear_graph(
                    self.data,
                    "A Initial",
                    "Pressure",
                    1.0,
                    1.0,
                    np.array(["A", "B"]),
                    ["A", "B"],
                    "A Initial",
                    "T",
                ),
                linear_graph_maxs(
                    self.data,
                    "A Initial",
                    "Pressure",
                    1.0,
                    1.0,
                    np.array(["A", "B"]),
                    ["A", "B"],
                    "A Initial",
                    "T",
                ),
            ]

        self.assertTrue(all(isinstance(figure, Figure) for figure in figures))

    def test_analysis_panel_embeds_generated_figure(self):
        panel = AnalysisPanel(
            self.data,
            np.array(["A", "B"]),
            "A",
            "gibbs",
        )
        panel._plot_correlation()

        self.assertIsInstance(panel.figure_canvas.figure, Figure)
        self.assertGreaterEqual(len(panel.figure_canvas.figure.axes), 2)

    def test_results_table_displays_complete_result_set(self):
        results = ResultsTable(self.data, np.array(["A", "B"]), "gibbs")

        self.assertEqual(results.table.model().rowCount(), len(self.data))
        self.assertEqual(results.table.model().columnCount(), len(self.data.columns))
        self.assertEqual(results.table.model().index(2, 0).data(), "2.0")

    def test_large_results_use_a_lazy_table_model(self):
        large_data = pd.DataFrame(
            np.arange(200_000, dtype=float).reshape(10_000, 20),
            columns=[f"C{index}" for index in range(20)],
        )

        started_at = perf_counter()
        results = ResultsTable(large_data, large_data.columns, "gibbs")
        elapsed = perf_counter() - started_at

        self.assertIsInstance(results.table, QTableView)
        self.assertLess(elapsed, 1.0)
        self.assertEqual(results.table.model().rowCount(), 10_000)

    def test_graphs_and_results_share_one_splitter(self):
        screen = SimulationScreen("gibbs")
        screen.reference_componente = "A"
        screen.components = np.array(["A", "B"])
        screen._started_at = 0.0
        screen._on_done(self.data)

        self.assertIsInstance(screen.results_splitter, QSplitter)
        self.assertEqual(screen.results_splitter.count(), 2)
        self.assertIsInstance(screen.results_splitter.widget(0), AnalysisPanel)
        self.assertIsInstance(screen.results_splitter.widget(1), ResultsTable)

    def test_embedded_chart_keeps_a_readable_height(self):
        screen = SimulationScreen("gibbs")
        screen.reference_componente = "A"
        screen.components = np.array(["A", "B"])
        screen._started_at = 0.0
        screen._on_done(self.data)
        panel = screen.results_splitter.widget(0)
        panel._plot_correlation()
        screen.resize(1400, 1000)
        screen.show()
        self.app.processEvents()

        visible_height = panel.figure_canvas.visibleRegion().boundingRect().height()
        self.assertGreaterEqual(visible_height, 160)
        screen.close()

    def test_embedded_chart_is_readable_inside_the_real_main_window(self):
        self.app.setStyle("Fusion")
        self.app.setStyleSheet(APP_STYLESHEET)
        window = MainWindow()
        window.resize(1180, 740)
        window.show()
        for index, screen in ((1, window.ming_screen), (2, window.maxs_screen)):
            with self.subTest(mode=screen.mode):
                window.navigate_to(index)
                screen.reference_componente = "A"
                screen.components = np.array(["A", "B"])
                screen._started_at = 0.0
                screen._on_done(self.data)
                panel = screen.results_splitter.widget(0)
                panel._plot_correlation()
                self.app.processEvents()
                visible_height = panel.figure_canvas.visibleRegion().boundingRect().height()
                self.assertGreaterEqual(visible_height, 160)
        window.close()

    def test_results_can_still_be_exported_to_csv(self):
        results = ResultsTable(self.data, np.array(["A", "B"]), "gibbs")
        with tempfile.TemporaryDirectory() as directory:
            output_path = os.path.join(directory, "results.csv")
            with (
                patch(
                    "app.screens.simulation_screen.QFileDialog.getSaveFileName",
                    return_value=(output_path, "CSV (*.csv)"),
                ),
                patch("app.screens.simulation_screen.QMessageBox.information"),
            ):
                results._save_results()

            exported = pd.read_csv(output_path)
            pd.testing.assert_frame_equal(exported, self.data)


if __name__ == "__main__":
    unittest.main()

