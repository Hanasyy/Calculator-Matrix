from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
    QFileDialog, QMessageBox, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
import os, json, numpy as np

from matrix_utils import (
    solve_obe, cetak_matriks, solve_homogeneous,
    det, inverse, rref_with_steps,
    norm, projection, angle_between
)
from history import History


class WindowProses(QWidget):
    """
    Halaman utama proses kalkulator matriks dan vektor.
    Terhubung otomatis dengan hasil input dari WindowInputGrid.
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
        title = QLabel("<h2>Proses Perhitungan Matriks dan Vektor</h2>")
        layout.addWidget(title)

        # Pilihan operasi
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Pilih Operasi:"))
        self.op_combo = QComboBox()
        self.op_combo.addItems([
            "Non-homogen (A·x = B)",
            "Homogen (A·x = 0)",
            "OBE",
            "Determinan A",
            "Determinan B",
            "Inverse A",
            "Inverse B",
            "A + B",
            "A - B",
            "A × B",
            "B × A",
            "Transpose (Aᵗ)",
            "Transpose (Bᵗ)",
            "Pengenalan Jenis Matriks A",
            "Pengenalan Jenis Matriks B",
            "Penjumlahan Vektor",
            "Pengurangan Vektor",
            "Dot Product (A·B)",
            "Cross Product (A×B)",
            "Panjang (Norma) Vektor u",
            "Panjang (Norma) Vektor v",
            "Proyeksi u ke arah v",
            "Sudut antara u dan v"
        ])
        op_layout.addWidget(self.op_combo)
        layout.addLayout(op_layout)

        # Input area
        in_box = QGroupBox("Input Matriks / Vektor")
        in_layout = QVBoxLayout()

        lblA = QLabel("Matriks / Vektor A:")
        in_layout.addWidget(lblA)

        self.comboA = QComboBox()
        self.comboA.addItem("(Belum ada matriks tersimpan)")
        in_layout.addWidget(self.comboA)

        self.textA = QTextEdit()
        self.textA.setPlaceholderText("contoh matriks:\n1 2 3\n4 5 6\natau vektor:\n1 2 3")
        in_layout.addWidget(self.textA)

        lblB = QLabel("Matriks / Vektor B (opsional):")
        in_layout.addWidget(lblB)

        self.comboB = QComboBox()
        self.comboB.addItem("(Belum ada matriks tersimpan)")
        in_layout.addWidget(self.comboB)

        self.textB = QTextEdit()
        self.textB.setPlaceholderText("contoh:\n7 8 9")
        in_layout.addWidget(self.textB)

        in_box.setLayout(in_layout)
        layout.addWidget(in_box)

        # Tombol aksi utama
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
        self.refresh_btn = QPushButton("Refresh Daftar Matriks")
        self.refresh_btn.clicked.connect(self.refresh_matrix_list)

        for b in [self.solve_btn, self.export_btn, self.save_btn, self.load_btn, self.save_hist_btn, self.refresh_btn]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        # Output area
        self.steps_area = QTextEdit()
        self.steps_area.setReadOnly(True)
        self.steps_area.setPlaceholderText("Langkah dan hasil operasi akan tampil di sini...")
        font = self.steps_area.font()
        font.setPointSize(12)
        self.steps_area.setFont(font)
        self.steps_area.setMinimumHeight(120)
        layout.addWidget(self.steps_area, stretch=2)

        # Tombol kembali ke menu
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("Kembali ke Menu Utama")
        self.back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
        back_layout.addWidget(self.back_btn)
        layout.addLayout(back_layout)

        self.setLayout(layout)


    # ====================================================
    # REFRESH DROPDOWN MATRIX LIST
    # ====================================================
    def refresh_matrix_list(self):
        """Ambil matriks tersimpan dari halaman input"""
        self.comboA.clear()
        self.comboB.clear()

        if hasattr(self.stacked, "matrices") and self.stacked.matrices:
            names = list(self.stacked.matrices.keys())
            self.comboA.addItem("(Pilih matriks tersimpan atau ketik manual)")
            self.comboB.addItem("(Pilih matriks tersimpan atau ketik manual)")
            self.comboA.addItems(names)
            self.comboB.addItems(names)
        else:
            self.comboA.addItem("(Belum ada matriks tersimpan)")
            self.comboB.addItem("(Belum ada matriks tersimpan)")


    # ====================================================
    # PARSING INPUT
    # ====================================================
    def parse_matrix(self, txt):
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        mat = [[float(x) for x in ln.split()] for ln in lines]
        return np.array(mat, dtype=float)

    def parse_vector(self, txt):
        vals = [float(x) for x in txt.split()]
        return np.array(vals, dtype=float)


    # ====================================================
    # OPERASI UTAMA
    # ====================================================
    def on_run(self):
        try:
            op = self.op_combo.currentText()
            out = []

            # --- Ambil matriks A ---
            if self.comboA.currentIndex() > 0:
                A = self.stacked.matrices[self.comboA.currentText()]
            else:
                txtA = self.textA.toPlainText().strip()
                A = self.parse_matrix(txtA) if "\n" in txtA else self.parse_vector(txtA)

            # --- Ambil matriks B ---
            B = None
            if self.comboB.currentIndex() > 0:
                B = self.stacked.matrices[self.comboB.currentText()]
            elif self.textB.toPlainText().strip():
                txtB = self.textB.toPlainText().strip()
                B = self.parse_matrix(txtB) if "\n" in txtB else self.parse_vector(txtB)

            # ==== operasi ====
            if op == "Non-homogen (A·x = B)":
                res, steps, status = solve_obe(A, B)
                out.append(f"Status: {status}")
                out.extend(steps)

            elif op == "Homogen (A·x = 0)":
                free_vars, basis = solve_homogeneous(A)
                if not basis:
                    out.append("Hanya solusi trivial (x=0).")
                else:
                    out.append(f"Free vars: {free_vars}")
                    for i, v in enumerate(basis):
                        out.append(f"Basis vector {i+1}: {v}")

            elif op == "A + B":
                out.append("A + B =\n" + cetak_matriks(A + B))
            elif op == "A - B":
                out.append("A - B =\n" + cetak_matriks(A - B))
            elif op == "A × B":
                out.append("A × B =\n" + cetak_matriks(A @ B))
            elif op == "B × A":
                out.append("B × A =\n" + cetak_matriks(B @ A))
            elif op == "Transpose (Aᵗ)":
                out.append("Aᵗ =\n" + cetak_matriks(A.T))
            elif op == "Transpose (Bᵗ)":
                out.append("Bᵗ =\n" + cetak_matriks(B.T))
            elif op == "Determinan A":
                out.append(f"det(A) = {det(A)}")
            elif op == "Determinan B":
                out.append(f"det(B) = {det(B)}")
            elif op == "Inverse A":
                out.append("A⁻¹ =\n" + cetak_matriks(inverse(A)))
            elif op == "Inverse B":
                out.append("B⁻¹ =\n" + cetak_matriks(inverse(B)))
            elif op == "OBE":
                R, piv, steps = rref_with_steps(A)
                out.append("Hasil OBE:\n" + cetak_matriks(R))
                out.extend(steps)
            elif op == "Pengenalan Jenis Matriks A":
                info = self.analyze_matrix(A, "A")
                out.extend(info)
            elif op == "Pengenalan Jenis Matriks B":
                info = self.analyze_matrix(B, "B")
                out.extend(info)
            elif op == "Penjumlahan Vektor":
                out.append(f"A + B = {A + B}")
            elif op == "Pengurangan Vektor":
                out.append(f"A - B = {A - B}")
            elif op == "Dot Product (A·B)":
                out.append(f"A·B = {np.dot(A, B)}")
            elif op == "Cross Product (A×B)":
                out.append(f"A×B = {np.cross(A, B)}")
            elif op == "Panjang (Norma) Vektor A":
                out.append(f"‖A‖ = {norm(A):.6f}")
            elif op == "Panjang (Norma) Vektor B":
                out.append(f"‖B‖ = {norm(B):.6f}")
            elif op == "Proyeksi u ke arah v":
                proj = projection(A, B)
                out.append(f"Proyeksi A ke arah B = {proj}")
            elif op == "Sudut antara u dan v":
                theta = angle_between(A, B)
                out.append(f"Sudut antara A dan B = {np.degrees(theta):.4f}°")

            self.steps_area.setPlainText("\n".join(out))
            self.last_steps = out

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def analyze_matrix(self, M, label="A"):
        """Analisis jenis matriks"""
        info = [f"Jenis Matriks {label}:"]
        rows, cols = M.shape
        info.append(f"Ukuran: {rows}×{cols}")
        if rows == cols:
            info.append("Persegi")
            if np.allclose(M, np.eye(rows)): info.append("Identitas")
            if np.allclose(M, M.T): info.append("Simetris")
            if np.allclose(M, np.triu(M)): info.append("Segitiga Atas")
            if np.allclose(M, np.tril(M)): info.append("Segitiga Bawah")
            if np.count_nonzero(M - np.diag(np.diag(M))) == 0: info.append("Diagonal")
            info.append("Singular (det=0)" if round(det(M)) == 0 else "Non-Singular (det≠0)")
        else:
            info.append("Bukan persegi")
        return info


    # ====================================================
    # EXPORT / SAVE / LOAD / HISTORY
    # ====================================================
    def on_export(self):
        if not self.last_steps:
            QMessageBox.information(self, "No steps", "Tidak ada hasil untuk diexport.")
            return
        fn, _ = QFileDialog.getSaveFileName(self, "Export Steps", filter="Text Files (*.txt)")
        if not fn: return
        with open(fn, "w", encoding="utf-8") as f:
            f.write("\n".join(self.last_steps))
        QMessageBox.information(self, "Exported", f"Hasil disimpan di {fn}")

    def on_save_case(self):
        try:
            data = {
                "A": self.textA.toPlainText().strip(),
                "B": self.textB.toPlainText().strip(),
                "operation": self.op_combo.currentText()
            }
            arr = []
            if os.path.exists(self.tests_file):
                with open(self.tests_file, "r") as f:
                    arr = json.load(f)
            arr.append(data)
            with open(self.tests_file, "w") as f:
                json.dump(arr, f, indent=2)
            QMessageBox.information(self, "Saved", "Test case disimpan ke user_tests.json")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def on_load_case(self):
        if not os.path.exists(self.tests_file):
            QMessageBox.warning(self, "No file", "Belum ada test case tersimpan.")
            return
        with open(self.tests_file, "r") as f:
            arr = json.load(f)
        if not arr:
            QMessageBox.information(self, "Empty", "Belum ada test case.")
            return
        last = arr[-1]
        self.textA.setPlainText(last.get("A", ""))
        self.textB.setPlainText(last.get("B", ""))
        idx = self.op_combo.findText(last.get("operation", ""))
        if idx >= 0:
            self.op_combo.setCurrentIndex(idx)
        QMessageBox.information(self, "Loaded", "Test case terakhir berhasil dimuat.")

    def on_save_history(self):
        if not self.last_steps:
            QMessageBox.information(self, "No result", "Belum ada hasil yang bisa disimpan ke history.")
            return
        self.history.add({"operation": self.op_combo.currentText(), "result": self.last_steps[:8]})
        QMessageBox.information(self, "Saved", "Hasil disimpan ke history.")
