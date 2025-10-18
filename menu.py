from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class MenuUtama(QWidget):
    def __init__(self, stacked=None, parent=None):
        super().__init__(parent)
        self.stacked = stacked
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        title = QLabel("<h1>Matrix Calculator</h1>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        btn_layout = QVBoxLayout()

        # Buttons: Input, Process, Quiz, History, Exit
        self.btn_input = QPushButton("Input / Matrices")
        self.btn_proses = QPushButton("Process / Solver")
        self.btn_quiz = QPushButton("Quiz")
        self.btn_history = QPushButton("History")
        self.btn_exit = QPushButton("Exit")

        self.btn_input.clicked.connect(lambda: self.goto_page(1))
        self.btn_proses.clicked.connect(lambda: self.goto_page(2))
        self.btn_quiz.clicked.connect(lambda: self.goto_page(3))
        self.btn_history.clicked.connect(lambda: self.goto_page(4))
        self.btn_exit.clicked.connect(lambda: exit(0))

        for w in [self.btn_input, self.btn_proses, self.btn_quiz, self.btn_history, self.btn_exit]:
            btn_layout.addWidget(w)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def goto_page(self, idx):
        # idx is stacked index (0-based)
        if self.stacked is None:
            return
        try:
            # safeguard: only set if index exists
            if 0 <= idx < self.stacked.count():
                self.stacked.setCurrentIndex(idx)
        except Exception:
            pass
