import PySide6.QtWidgets as qtw

class PreviewVideoWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self._main_layout = qtw.QVBoxLayout()

        self._init_ui()

        self.setLayout(self._main_layout)



    def _init_ui(self):

        self._video_frame = qtw.QFrame()

        self._main_layout.addWidget(self._video_frame)

        self._create_control_widget()

    def _create_control_widget(self):
        control_frame = qtw.QFrame()
        control_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Raised)

        control_layout = qtw.QHBoxLayout()

        lbl = qtw.QLabel("Current Speed:")
        speed_lbl = qtw.QLabel("0")
        speed_spinbox = qtw.QSpinBox()

        loop_btn = qtw.QPushButton("Loop")
        preview_again_btn = qtw.QPushButton("Preview Again")
        pause_btn = qtw.QPushButton("Pause")
        exit_btn = qtw.QPushButton("Exit")

        control_layout.addWidget(lbl)
        control_layout.addWidget(speed_lbl)
        control_layout.addWidget(speed_spinbox)
        control_layout.addWidget(loop_btn)
        control_layout.addWidget(preview_again_btn)
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(exit_btn)

        control_layout.setSizeConstraint(qtw.QLayout.SetFixedSize)
        control_frame.setLayout(control_layout)

        self._main_layout.addStretch(1)
        self._main_layout.addWidget(control_frame)
