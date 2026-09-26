"""TeS Studio desktop application entry point."""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.find_path import resource_path
from app.ui.theme import APP_STYLESHEET


class MainWindow(QMainWindow):
    """Application shell. Numerical screens remain isolated from navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"TeS Studio {__version__}")
        self.setWindowIcon(QIcon(resource_path("ico.ico")))
        self.setMinimumSize(1050, 720)
        self.resize(1280, 840)

        root = QWidget(objectName="appRoot")
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_sidebar())

        content = QFrame(objectName="contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 22, 28, 24)
        content_layout.setSpacing(16)
        content_layout.addLayout(self._build_header())

        self.stack = QStackedWidget(objectName="workspaceStack")
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        content_layout.addWidget(self.stack, 1)
        root_layout.addWidget(content, 1)

        self._load_screens()
        self.navigate_to(0)
        self.statusBar().showMessage("Pronto")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(264)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(10)

        brand = QLabel("TeS", objectName="brandName")
        brand.setAccessibleName("TeS Studio")
        layout.addWidget(brand)
        layout.addWidget(QLabel("STUDIO", objectName="brandStudio"))
        layout.addWidget(
            QLabel(
                "Equilíbrio termodinâmico\ncom solver IPOPT",
                objectName="brandDescription",
            )
        )
        layout.addSpacing(22)
        layout.addWidget(QLabel("NAVEGAÇÃO", objectName="sidebarSection"))

        self.navigation_group = QButtonGroup(self)
        self.navigation_group.setExclusive(True)
        self.navigation_buttons: list[QPushButton] = []
        labels = (
            "Visão geral",
            "Minimização de Gibbs",
            "Maximização de entropia",
        )
        for index, label in enumerate(labels):
            button = QPushButton(label, objectName="navigationButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, i=index: self.navigate_to(i))
            self.navigation_group.addButton(button, index)
            self.navigation_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch(1)
        layout.addWidget(QLabel(f"Versão {__version__}", objectName="versionLabel"))
        return sidebar

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.page_title = QLabel(objectName="pageTitle")
        self.page_subtitle = QLabel(objectName="pageSubtitle")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_subtitle)
        layout.addLayout(titles)
        layout.addStretch(1)

        solver_badge = QLabel("IPOPT", objectName="solverBadge")
        solver_badge.setToolTip("Interior Point OPTimizer")
        layout.addWidget(solver_badge, alignment=Qt.AlignmentFlag.AlignTop)
        return layout

    def _load_screens(self) -> None:
        # Deferred imports allow startup to report missing solver dependencies.
        from app.screens.initial import InitialScreen
        from app.screens.maxs import MaxS
        from app.screens.ming import MinG

        self.initial_screen = InitialScreen()
        self.ming_screen = MinG()
        self.maxs_screen = MaxS()
        self.initial_screen.open_method_requested.connect(self.navigate_to)

        for screen in (self.initial_screen, self.ming_screen, self.maxs_screen):
            self.stack.addWidget(screen)

    def navigate_to(self, index: int) -> None:
        """Switch screens and keep the navigation state synchronized."""
        if not 0 <= index < self.stack.count():
            return

        titles = (
            ("Visão geral", "Escolha um método e prepare sua simulação."),
            ("Minimização de Gibbs", "Equilíbrio a temperatura e pressão definidas."),
            ("Maximização de entropia", "Equilíbrio para energia e volume definidos."),
        )
        self.stack.setCurrentIndex(index)
        self.navigation_buttons[index].setChecked(True)
        self.page_title.setText(titles[index][0])
        self.page_subtitle.setText(titles[index][1])
        self.statusBar().showMessage(titles[index][0])


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("TeS Studio")
    app.setApplicationDisplayName("TeS Studio")
    app.setOrganizationName("TeS")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    try:
        window = MainWindow()
    except Exception as exc:  # pragma: no cover - desktop startup safeguard
        QMessageBox.critical(
            None,
            "TeS Studio não pôde iniciar",
            "Falha ao carregar os módulos do aplicativo.\n\n"
            f"Detalhes: {exc}\n\n"
            "Verifique a instalação do IPOPT/cyipopt e consulte o guia de build.",
        )
        return 1

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
