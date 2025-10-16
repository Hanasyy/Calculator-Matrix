from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from file_utils import import_matrix, export_matrix
from quiz_utils import get_random_quiz

class MenuUtama(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked
        self.operands = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Kalkulator Matriks & SPL")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        btn1 = QPushButton("Input Matriks Grid")
        btn1.clicked.connect(lambda: self.goto_page(1))
        layout.addWidget(btn1)

        btn2 = QPushButton("Proses Operasi & SPL")
        btn2.clicked.connect(lambda: self.goto_page(2))
        layout.addWidget(btn2)

        btn3 = QPushButton("Import Matriks")
        btn3.clicked.connect(self.import_data)
        layout.addWidget(btn3)

        btn4 = QPushButton("Export Matriks")
        btn4.clicked.connect(self.export_data)
        layout.addWidget(btn4)

        btn5 = QPushButton("Quiz")
        btn5.clicked.connect(self.start_quiz)
        layout.addWidget(btn5)

        btn6 = QPushButton("Keluar")
        btn6.clicked.connect(lambda: self.close())
        layout.addWidget(btn6)

    def goto_page(self, index):
        self.stacked.setCurrentIndex(index)

    def import_data(self):
        file, _ = QFileDialog.getOpenFileName(self, "Import File Matriks", "", "Text Files (*.txt)")
        if file:
            self.operands.update(import_matrix(file))
            QMessageBox.information(self, "Sukses", "Matriks berhasil diimpor!")

    def export_data(self):
        file, _ = QFileDialog.getSaveFileName(self, "Simpan File Matriks", "", "Text Files (*.txt)")
        if file:
            export_matrix(file, self.operands)
            QMessageBox.information(self, "Sukses", "Matriks berhasil diekspor!")

    def start_quiz(self):
        q, options, ans = get_random_quiz()
        msg = QMessageBox(self)
        msg.setWindowTitle("Kuis Matematika")
        msg.setText(q)
        for opt in options:
            msg.addButton(opt, QMessageBox.ButtonRole.ActionRole)
        ret = msg.exec()
        chosen = options[ret] if ret < len(options) else None
        if chosen == ans:
            QMessageBox.information(self, "Benar!", "Jawaban kamu benar 🎉")
        else:
            QMessageBox.warning(self, "Salah", f"Jawaban salah! Yang benar: {ans}")
