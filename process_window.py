from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
    QFileDialog, QMessageBox, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
import os, json, numpy as np

from matrix_utils import (
    solve_obe, cetak_matriks, solve_homogeneous,
    det, inverse, rref_with_steps
)
from history import History


class WindowProses(QWidget):
    """
    Halaman proses utama:
    - Menjalankan operasi matriks (Solve OBE, Homogen, Determinan, Invers, RREF)
    - Menyimpan hasil ke history
    - Menyimpan & memuat test case (dinamis)
    """
    def __init__(self, stacked=None, parent=None):
        super().__init__(parent)
        self.stacked = stacked
        self.history = History()
        self.tests_file = os.path.join(os.path.dirname(__file__), "user_tests.json")
        self._build_ui()
        self.last_result = None
        self.last_steps = None
        self.last_status = None

    # ====================================================
    # BUILD UI
    # ====================================================
    def _build_ui(self):
        layout = QVBoxLayout()
        title = QLabel("<h2>Process / Solver (Dynamic Test Enabled)</h2>")
        layout.addWidget(title)

        # Pilihan operasi
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Pilih Operasi:"))
        self.op_combo = QComboBox()
        self.op_combo.addItems([
            "Solve Non-homogeneous (A·x = B)",
            "Solve Homogeneous (A·x = 0)",
            "RREF Only",
            "Determinant of A",
            "Inverse of A"
        ])
        op_layout.addWidget(self.op_combo)
        layout.addLayout(op_layout)

        # Input Matriks A
        in_box = QGroupBox("Input Matriks / Vektor")
        in_layout = QVBoxLayout()
        lblA = QLabel("Matriks A:")
        self.textA = QTextEdit()
        self.textA.setPlaceholderText("contoh:\n2 -1 0 3\n1 4 -2 0\n0 5 3 -1\n2 0 1 2")
        in_layout.addWidget(lblA)
        in_layout.addWidget(self.textA)

        lblB = QLabel("Vektor B (opsional):")
        self.textB = QTextEdit()
        self.textB.setPlaceholderText("contoh:\n9 11 4 7")
        in_layout.addWidget(lblB)
        in_layout.addWidget(self.textB)
        in_box.setLayout(in_layout)
        layout.addWidget(in_box)

        # Tombol aksi
        btn_layout = QHBoxLayout()
        self.solve_btn = QPushButton("Run Operation")
        self.solve_btn.clicked.connect(self.on_run)
        self.export_btn = QPushButton("Export Steps...")
        self.export_btn.clicked.connect(self.on_export)
        self.save_btn = QPushButton("Save Test Case")
        self.save_btn.clicked.connect(self.on_save_case)
        self.load_btn = QPushButton("Load Last Case")
        self.load_btn.clicked.connect(self.on_load_case)
        self.save_hist_btn = QPushButton("Save Result to History")
        self.save_hist_btn.clicked.connect(self.on_save_history)
        for b in [self.solve_btn, self.export_btn, self.save_btn, self.load_btn, self.save_hist_btn]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        # Output steps
        self.steps_area = QTextEdit()
        self.steps_area.setReadOnly(True)
        self.steps_area.setPlaceholderText("Langkah dan hasil operasi akan tampil di sini...")
        layout.addWidget(self.steps_area, stretch=1)

        self.setLayout(layout)

    # ====================================================
    # PARSE
    # ====================================================
    def parse_matrix(self, txt):
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if not lines:
            return None
        mat = [[float(x) for x in ln.split()] for ln in lines]
        cols = {len(r) for r in mat}
        if len(cols) != 1:
            raise ValueError("Jumlah kolom tiap baris tidak konsisten.")
        return np.array(mat, dtype=float)

    def parse_vector(self, txt):
        if not txt.strip():
            return None
        vals = []
        for ln in txt.splitlines():
            if ln.strip():
                vals.extend(ln.split())
        return np.array([float(v) for v in vals], dtype=float)

    # ====================================================
    # EVENT HANDLERS
    # ====================================================
    def on_run(self):
        """ Jalankan operasi sesuai pilihan """
        try:
            A = self.parse_matrix(self.textA.toPlainText())
            if A is None:
                QMessageBox.warning(self, "Input error", "Matriks A belum diisi.")
                return
            B = self.parse_vector(self.textB.toPlainText())
            op = self.op_combo.currentText()
            out = []

            if op == "Solve Non-homogeneous (A·x = B)":
                if B is None:
                    QMessageBox.warning(self, "Input error", "Vektor B diperlukan untuk operasi ini.")
                    return
                res, steps, status = solve_obe(A, B)
                out.append(f"Status: {status}\n")
                out.extend(steps)
                if status == "unique":
                    out.append(f"\nSolution:\n{res}")
                elif status == "infinite":
                    particular, free_vars, basis = res
                    out.append(f"\nParticular: {particular}")
                    out.append(f"Free vars: {free_vars}")
                    for i, v in enumerate(basis):
                        out.append(f"t{i+1} basis: {v}")
                elif status == "inconsistent":
                    out.append("No solution (inconsistent).")

            elif op == "Solve Homogeneous (A·x = 0)":
                free_vars, basis = solve_homogeneous(A)
                if not basis:
                    out.append("Hanya solusi trivial (x=0).")
                else:
                    out.append(f"Free vars: {free_vars}")
                    for i, v in enumerate(basis):
                        out.append(f"Basis vector {i+1}: {v}")

            elif op == "RREF Only":
                R, piv, steps = rref_with_steps(A)
                out.append("RREF Result:\n" + cetak_matriks(R))
                out.append("\nSteps:")
                out.extend(steps)

            elif op == "Determinant of A":
                out.append(f"det(A) = {det(A)}")

            elif op == "Inverse of A":
                invA = inverse(A)
                out.append("A⁻¹ =\n" + cetak_matriks(invA))

            else:
                out.append("Operasi belum diimplementasikan.")

            self.steps_area.setPlainText("\n".join(out))
            self.last_result = {"operation": op, "output": out}
            self.last_steps = out
            self.last_status = "ok"
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{e}")

    def on_export(self):
        if not self.last_steps:
            QMessageBox.information(self, "No steps", "Tidak ada hasil untuk diexport.")
            return
        fn, _ = QFileDialog.getSaveFileName(
            self, "Export Steps to TXT", filter="Text Files (*.txt);;All Files (*)"
        )
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write("\n".join(self.last_steps))
            QMessageBox.information(self, "Exported", f"Langkah disimpan ke {fn}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export: {e}")

    def on_save_case(self):
        """ Simpan test case ke user_tests.json """
        try:
            data = {
                "A": self.textA.toPlainText().strip(),
                "B": self.textB.toPlainText().strip(),
                "operation": self.op_combo.currentText()
            }
            if os.path.exists(self.tests_file):
                with open(self.tests_file, "r") as f:
                    arr = json.load(f)
            else:
                arr = []
            arr.append(data)
            with open(self.tests_file, "w") as f:
                json.dump(arr, f, indent=2)
            QMessageBox.information(self, "Saved", "Test case disimpan ke user_tests.json")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def on_load_case(self):
        """ Muat test case terakhir dari user_tests.json """
        if not os.path.exists(self.tests_file):
            QMessageBox.warning(self, "No file", "Belum ada test case tersimpan.")
            return
        try:
            with open(self.tests_file, "r") as f:
                arr = json.load(f)
            if not arr:
                QMessageBox.information(self, "Empty", "Belum ada test case tersimpan.")
                return
            last = arr[-1]
            self.textA.setPlainText(last.get("A", ""))
            self.textB.setPlainText(last.get("B", ""))
            op = last.get("operation", "")
            idx = self.op_combo.findText(op)
            if idx >= 0:
                self.op_combo.setCurrentIndex(idx)
            QMessageBox.information(self, "Loaded", "Test case terakhir berhasil dimuat.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat: {e}")

    def on_save_history(self):
        if not self.last_result:
            QMessageBox.information(self, "No result", "Belum ada hasil yang bisa disimpan ke history.")
            return
        self.history.add({
            "operation": self.last_result.get("operation"),
            "result": self.last_result.get("output")[:6],
        })
        QMessageBox.information(self, "Saved", "Hasil disimpan ke history.")
