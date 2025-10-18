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

    # buat halaman dan kirim stacked ke semua window
    from menu import MenuUtama
    from input_matrix import WindowInputGrid
    from process_window import WindowProses
    from history_window import HistoryWindow
    from quiz_utils import QuizWindow

    menu_page = MenuUtama(stacked)
    input_page = WindowInputGrid(stacked)
    process_page = WindowProses(stacked)
    quiz_page = QuizWindow(os.path.join(os.path.dirname(__file__), "quiz_questions.json"))
    history_page = HistoryWindow(stacked)

    # urutan index stack (penting)
    stacked.addWidget(menu_page)      # index 0
    stacked.addWidget(input_page)     # index 1
    stacked.addWidget(process_page)   # index 2
    stacked.addWidget(quiz_page)      # index 3
    stacked.addWidget(history_page)   # index 4

    stacked.resize(900, 700)
    stacked.show()
    sys.exit(app.exec())
