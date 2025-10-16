import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from menu import MenuUtama
from input_matrix import WindowInputGrid
from process_window import WindowProses
from style import APP_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    stacked = QStackedWidget()

    menu = MenuUtama(stacked)
    input_page = WindowInputGrid(menu)
    proses_page = WindowProses(menu)

    stacked.addWidget(menu)
    stacked.addWidget(input_page)
    stacked.addWidget(proses_page)

    stacked.resize(700, 500)
    stacked.showMaximized()
    stacked.show()

    sys.exit(app.exec())
