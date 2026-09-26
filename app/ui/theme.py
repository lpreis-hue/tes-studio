"""Application-level theme scoped to the TeS Studio shell."""

APP_STYLESHEET = """
QMainWindow, QWidget#appRoot { background: #f3f6fb; }
QFrame#sidebar { background: #0b1220; border: none; }
QLabel#brandName {
    color: #38bdf8; font-family: "Segoe UI"; font-size: 32px; font-weight: 800;
}
QLabel#brandStudio {
    color: #f8fafc; font-family: "Segoe UI"; font-size: 13px;
    font-weight: 700; letter-spacing: 4px;
}
QLabel#brandDescription, QLabel#versionLabel {
    color: #94a3b8; font-family: "Segoe UI"; font-size: 12px;
}
QLabel#sidebarSection {
    color: #64748b; font-family: "Segoe UI"; font-size: 10px;
    font-weight: 700; letter-spacing: 1px;
}
QPushButton#navigationButton {
    color: #cbd5e1; background: transparent; border: 1px solid transparent;
    border-radius: 8px; padding: 12px 14px; text-align: left;
    font-family: "Segoe UI"; font-size: 13px; font-weight: 600;
}
QPushButton#navigationButton:hover { color: #f8fafc; background: #162033; }
QPushButton#navigationButton:checked {
    color: #ecfeff; background: #0e7490; border-color: #22d3ee;
}
QFrame#contentArea { background: #f3f6fb; }
QLabel#pageTitle {
    color: #0f172a; font-family: "Segoe UI"; font-size: 25px; font-weight: 700;
}
QLabel#pageSubtitle {
    color: #64748b; font-family: "Segoe UI"; font-size: 13px;
}
QLabel#solverBadge {
    color: #155e75; background: #cffafe; border: 1px solid #a5f3fc;
    border-radius: 10px; padding: 7px 12px; font-family: "Segoe UI";
    font-size: 11px; font-weight: 700;
}
QStackedWidget#workspaceStack {
    background: #ffffff; border: 1px solid #dbe3ef; border-radius: 12px;
}
QStatusBar {
    color: #64748b; background: #ffffff; border-top: 1px solid #dbe3ef;
    font-family: "Segoe UI"; font-size: 11px;
}
"""
