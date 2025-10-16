from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTextEdit, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import numpy as np
from matrix_utils import cetak_matriks, solve_obe, solve_inverse, solve_cramer

class WindowProses(QWidget):
    def __init__(self, parent_menu):
        super().__init__()
        self.parent_menu = parent_menu
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("Operasi Matriks & SPL")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # ================== Ekspresi Matriks ==================
        self.layout.addWidget(QLabel("Ekspresi Matriks (+, -, *, @):"))
        self.expr_edit = QLineEdit()
        self.expr_edit.setPlaceholderText("Contoh ekspresi: A+B, A@B")
        self.layout.addWidget(self.expr_edit)

        self.btn_eval = QPushButton("Evaluasi Ekspresi")
        self.btn_eval.clicked.connect(self.eval_expr)
        self.layout.addWidget(self.btn_eval)

        # ================== Solver SPL ==================
        self.layout.addWidget(QLabel("Sistem Persamaan Linear (SPL)"))
        hb = QHBoxLayout()
        self.combo_A = QComboBox()
        self.combo_B = QComboBox()
        hb.addWidget(QLabel("Matriks A:"))
        hb.addWidget(self.combo_A)
        hb.addWidget(QLabel("Matriks B:"))
        hb.addWidget(self.combo_B)
        self.layout.addLayout(hb)

        self.method_box = QComboBox()
        self.method_box.addItems(["OBE", "Invers", "Cramer"])
        self.layout.addWidget(QLabel("Metode SPL:"))
        self.layout.addWidget(self.method_box)

        self.btn_spl = QPushButton("Hitung SPL")
        self.btn_spl.clicked.connect(self.calc_spl)
        self.layout.addWidget(self.btn_spl)

        # ================== Area Hasil ==================
        self.layout.addWidget(QLabel("Langkah-langkah:"))
        self.steps_area = QTextEdit()
        self.steps_area.setReadOnly(True)
        self.layout.addWidget(self.steps_area)

        self.layout.addWidget(QLabel("Hasil Akhir:"))
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.layout.addWidget(self.result_area)

        # Tombol kembali
        self.btn_back = QPushButton("Kembali ke Menu")
        self.btn_back.clicked.connect(lambda: self.parent_menu.goto_page(0))
        self.layout.addWidget(self.btn_back)

        self.refresh_combobox()

    def refresh_combobox(self):
        matrices = [k for k, v in self.parent_menu.operands.items() if isinstance(v, np.ndarray)]
        self.combo_A.clear()
        self.combo_B.clear()
        self.combo_A.addItems(matrices)
        self.combo_B.addItems(matrices)

    def eval_expr(self):
        expr = self.expr_edit.text().strip()
        if not expr:
            QMessageBox.warning(self, "Error", "Masukkan ekspresi matriks terlebih dahulu.")
            return
        try:
            res = eval(expr, {}, self.parent_menu.operands)
            if isinstance(res, np.ndarray):
                self.result_area.setPlainText(cetak_matriks(res))
            else:
                self.result_area.setPlainText(str(res))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def calc_spl(self):
        nameA = self.combo_A.currentText()
        nameB = self.combo_B.currentText()
        if not nameA or not nameB:
            QMessageBox.warning(self, "Error", "Pilih matriks A dan B terlebih dahulu.")
            return
        try:
            A = self.parent_menu.operands[nameA]
            B = self.parent_menu.operands[nameB]
            method = self.method_box.currentText()

            if method == "OBE":
                res, steps = solve_obe(A, B)
            elif method == "Invers":
                res, steps = solve_inverse(A, B)
            else:
                res, steps = solve_cramer(A, B)

            self.steps_area.clear()
            for s in steps:
                self.steps_area.append(s)
            self.result_area.setPlainText(cetak_matriks(res.reshape(-1, 1)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menghitung SPL: {e}")
