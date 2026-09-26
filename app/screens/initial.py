from pathlib import Path

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.find_path import resource_path

class InitialScreen(QWidget):
    """Landing page for choosing an equilibrium method."""

    open_method_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("overviewPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        hero = QFrame(objectName="overviewHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 18, 24, 18)

        text_layout = QVBoxLayout()
        title = QLabel("Thermodynamic Equilibrium Simulation", objectName="heroTitle")
        subtitle = QLabel(
            "Configure, execute e compare simulações de equilíbrio em um fluxo único.",
            objectName="heroSubtitle",
        )
        subtitle.setWordWrap(True)
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        text_layout.addStretch(1)
        hero_layout.addLayout(text_layout, 1)

        image_label = QLabel(objectName="heroImage")
        pixmap = QPixmap(resource_path("app/imgs/initial_v3.png"))
        image_label.setPixmap(
            pixmap.scaled(
                300,
                160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(image_label)
        layout.addWidget(hero)

        methods = QGridLayout()
        methods.setHorizontalSpacing(16)
        methods.addWidget(
            self._method_card(
                "Minimização de Gibbs",
                "Calcule o equilíbrio com temperatura e pressão especificadas.",
                "Abrir módulo Gibbs",
                1,
            ),
            0,
            0,
        )
        methods.addWidget(
            self._method_card(
                "Maximização de entropia",
                "Calcule o equilíbrio com energia interna e volume especificados.",
                "Abrir módulo Entropia",
                2,
            ),
            0,
            1,
        )
        layout.addLayout(methods)
        layout.addStretch(1)

        footer = QHBoxLayout()
        footer.addWidget(QLabel("Recursos", objectName="footerLabel"))
        footer.addStretch(1)
        doc_button = QPushButton("Abrir documentação", objectName="secondaryButton")
        doc_button.clicked.connect(self.open_documentation)
        contact_button = QPushButton("Contato", objectName="secondaryButton")
        contact_button.clicked.connect(self.show_contact_message)
        footer.addWidget(doc_button)
        footer.addWidget(contact_button)
        layout.addLayout(footer)

        self.setStyleSheet(self._styles())

    def _method_card(self, title, description, button_text, page_index):
        card = QFrame(objectName="methodCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(10)

        title_label = QLabel(title, objectName="cardTitle")
        description_label = QLabel(description, objectName="cardDescription")
        description_label.setWordWrap(True)
        open_button = QPushButton(button_text, objectName="primaryButton")
        open_button.clicked.connect(
            lambda _checked=False, index=page_index: self.open_method_requested.emit(index)
        )
        card_layout.addWidget(title_label)
        card_layout.addWidget(description_label)
        card_layout.addStretch(1)
        card_layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignLeft)
        return card

    def open_documentation(self):
        pdf_path = Path(resource_path("app/files/TeS.pdf"))
        if pdf_path.exists():
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path))):
                QMessageBox.warning(
                    self, "Documentação", "Não foi possível abrir o leitor de PDF."
                )
        else:
            QMessageBox.warning(self, "Documentação", "Arquivo TeS.pdf não encontrado.")

    def show_contact_message(self):
        txt_path = Path(resource_path("app/files/msg.txt"))
        try:
            message = txt_path.read_text(encoding="utf-8")
            QMessageBox.information(self, "Contato", message)
        except FileNotFoundError:
            QMessageBox.warning(
                self, "Contato", f"Arquivo de contato não encontrado em: {txt_path}"
            )

    @staticmethod
    def _styles():
        return """
        QWidget#overviewPage { background: #ffffff; }
        QFrame#overviewHero {
            background: #ecfeff; border: 1px solid #a5f3fc; border-radius: 12px;
        }
        QLabel#heroTitle { color: #164e63; font-size: 21px; font-weight: 700; }
        QLabel#heroSubtitle { color: #475569; font-size: 13px; }
        QFrame#methodCard {
            background: #f8fafc; border: 1px solid #dbe3ef; border-radius: 10px;
            min-height: 150px;
        }
        QLabel#cardTitle { color: #0f172a; font-size: 16px; font-weight: 700; }
        QLabel#cardDescription { color: #64748b; font-size: 12px; }
        QLabel#footerLabel { color: #475569; font-size: 12px; font-weight: 600; }
        QPushButton#primaryButton {
            color: white; background: #0e7490; border: none; border-radius: 7px;
            padding: 9px 14px; font-weight: 600;
        }
        QPushButton#primaryButton:hover { background: #0891b2; }
        QPushButton#secondaryButton {
            color: #155e75; background: #ffffff; border: 1px solid #a5f3fc;
            border-radius: 7px; padding: 8px 13px; font-weight: 600;
        }
        QPushButton#secondaryButton:hover { background: #ecfeff; }
        """
