import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from menu import MenuUtama
from input_matrix import WindowInputGrid
from process_window import WindowProses
from style import APP_STYLE
from quiz_utils import QuizWindow  
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    stacked = QStackedWidget()

    # Inisialisasi halaman utama
    menu = MenuUtama(stacked)
    input_page = WindowInputGrid(menu)
    proses_page = WindowProses(menu)

    # Pastikan file quiz ada
    quiz_file_path = os.path.join("data", "quiz_data.json")
    quiz_page = QuizWindow(quiz_file_path)  

    # Tambahkan ke stack
    stacked.addWidget(menu)
    stacked.addWidget(input_page)
    stacked.addWidget(proses_page)
    stacked.addWidget(quiz_page)  

    stacked.resize(700, 500)
    stacked.showMaximized()
    stacked.show()

    sys.exit(app.exec())
