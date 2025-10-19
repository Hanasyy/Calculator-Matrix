# Calculator-Matrix/history_window.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QMessageBox, QHBoxLayout
)
from history import History
import json

class HistoryWindow(QWidget):
    def __init__(self, stacked=None, parent=None):
        super().__init__(parent)
        self.stacked = stacked
        self.history = History()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>History</h2>"))

        # Daftar history
        self.listw = QListWidget()
        layout.addWidget(self.listw)

        # Tombol refresh dan clear
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_history)
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        # Tombol kembali ke menu utama
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("Kembali ke Menu Utama")
        self.back_btn.clicked.connect(self.go_back)
        back_layout.addWidget(self.back_btn)
        layout.addLayout(back_layout)

        self.setLayout(layout)
        self.load_history()

    def load_history(self):
        """Menampilkan seluruh history"""
        self.listw.clear()
        items = self.history.all()
        if not items:
            self.listw.addItem("(no history)")
            return
        for it in items[::-1]:
            t = it.get("time", "")
            op = it.get("operation", "")
            status = it.get("status", "")
            summary = f"{t} | {op} | status={status}"
            self.listw.addItem(summary)

    def clear_history(self):
        """Hapus seluruh isi history"""
        choice = QMessageBox.question(self, "Clear history", "Yakin ingin mengosongkan history?")
        if choice != QMessageBox.StandardButton.Yes:
            return
        self.history.clear()
        self.load_history()

    def go_back(self):
        """Kembali ke menu utama"""
        if self.stacked is not None:
            self.stacked.setCurrentIndex(0)
