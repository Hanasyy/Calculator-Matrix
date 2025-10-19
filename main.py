import sys, os
from PyQt6.QtWidgets import QApplication, QStackedWidget
from menu import MenuUtama
from input_matrix import WindowInputGrid
from process_window import WindowProses
from history_window import HistoryWindow
from quiz_utils import QuizWindow
from style import APP_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    stacked = QStackedWidget()

    menu_page = MenuUtama(stacked)
    input_page = WindowInputGrid(stacked)
    process_page = WindowProses(stacked)
    quiz_page = QuizWindow(os.path.join(os.path.dirname(__file__), "quiz_questions.json"), stacked)
    history_page = HistoryWindow(stacked)

    stacked.addWidget(menu_page)     # index 0
    stacked.addWidget(input_page)    # index 1
    stacked.addWidget(process_page)  # index 2
    stacked.addWidget(quiz_page)     # index 3
    stacked.addWidget(history_page)  # index 4

    def update_before_show(index):
        if index == 2 and hasattr(process_page, "refresh_matrix_list"):
            process_page.refresh_matrix_list()
    stacked.currentChanged.connect(update_before_show)

    stacked.resize(900, 700)
    stacked.show()
    sys.exit(app.exec())
