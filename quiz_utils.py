import json
import os
import random
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton,
    QMessageBox, QButtonGroup, QLineEdit, QTextEdit, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt


class QuizWindow(QWidget):
    def __init__(self, quiz_file_path):
        super().__init__()
        self.setWindowTitle("Kuis Kalkulator Matriks")
        self.resize(550, 400)

        self.quiz_file_path = quiz_file_path
        self.questions = self.load_questions(quiz_file_path)
        if not self.questions:
            QMessageBox.warning(self, "Error", "Tidak ada pertanyaan ditemukan.")
            self.close()
            return

        random.shuffle(self.questions)
        self.current_index = 0
        self.score = 0

        # --- Layout utama ---
        self.layout = QVBoxLayout()
        self.question_label = QLabel()
        self.option_group = QButtonGroup(self)
        self.option_buttons = []

        for _ in range(4):
            btn = QRadioButton()
            self.layout.addWidget(btn)
            self.option_buttons.append(btn)
            self.option_group.addButton(btn)

        # --- Tombol kontrol kuis ---
        btn_layout = QHBoxLayout()
        self.next_button = QPushButton("Selanjutnya")
        self.add_button = QPushButton("Tambah Pertanyaan")
        self.import_button = QPushButton("Import Soal")
        self.export_button = QPushButton("Export Soal")

        self.next_button.clicked.connect(self.next_question)
        self.add_button.clicked.connect(self.open_add_question_window)
        self.import_button.clicked.connect(self.import_questions)
        self.export_button.clicked.connect(self.export_questions)

        btn_layout.addWidget(self.next_button)
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.import_button)
        btn_layout.addWidget(self.export_button)

        self.layout.addWidget(self.question_label)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

        self.load_question()

    # -------------------- BAGIAN FUNGSI UTAMA --------------------

    def load_questions(self, path):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Gagal memuat file kuis: {e}")
            return []


    def save_questions(self):
        """Simpan ulang pertanyaan ke file utama."""
        try:
            with open(self.quiz_file_path, "w", encoding="utf-8") as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menyimpan file: {e}")

    def load_question(self):
        """Tampilkan pertanyaan saat ini."""
        if self.current_index >= len(self.questions):
            self.show_result()
            return

        q = self.questions[self.current_index]
        self.question_label.setText(f"{self.current_index+1}. {q['q']}")
        for i, opt in enumerate(q["options"]):
            self.option_buttons[i].setText(opt)
            self.option_buttons[i].setChecked(False)

    def next_question(self):
        """Periksa jawaban dan lanjut ke pertanyaan berikutnya."""
        selected = None
        for btn in self.option_buttons:
            if btn.isChecked():
                selected = btn.text()
                break

        if selected is None:
            QMessageBox.warning(self, "Peringatan", "Pilih salah satu jawaban dulu!")
            return

        correct = self.questions[self.current_index]["answer"]
        if selected == correct:
            self.score += 1

        self.current_index += 1
        if self.current_index < len(self.questions):
            self.load_question()
        else:
            self.show_result()

    def show_result(self):
        """Tampilkan skor akhir."""
        QMessageBox.information(
            self,
            "Hasil Kuis",
            f"Kuis selesai!\nSkor kamu: {self.score}/{len(self.questions)}"
        )
        self.close()

    # -------------------- FITUR TAMBAHAN --------------------

    def open_add_question_window(self):
        """Buka jendela untuk menambah pertanyaan baru."""
        self.add_window = AddQuizWindow(self.quiz_file_path, self)
        self.add_window.show()

    def import_questions(self):
        """Import soal dari file JSON lain."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Soal untuk Diimport", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_questions = json.load(f)

            # Validasi struktur data
            if not isinstance(imported_questions, list):
                raise ValueError("Format file tidak valid (harus berupa list).")

            self.questions.extend(imported_questions)
            self.save_questions()

            QMessageBox.information(
                self, "Berhasil", f"{len(imported_questions)} pertanyaan berhasil diimport!"
            )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal import file: {e}")

    def export_questions(self):
        """Export semua soal ke file JSON lain."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Soal ke File", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Berhasil", f"Soal berhasil diexport ke:\n{file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal export file: {e}")


# -------------------- WINDOW TAMBAH PERTANYAAN --------------------

class AddQuizWindow(QWidget):
    def __init__(self, quiz_file_path, parent_window=None):
        super().__init__()
        self.setWindowTitle("Tambah Pertanyaan Baru")
        self.resize(400, 350)

        self.quiz_file_path = quiz_file_path
        self.parent_window = parent_window

        layout = QVBoxLayout()

        self.q_input = QTextEdit()
        self.q_input.setPlaceholderText("Masukkan teks pertanyaan di sini...")

        self.option_inputs = []
        for i in range(4):
            opt = QLineEdit()
            opt.setPlaceholderText(f"Pilihan {i+1}")
            layout.addWidget(opt)
            self.option_inputs.append(opt)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Jawaban yang benar (harus sama dengan salah satu opsi)")

        self.save_button = QPushButton("Simpan Pertanyaan")
        self.save_button.clicked.connect(self.save_question)

        layout.addWidget(QLabel("Pertanyaan:"))
        layout.addWidget(self.q_input)
        layout.addWidget(QLabel("Pilihan Jawaban:"))
        layout.addWidget(self.answer_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_question(self):
        """Simpan pertanyaan baru ke file JSON."""
        question_text = self.q_input.toPlainText().strip()
        options = [opt.text().strip() for opt in self.option_inputs]
        answer = self.answer_input.text().strip()

        if not question_text or not all(options) or not answer:
            QMessageBox.warning(self, "Error", "Semua field harus diisi!")
            return
        if answer not in options:
            QMessageBox.warning(self, "Error", "Jawaban harus sesuai dengan salah satu opsi!")
            return

        new_question = {"q": question_text, "options": options, "answer": answer}

        try:
            with open(self.quiz_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append(new_question)

        with open(self.quiz_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        QMessageBox.information(self, "Berhasil", "Pertanyaan baru berhasil ditambahkan!")

        if self.parent_window:
            self.parent_window.questions = self.parent_window.load_questions(self.quiz_file_path)

        self.close()
