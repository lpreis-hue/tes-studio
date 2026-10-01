"""Dark technical workspace shared by the Gibbs and entropy modules."""

from __future__ import annotations

from time import perf_counter

import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QCursor, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.auxiliar_func.read_data import ReadData
from app.graphs import (
    linear_graph,
    linear_graph_maxs,
    plot_correlation_matrix,
    plot_superficie,
)
from app.screens.sim_worker import SimWorker


_FILE_FILTER = (
    "Planilhas (*.xlsx *.xls);;CSV (*.csv);;Texto (*.txt);;Todos os arquivos (*)"
)


class CheckableComboBox(QComboBox):
    """Compact multi-selection control used by composition charts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(QStandardItemModel(self))
        self.view().pressed.connect(self._toggle_item)

    def add_check_item(self, text):
        item = QStandardItem(str(text))
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.model().appendRow(item)

    def checked_items(self):
        return [
            self.model().item(index).text()
            for index in range(self.count())
            if self.model().item(index).checkState() == Qt.CheckState.Checked
        ]

    def _toggle_item(self, index):
        item = self.model().itemFromIndex(index)
        checked = item.checkState() == Qt.CheckState.Checked
        item.setCheckState(
            Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked
        )


class DataFrameTableModel(QAbstractTableModel):
    """Expose a DataFrame lazily so large result sets do not freeze the UI."""

    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self.dataframe = dataframe

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.dataframe)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.dataframe.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        value = self.dataframe.iat[index.row(), index.column()]
        return "" if pd.isna(value) else str(value)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self.dataframe.columns[section])
        return str(section + 1)


class AnalysisPanel(QWidget):
    """Result overview and launch controls for the existing plot functions."""

    def __init__(self, dataframe, components, reference_component, mode, parent=None):
        super().__init__(parent)
        self.dataframe = dataframe
        self.components = list(components)
        self.reference_component = reference_component
        self.mode = mode
        self.temperature_column = (
            "Temperature" if mode == "gibbs" else "Initial Temperature"
        )
        self.reference_column = f"{reference_component} Initial"
        self.has_reference = self.reference_column in dataframe.columns

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        root.addWidget(self._build_summary())
        root.addWidget(self._build_plot_card(), 1)

    def _build_summary(self):
        temp_min = self.dataframe[self.temperature_column].min()
        temp_max = self.dataframe[self.temperature_column].max()
        pressure_min = self.dataframe["Pressure"].min()
        pressure_max = self.dataframe["Pressure"].max()
        summary = QLabel(
            f"{len(self.dataframe)} cenários  •  "
            f"{len(self.components)} componentes  •  "
            f"{temp_min:g}–{temp_max:g} K  •  "
            f"Pressão {pressure_min:g}–{pressure_max:g}",
            objectName="metricSubtitle",
        )
        summary.setWordWrap(True)
        return summary

    def _build_plot_card(self):
        card = QFrame(objectName="innerCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        heading = QHBoxLayout()
        heading.addWidget(QLabel("Ferramentas de análise", objectName="sectionTitle"))
        heading.addStretch(1)
        correlation = QPushButton("Matriz de correlação", objectName="secondaryAction")
        correlation.clicked.connect(self._plot_correlation)
        heading.addWidget(correlation)
        layout.addLayout(heading)

        surface_grid = QGridLayout()
        surface_grid.setHorizontalSpacing(10)
        self.x_combo = self._combo(self.dataframe.columns)
        self.y_combo = self._combo(self.dataframe.columns)
        self.z_combo = self._combo(self.dataframe.columns)
        self._select(self.x_combo, self.temperature_column)
        self._select(self.y_combo, "Pressure")
        default_z = next(
            (component for component in self.components if component in self.dataframe),
            self.dataframe.columns[0],
        )
        self._select(self.z_combo, default_z)
        surface_grid.addWidget(QLabel("Eixo X"), 0, 0)
        surface_grid.addWidget(self.x_combo, 1, 0)
        surface_grid.addWidget(QLabel("Eixo Y"), 0, 1)
        surface_grid.addWidget(self.y_combo, 1, 1)
        surface_grid.addWidget(QLabel("Eixo Z"), 0, 2)
        surface_grid.addWidget(self.z_combo, 1, 2)
        surface_button = QPushButton("Gerar superfície 3D", objectName="primaryAction")
        surface_button.clicked.connect(self._plot_surface)
        surface_grid.addWidget(surface_button, 1, 3)
        for column in range(3):
            surface_grid.setColumnStretch(column, 1)
        layout.addLayout(surface_grid)

        divider = QFrame(objectName="divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        composition_grid = QGridLayout()
        composition_grid.setHorizontalSpacing(10)
        self.component_combo = CheckableComboBox()
        for component in self.components:
            self.component_combo.add_check_item(component)
        composition_grid.addWidget(QLabel("Componentes dos gráficos"), 0, 0, 1, 2)
        composition_grid.addWidget(self.component_combo, 1, 0, 1, 2)

        self.n_for_t = self._value_combo(self.reference_column)
        self.p_for_t = self._value_combo("Pressure")
        self.n_for_p = self._value_combo(self.reference_column)
        self.t_for_p = self._value_combo(self.temperature_column)
        self.p_for_n = self._value_combo("Pressure")
        self.t_for_n = self._value_combo(self.temperature_column)

        composition_grid.addWidget(QLabel("n fixo"), 0, 2)
        composition_grid.addWidget(self.n_for_t, 1, 2)
        composition_grid.addWidget(QLabel("P fixa"), 0, 3)
        composition_grid.addWidget(self.p_for_t, 1, 3)
        button_t = QPushButton("Composição × T", objectName="plotAction")
        button_t.clicked.connect(lambda: self._plot_composition("T"))
        composition_grid.addWidget(button_t, 1, 4)

        composition_grid.addWidget(QLabel("n fixo"), 2, 2)
        composition_grid.addWidget(self.n_for_p, 3, 2)
        composition_grid.addWidget(QLabel("T fixa"), 2, 3)
        composition_grid.addWidget(self.t_for_p, 3, 3)
        button_p = QPushButton("Composição × P", objectName="plotAction")
        button_p.clicked.connect(lambda: self._plot_composition("P"))
        composition_grid.addWidget(button_p, 3, 4)

        composition_grid.addWidget(QLabel("P fixa"), 2, 0)
        composition_grid.addWidget(self.p_for_n, 3, 0)
        composition_grid.addWidget(QLabel("T fixa"), 2, 1)
        composition_grid.addWidget(self.t_for_n, 3, 1)
        button_n = QPushButton("Composição × n", objectName="plotAction")
        button_n.clicked.connect(lambda: self._plot_composition("N"))
        composition_grid.addWidget(button_n, 3, 4)

        for button in (button_t, button_p, button_n):
            button.setEnabled(self.has_reference)
            if not self.has_reference:
                button.setToolTip(
                    "Selecione um componente de referência antes da simulação."
                )
        for combo in (self.n_for_t, self.n_for_p):
            combo.setEnabled(self.has_reference)
        layout.addLayout(composition_grid)

        self.chart_host = QFrame(objectName="chartHost")
        self.chart_layout = QVBoxLayout(self.chart_host)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        placeholder = QLabel("Escolha uma análise para exibir o gráfico nesta área.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_layout.addWidget(placeholder)
        layout.addWidget(self.chart_host, 1)
        return card

    @staticmethod
    def _combo(items):
        combo = QComboBox()
        combo.addItems([str(item) for item in items])
        return combo

    def _value_combo(self, column):
        if column not in self.dataframe:
            return self._combo([])
        return self._combo(self.dataframe[column].dropna().unique())

    @staticmethod
    def _select(combo, text):
        index = combo.findText(str(text))
        if index >= 0:
            combo.setCurrentIndex(index)

    def _plot_surface(self):
        x_value = self.x_combo.currentText()
        y_value = self.y_combo.currentText()
        if self.dataframe[x_value].nunique() < 2 or self.dataframe[y_value].nunique() < 2:
            self._warn(
                "Pontos insuficientes",
                "Use pelo menos dois valores distintos nos eixos X e Y.",
            )
            return
        self._show_figure(
            plot_superficie(
                self.dataframe,
                x_value,
                y_value,
                self.z_combo.currentText(),
            )
        )

    def _plot_correlation(self):
        if len(self.dataframe.select_dtypes(include="number").columns) < 2:
            self._warn("Dados insuficientes", "São necessárias duas colunas numéricas.")
            return
        self._show_figure(plot_correlation_matrix(df=self.dataframe))

    def _plot_composition(self, graph_type):
        selected = self.component_combo.checked_items()
        if not selected:
            self._warn("Selecione componentes", "Marque ao menos um componente no campo de seleção.")
            return
        if graph_type == "T":
            label1, value1 = self.reference_column, float(self.n_for_t.currentText())
            label2, value2 = "Pressure", float(self.p_for_t.currentText())
        elif graph_type == "P":
            label1, value1 = self.reference_column, float(self.n_for_p.currentText())
            label2, value2 = self.temperature_column, float(self.t_for_p.currentText())
        else:
            label1, value1 = "Pressure", float(self.p_for_n.currentText())
            label2, value2 = self.temperature_column, float(self.t_for_n.currentText())

        plot_function = linear_graph if self.mode == "gibbs" else linear_graph_maxs
        self._show_figure(
            plot_function(
                dataframe=self.dataframe,
                label1=label1,
                label2=label2,
                value1=value1,
                value2=value2,
                components=self.components,
                selected_components=selected,
                name_colum=self.reference_column,
                graph_type=graph_type,
            )
        )

    def _show_figure(self, figure):
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.figure_canvas = FigureCanvas(figure)
        self.figure_canvas.setMinimumHeight(160)
        self.chart_layout.addWidget(self.figure_canvas)
        self.figure_canvas.draw_idle()

    def _warn(self, title, message):
        QMessageBox.warning(self, title, message)


class ResultsTable(QWidget):
    """Lazy full-result table with export of the original result set."""

    def __init__(self, dataframe, components, mode, parent=None):
        super().__init__(parent)
        self.original_data = dataframe
        self.temperature_column = (
            "Temperature" if mode == "gibbs" else "Initial Temperature"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        heading = QHBoxLayout()
        heading.addWidget(QLabel("Resultados completos da simulação", objectName="sectionTitle"))
        heading.addStretch(1)
        export = QPushButton("Exportar resultados", objectName="primaryAction")
        export.clicked.connect(self._save_results)
        heading.addWidget(export)
        root.addLayout(heading)

        self.table = QTableView(objectName="resultTable")
        self.model = DataFrameTableModel(dataframe, self.table)
        self.table.setModel(self.model)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setDefaultSectionSize(115)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        root.addWidget(self.table, 1)

    def _save_results(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar resultados",
            "resultados_tes_studio.xlsx",
            "Excel (*.xlsx);;CSV (*.csv)",
        )
        if not file_name:
            return
        try:
            if file_name.lower().endswith(".csv"):
                self.original_data.to_csv(file_name, index=False)
            else:
                if not file_name.lower().endswith(".xlsx"):
                    file_name += ".xlsx"
                self.original_data.to_excel(file_name, index=False)
            QMessageBox.information(self, "Exportação concluída", "Resultados salvos com sucesso.")
        except Exception as exc:
            QMessageBox.critical(self, "Falha ao exportar", str(exc))


class SimulationScreen(QWidget):
    """Full simulation workspace for either thermodynamic method."""

    def __init__(self, mode):
        super().__init__()
        if mode not in {"gibbs", "entropy"}:
            raise ValueError(f"Modo de simulação desconhecido: {mode}")
        self.mode = mode
        self.dataframe = self.data = self.species = self.initial = None
        self.components = np.array([])
        self.results = None
        self.file_path = ""
        self._worker = None
        self._started_at = None

        self.setObjectName("simulationPage")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        self.workspace_splitter = QSplitter(Qt.Orientation.Vertical)
        self.workspace_splitter.setChildrenCollapsible(False)

        self.setup_host = QWidget()
        self.setup_host.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Ignored,
        )
        top = QHBoxLayout(self.setup_host)
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(12)
        top.addWidget(self._build_data_card(), 4)
        top.addWidget(self._build_parameters_card(), 6)
        top.addWidget(self._build_run_card(), 3)
        self.workspace_splitter.addWidget(self.setup_host)
        self.workspace_splitter.addWidget(self._build_results_workspace())
        self.workspace_splitter.setSizes([320, 520])
        root.addWidget(self.workspace_splitter, 1)

    def _card(self, title, subtitle=None):
        card = QFrame(objectName="simulationCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        layout.addWidget(QLabel(title, objectName="cardHeading"))
        if subtitle:
            label = QLabel(subtitle, objectName="cardSubtitle")
            label.setWordWrap(True)
            layout.addWidget(label)
        return card, layout

    def _build_data_card(self):
        card, layout = self._card("Dados de entrada", "Composição inicial do sistema")
        action_row = QHBoxLayout()
        open_button = QPushButton("Abrir arquivo", objectName="secondaryAction")
        open_button.clicked.connect(self.open_file_dialog)
        action_row.addWidget(open_button)
        action_row.addStretch(1)
        self.file_status = QLabel("Nenhum arquivo", objectName="mutedLabel")
        action_row.addWidget(self.file_status)
        layout.addLayout(action_row)

        self.table = QTableWidget(objectName="inputTable")
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Componente", "Inicial (mol)"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)
        self.component_count = QLabel("0 componentes", objectName="mutedLabel")
        layout.addWidget(self.component_count)
        return card

    def _build_parameters_card(self):
        card, layout = self._card("Parâmetros", "Condições e discretização da simulação")
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        self.min_temp_input = QLineEdit(placeholderText="700")
        self.max_temp_input = QLineEdit(placeholderText="1100")
        self.min_pressure_input = QLineEdit(placeholderText="1")
        self.max_pressure_input = QLineEdit(placeholderText="10")
        self.n_values_t_input = QLineEdit(placeholderText="3")
        self.n_values_p_input = QLineEdit(placeholderText="3")
        self.n_values_n_input = QLineEdit(placeholderText="3")
        self.min_value_input = QLineEdit(placeholderText="0")
        self.max_value_input = QLineEdit(placeholderText="1")

        self.component_combobox = QComboBox()
        self.component_combobox.setEnabled(False)
        self.component_combobox.currentTextChanged.connect(self._on_component_changed)
        self.inhibit_component_combox = QComboBox()
        self.inhibit_component_combox.setEnabled(False)
        self.state_equation_combobox = QComboBox()
        self.state_equation_combobox.addItems(
            ["Ideal Gas", "Peng-Robinson", "Soave-Redlich-Kwong", "Redlich-Kwong", "Virial"]
        )

        self._add_field(grid, "Temperatura mínima (K)", self.min_temp_input, 0, 0)
        self._add_field(grid, "Temperatura máxima (K)", self.max_temp_input, 0, 2)
        self._add_field(grid, "Pressão mínima", self.min_pressure_input, 1, 0)
        self._add_field(grid, "Pressão máxima", self.max_pressure_input, 1, 2)
        self._add_field(grid, "Nº de temperaturas", self.n_values_t_input, 2, 0)
        self._add_field(grid, "Nº de pressões", self.n_values_p_input, 2, 2)
        self._add_field(grid, "Componente de referência", self.component_combobox, 3, 0)
        self._add_field(grid, "Nº de composições", self.n_values_n_input, 3, 2)
        self._add_field(grid, "Valor mínimo", self.min_value_input, 4, 0)
        self._add_field(grid, "Valor máximo", self.max_value_input, 4, 2)
        self._add_field(grid, "Equação de estado", self.state_equation_combobox, 5, 0)
        self._add_field(grid, "Inibir componente", self.inhibit_component_combox, 5, 2)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        layout.addLayout(grid)

        for field in (
            self.n_values_t_input,
            self.n_values_p_input,
            self.n_values_n_input,
        ):
            field.textChanged.connect(self._update_scenario_preview)
        self._on_component_changed("---")
        return card

    @staticmethod
    def _add_field(layout, label, widget, row, column):
        layout.addWidget(QLabel(label, objectName="fieldLabel"), row, column)
        layout.addWidget(widget, row, column + 1)

    def _build_run_card(self):
        card, layout = self._card("Simulação", "Solver não linear IPOPT")
        online = QLabel("●  IPOPT disponível", objectName="onlineStatus")
        layout.addWidget(online)

        self.btn_run = QPushButton("▶  Executar", objectName="runAction")
        self.btn_run.setMinimumHeight(48)
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self.run_simulation)
        layout.addWidget(self.btn_run)

        self.progress_bar = QProgressBar(objectName="simulationProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Abra um arquivo para começar.", objectName="statusText")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        summary = QFrame(objectName="scenarioSummary")
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(12, 10, 12, 10)
        summary_layout.addWidget(QLabel("TOTAL DE CENÁRIOS", objectName="metricTitle"))
        self.total_scenarios = QLabel("—", objectName="scenarioValue")
        summary_layout.addWidget(self.total_scenarios)
        self.scenario_detail = QLabel("Preencha os valores da malha", objectName="metricSubtitle")
        summary_layout.addWidget(self.scenario_detail)
        layout.addWidget(summary)
        return card

    def _build_results_workspace(self):
        workspace = QFrame(objectName="resultsWorkspace")
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(QLabel("Análises e resultados", objectName="sectionTitle"))

        self.results_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.results_splitter.setChildrenCollapsible(False)
        self.results_splitter.addWidget(
            self._empty_state("Execute uma simulação para liberar os gráficos.")
        )
        self.results_splitter.addWidget(
            self._empty_state("Os resultados aparecerão nesta mesma área.")
        )
        self.results_splitter.setSizes([900, 500])
        layout.addWidget(self.results_splitter, 1)
        return workspace

    @staticmethod
    def _empty_state(message):
        frame = QFrame(objectName="emptyState")
        layout = QVBoxLayout(frame)
        label = QLabel(message, objectName="emptyStateText")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return frame

    def collect_input_values(self):
        if self.data is None:
            QMessageBox.warning(self, "Sem dados", "Abra um arquivo antes de executar.")
            return False

        errors = []

        def number(field, label, integer=False):
            text = field.text().strip().replace(",", ".")
            if not text:
                errors.append(f"Informe {label}.")
                return None
            try:
                return int(text) if integer else float(text)
            except ValueError:
                errors.append(f"{label} possui valor inválido.")
                return None

        self.tmin = number(self.min_temp_input, "a temperatura mínima")
        self.tmax = number(self.max_temp_input, "a temperatura máxima")
        self.pmin = number(self.min_pressure_input, "a pressão mínima")
        self.pmax = number(self.max_pressure_input, "a pressão máxima")
        self.n_temperature = number(self.n_values_t_input, "o nº de temperaturas", True)
        self.n_pressure = number(self.n_values_p_input, "o nº de pressões", True)
        self.reference_componente = self.component_combobox.currentText()
        self.inhibit_component = self.inhibit_component_combox.currentText()
        self.state_equation = self.state_equation_combobox.currentText()

        has_reference = self.reference_componente not in {"", "---"}
        if has_reference:
            self.reference_componente_min = number(self.min_value_input, "o valor mínimo")
            self.reference_componente_max = number(self.max_value_input, "o valor máximo")
            self.n_component_values = number(self.n_values_n_input, "o nº de composições", True)
        else:
            self.reference_componente_min = 0.0
            self.reference_componente_max = 0.0
            self.n_component_values = 1

        if self.n_temperature is not None and self.n_temperature < 1:
            errors.append("O nº de temperaturas deve ser maior que zero.")
        if self.n_pressure is not None and self.n_pressure < 1:
            errors.append("O nº de pressões deve ser maior que zero.")
        if has_reference and self.n_component_values is not None and self.n_component_values < 1:
            errors.append("O nº de composições deve ser maior que zero.")
        if None not in (self.tmin, self.tmax) and self.tmin > self.tmax:
            errors.append("A temperatura mínima não pode superar a máxima.")
        if None not in (self.pmin, self.pmax):
            if self.pmin <= 0 or self.pmax <= 0:
                errors.append("As pressões devem ser positivas.")
            if self.pmin > self.pmax:
                errors.append("A pressão mínima não pode superar a máxima.")
        if has_reference and None not in (
            self.reference_componente_min,
            self.reference_componente_max,
        ) and self.reference_componente_min > self.reference_componente_max:
            errors.append("O valor mínimo do componente não pode superar o máximo.")

        if errors:
            QMessageBox.warning(self, "Revise os parâmetros", "\n".join(f"• {error}" for error in errors))
            return False
        return True

    def run_simulation(self):
        if not self.collect_input_values():
            return
        if self.mode == "gibbs":
            from app.auxiliar_func.run_gibbs import RunGibbs

            runner = RunGibbs(
                self.data, self.species, self.initial, self.components,
                self.tmin, self.tmax, self.pmin, self.pmax,
                self.n_temperature, self.n_pressure,
                self.reference_componente, self.reference_componente_min,
                self.reference_componente_max, self.n_component_values,
                self.inhibit_component, self.state_equation,
            )
            runner_function = runner.run_gibbs
        else:
            from app.auxiliar_func.run_entropy import RunEntropy

            runner = RunEntropy(
                self.data, self.species, self.initial, self.components,
                self.tmin, self.tmax, self.pmin, self.pmax,
                self.n_temperature, self.n_pressure,
                self.reference_componente, self.reference_componente_min,
                self.reference_componente_max, self.n_component_values,
                self.inhibit_component, self.state_equation,
            )
            runner_function = runner.run_entropy

        total = self.n_temperature * self.n_pressure * self.n_component_values
        self._start_simulation(total)
        self._worker = SimWorker(runner_function)
        self._worker.progress.connect(self._on_progress)
        self._worker.result_ready.connect(self._on_done)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _start_simulation(self, total):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._started_at = perf_counter()
        self.btn_run.setEnabled(False)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Iniciando {total} cenário(s)…")

    def _on_progress(self, current, total):
        self.progress_bar.setValue(current)
        elapsed = max(perf_counter() - self._started_at, 0.001)
        remaining = (elapsed / current) * (total - current) if current else 0
        self.status_label.setText(
            f"Cenário {current} de {total}\nTempo estimado restante: {self._format_seconds(remaining)}"
        )

    @staticmethod
    def _format_seconds(seconds):
        seconds = max(int(seconds), 0)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes} min {seconds:02d} s" if minutes else f"{seconds} s"

    def _finish_cursor(self):
        if QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()
        self.btn_run.setEnabled(True)

    def _on_done(self, results):
        self._finish_cursor()
        self.results = results
        elapsed = perf_counter() - self._started_at
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.status_label.setText(
            f"Simulação concluída em {self._format_seconds(elapsed)}."
        )
        self._replace_splitter_widget(
            0,
            AnalysisPanel(
                results, self.components, self.reference_componente, self.mode
            ),
        )
        self._replace_splitter_widget(
            1,
            ResultsTable(results, self.components, self.mode),
        )
        self.workspace_splitter.setSizes([120, 720])

    def _on_error(self, error_message):
        self._finish_cursor()
        self.progress_bar.setValue(0)
        self.status_label.setText("A simulação foi interrompida por um erro.")
        QMessageBox.critical(self, "Erro na simulação", error_message)

    @staticmethod
    def _replace_layout(layout, widget):
        while layout.count():
            item = layout.takeAt(0)
            old_widget = item.widget()
            if old_widget is not None:
                old_widget.deleteLater()
        layout.addWidget(widget)

    def _replace_splitter_widget(self, index, widget):
        previous = self.results_splitter.widget(index)
        previous.setParent(None)
        previous.deleteLater()
        self.results_splitter.insertWidget(index, widget)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Abrir dados termodinâmicos", "", _FILE_FILTER
        )
        if not file_name:
            return
        try:
            document = ReadData(file_name)
            self.dataframe = document.dataframe
            self.data = document.data
            self.species = document.species
            self.initial = document.initial
            self.components = np.asarray(document.components)
            self.file_path = file_name
            self._populate_table()
            self._populate_combos()
            self.btn_run.setEnabled(True)
            self.file_status.setText(file_name.replace("\\", "/").split("/")[-1])
            self.status_label.setText("Dados carregados. Configure e execute a simulação.")
        except (FileNotFoundError, ValueError, KeyError) as exc:
            QMessageBox.critical(self, "Erro ao abrir arquivo", str(exc))

    def _populate_table(self):
        self.table.setRowCount(len(self.dataframe))
        for row in range(len(self.dataframe)):
            component = QTableWidgetItem(str(self.dataframe["Component"].iloc[row]))
            initial = QTableWidgetItem(str(self.dataframe["initial"].iloc[row]))
            self.table.setItem(row, 0, component)
            self.table.setItem(row, 1, initial)
        self.component_count.setText(f"{len(self.components)} componentes")

    def _populate_combos(self):
        for combo in (self.component_combobox, self.inhibit_component_combox):
            combo.clear()
            combo.addItem("---")
            combo.addItems([str(component) for component in self.components])
            combo.setEnabled(True)

    def _on_component_changed(self, text):
        enabled = text not in {"", "---"}
        for widget in (
            self.min_value_input,
            self.max_value_input,
            self.n_values_n_input,
        ):
            widget.setEnabled(enabled)
        if hasattr(self, "total_scenarios"):
            self._update_scenario_preview()

    def _update_scenario_preview(self):
        try:
            n_temperature = int(self.n_values_t_input.text())
            n_pressure = int(self.n_values_p_input.text())
            has_reference = self.component_combobox.currentText() not in {"", "---"}
            n_component = int(self.n_values_n_input.text()) if has_reference else 1
            if min(n_temperature, n_pressure, n_component) < 1:
                raise ValueError
            total = n_temperature * n_pressure * n_component
            self.total_scenarios.setText(str(total))
            self.scenario_detail.setText(
                f"{n_temperature} × {n_pressure} × {n_component}"
            )
        except (ValueError, AttributeError):
            self.total_scenarios.setText("—")
            self.scenario_detail.setText("Preencha os valores da malha")


class GibbsSimulationScreen(SimulationScreen):
    def __init__(self):
        super().__init__("gibbs")


class EntropySimulationScreen(SimulationScreen):
    def __init__(self):
        super().__init__("entropy")

