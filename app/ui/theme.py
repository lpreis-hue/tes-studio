"""Dark technical visual system for TeS Studio."""

APP_STYLESHEET = r"""
* {
    font-family: "Segoe UI";
    font-size: 12px;
}
QMainWindow, QWidget#appRoot, QFrame#contentArea, QWidget#simulationPage {
    background: #07131f;
    color: #dce8f2;
}
QFrame#sidebar {
    background: #07101c;
    border-right: 1px solid #1d3547;
}
QLabel#brandName {
    color: #26d4f2;
    font-size: 29px;
    font-weight: 800;
}
QLabel#brandStudio {
    color: #e8f4fb;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
}
QLabel#brandDescription, QLabel#versionLabel {
    color: #7892a6;
    font-size: 11px;
}
QLabel#sidebarSection {
    color: #58738a;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
}
QPushButton#navigationButton {
    color: #a9bfd0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 7px;
    padding: 11px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#navigationButton:hover {
    color: #eef8ff;
    background: #102536;
}
QPushButton#navigationButton:checked {
    color: #e9fbff;
    background: #0d3247;
    border-left: 3px solid #17c8eb;
}
QLabel#pageTitle {
    color: #eff8ff;
    font-size: 23px;
    font-weight: 700;
}
QLabel#pageSubtitle {
    color: #86a0b4;
    font-size: 12px;
}
QLabel#solverBadge {
    color: #54e68b;
    background: #0d2a25;
    border: 1px solid #176044;
    border-radius: 9px;
    padding: 7px 12px;
    font-size: 11px;
    font-weight: 700;
}
QStackedWidget#workspaceStack {
    background: transparent;
    border: none;
}
QFrame#simulationCard, QFrame#innerCard {
    background: #0c1d2b;
    border: 1px solid #203b4f;
    border-radius: 9px;
}
QLabel#cardHeading, QLabel#sectionTitle {
    color: #eff8ff;
    font-size: 14px;
    font-weight: 700;
}
QLabel#cardSubtitle, QLabel#mutedLabel, QLabel#metricSubtitle {
    color: #7894a9;
    font-size: 10px;
}
QLabel#fieldLabel {
    color: #b8ccdb;
    font-size: 10px;
}
QLabel#onlineStatus {
    color: #50df88;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusText {
    color: #a8bfce;
    font-size: 11px;
}
QLineEdit, QComboBox {
    color: #e5f0f7;
    background: #081722;
    border: 1px solid #315064;
    border-radius: 6px;
    padding: 6px 8px;
    min-height: 18px;
    selection-background-color: #1184b1;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #19c6e5;
}
QLineEdit:disabled, QComboBox:disabled {
    color: #516c7f;
    background: #0a1721;
    border-color: #1a3040;
}
QComboBox QAbstractItemView {
    color: #e5f0f7;
    background: #0b1b28;
    border: 1px solid #315064;
    selection-background-color: #0e789f;
}
QPushButton#primaryAction, QPushButton#plotAction {
    color: #eaffff;
    background: #087da3;
    border: 1px solid #16bad8;
    border-radius: 6px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton#primaryAction:hover, QPushButton#plotAction:hover {
    background: #0c98c5;
}
QPushButton#secondaryAction {
    color: #c6dce9;
    background: #112a3b;
    border: 1px solid #31546b;
    border-radius: 6px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton#secondaryAction:hover {
    color: white;
    background: #173b50;
    border-color: #23b8d4;
}
QPushButton#runAction {
    color: #f3fff7;
    background: #25b858;
    border: 1px solid #52df7c;
    border-radius: 7px;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#runAction:hover { background: #2dca64; }
QPushButton#runAction:pressed { background: #1c9948; }
QPushButton#runAction:disabled {
    color: #668378;
    background: #173328;
    border-color: #28513e;
}
QProgressBar#simulationProgress {
    color: #dff8ff;
    background: #071620;
    border: 1px solid #28485c;
    border-radius: 8px;
    text-align: center;
    min-height: 17px;
}
QProgressBar#simulationProgress::chunk {
    background: #1ed9b5;
    border-radius: 7px;
}
QFrame#scenarioSummary, QFrame#metricCard {
    background: #091824;
    border: 1px solid #1e3b4e;
    border-radius: 7px;
}
QLabel#metricTitle {
    color: #6f91a8;
    font-size: 9px;
    font-weight: 700;
}
QLabel#metricValue, QLabel#scenarioValue {
    color: #f1f9ff;
    font-size: 17px;
    font-weight: 700;
}
QTableWidget, QTableView {
    color: #d6e5ef;
    background: #081722;
    alternate-background-color: #0b1c29;
    border: 1px solid #244155;
    border-radius: 5px;
    gridline-color: #1c3648;
    selection-background-color: #0d6f91;
    selection-color: #ffffff;
}
QTableWidget::item, QTableView::item { padding: 4px; }
QHeaderView::section {
    color: #cce4f2;
    background: #102b3d;
    border: none;
    border-right: 1px solid #24485f;
    border-bottom: 1px solid #24485f;
    padding: 6px;
    font-size: 10px;
    font-weight: 700;
}
QTabWidget#resultTabs::pane {
    background: #0a1925;
    border: 1px solid #203b4f;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    color: #89a4b8;
    background: #0b1b28;
    border: 1px solid #203b4f;
    padding: 8px 20px;
    min-width: 90px;
}
QTabBar::tab:selected {
    color: #eaf9ff;
    background: #0d3146;
    border-bottom: 2px solid #20c7e5;
}
QFrame#emptyState {
    background: #0a1925;
    border: 1px dashed #29475a;
    border-radius: 7px;
}
QLabel#emptyStateText { color: #648297; }
QFrame#divider { color: #203b4f; }
QMessageBox { background: #0d1d2b; }
QMessageBox QLabel { color: #e3eff6; }
QMessageBox QPushButton {
    color: #e9f7fc;
    background: #14354a;
    border: 1px solid #2c607a;
    border-radius: 5px;
    padding: 6px 14px;
}
QScrollBar:vertical {
    background: #071620;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #29495e;
    min-height: 25px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QStatusBar {
    color: #7793a8;
    background: #07101c;
    border-top: 1px solid #1d3547;
    font-size: 10px;
}
"""

