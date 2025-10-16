from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout,
    QPushButton, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import numpy as np

class WindowInputGrid(QWidget):
    def __init__(self, parent_menu):
        super().__init__()
        self.parent_menu = parent_menu
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("Input Matriks")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Nama matriks
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nama matriks (contoh: A)")
        self.layout.addWidget(self.name_edit)

        # Ukuran matriks
        size_layout = QHBoxLayout()
        self.rows_edit = QLineEdit("3")
        self.cols_edit = QLineEdit("3")
        size_layout.addWidget(QLabel("Baris:"))
        size_layout.addWidget(self.rows_edit)
        size_layout.addWidget(QLabel("Kolom:"))
        size_layout.addWidget(self.cols_edit)
        self.layout.addLayout(size_layout)

        # Tombol buat grid
        self.btn_grid = QPushButton("Buat Grid Matriks")
        self.btn_grid.clicked.connect(self.create_grid)
        self.layout.addWidget(self.btn_grid)

        # Area grid untuk input elemen
        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        # Tombol simpan
        self.btn_save = QPushButton("Simpan Matriks")
        self.btn_save.clicked.connect(self.save_matrix)
        self.layout.addWidget(self.btn_save)

        # Tombol kembali ke menu
        self.btn_back = QPushButton("Kembali ke Menu")
        self.btn_back.clicked.connect(lambda: self.parent_menu.goto_page(0))
        self.layout.addWidget(self.btn_back)

        self.inputs = []

    def create_grid(self):
        # Bersihkan grid lama
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.inputs.clear()

        try:
            rows = int(self.rows_edit.text())
            cols = int(self.cols_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Masukkan angka valid untuk baris dan kolom.")
            return

        for i in range(rows):
            row_inputs = []
            for j in range(cols):
                le = QLineEdit("0")
                le.setFixedWidth(50)
                self.grid_layout.addWidget(le, i, j)
                row_inputs.append(le)
            self.inputs.append(row_inputs)

    def save_matrix(self):
        name = self.name_edit.text().strip()
        if not name or not name.isidentifier():
            QMessageBox.warning(self, "Error", "Nama matriks tidak valid.")
            return
        try:
            mat = [[float(cell.text()) for cell in row] for row in self.inputs]
            self.parent_menu.operands[name] = np.array(mat)
            QMessageBox.information(self, "Sukses", f"Matriks '{name}' berhasil disimpan.")
            self.parent_menu.goto_page(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan matriks: {e}")
