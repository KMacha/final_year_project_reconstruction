#!/usr/bin/python
import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc

from gui.config import ConfigWindow
from gui.offline.offline import OfflineWindow
from gui.query.query import QueryWindow

class MainWindow(qtw.QMainWindow):
    def _configure_window(self,width:int=1280,height:int=720):
        self.setFixedSize(qtc.QSize(width,height))
        self.setWindowTitle("Offline Processing")

    def __init__(self):
        super().__init__()

        self._configure_window()

        self._main_layout = qtw.QHBoxLayout()
        self._main_widget = qtw.QWidget()
        self._main_stacked_widget = qtw.QStackedWidget()

        self._init_ui()

        self._main_widget.setLayout(self._main_layout)

        print(self.size())
        print(self.maximumSize())
        print(self.minimumSize())

        self.setCentralWidget(self._main_widget)

    def _init_ui(self):
        self._config_window = ConfigWindow()
        self._offline_window = OfflineWindow()
        self._query_window = QueryWindow()

        self._create_side_panel()
        self._main_layout.addWidget(self._side_panel)

        self._main_layout.addWidget(self._main_stacked_widget)

        self._main_stacked_widget.addWidget(self._offline_window)
        self._main_stacked_widget.addWidget(self._query_window)
        self._main_stacked_widget.addWidget(self._config_window)

    def _create_side_panel(self):
        side_panel_layout = qtw.QVBoxLayout()

        self._side_panel = qtw.QFrame()
        self._side_panel.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Sunken)
        self._side_panel.setContentsMargins(0,0,1,0)
        self._side_panel.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Minimum)

        config_btn = qtw.QPushButton("Configuration Settings")
        config_btn.clicked.connect(lambda: self._main_stacked_widget.setCurrentWidget(self._config_window))

        offline_btn = qtw.QPushButton("Offline Feature\n Processing")
        offline_btn.clicked.connect(lambda: self._main_stacked_widget.setCurrentWidget(self._offline_window))

        query_btn = qtw.QPushButton("Query \n(Online Search & Retrieval)")
        query_btn.clicked.connect(lambda: self._main_stacked_widget.setCurrentWidget(self._query_window))

        side_panel_layout.addWidget(config_btn)
        side_panel_layout.addStretch(1)
        side_panel_layout.addWidget(offline_btn)
        side_panel_layout.addStretch(1)
        side_panel_layout.addWidget(query_btn)
        side_panel_layout.addStretch(1)

        self._side_panel.setLayout(side_panel_layout)


if __name__ == "__main__":
    app = qtw.QApplication([])

    window = MainWindow()
    window.show()


    app.exec()
