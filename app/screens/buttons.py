class Button:
    """Legacy-compatible button style provider used by calculation screens."""

    def __init__(self):
        self.active_button = None

    @classmethod
    def css(cls):
        return """
        QPushButton {
            color: white;
            background-color: #0e7490;
            border: 1px solid #0e7490;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #0891b2;
            border-color: #0891b2;
        }
        QPushButton:pressed {
            background-color: #155e75;
        }
        QPushButton:disabled {
            color: #cbd5e1;
            background-color: #94a3b8;
            border-color: #94a3b8;
        }
        """
