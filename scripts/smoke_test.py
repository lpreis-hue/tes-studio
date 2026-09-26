"""Instantiate every screen without displaying a desktop window."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication

from app.ui.theme import APP_STYLESHEET
from main import MainWindow


app = QApplication.instance() or QApplication([])
app.setStyle("Fusion")
app.setStyleSheet(APP_STYLESHEET)
window = MainWindow()
assert window.stack.count() == 3, "As três telas principais devem estar disponíveis."
for index in range(window.stack.count()):
    window.navigate_to(index)
    assert window.stack.currentIndex() == index
window.close()
app.quit()
print("Smoke test da interface concluído.")
