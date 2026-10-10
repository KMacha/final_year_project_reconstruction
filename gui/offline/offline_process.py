import PySide6.QtWidgets as qtw

from PySide6.QtCore import Qt,Signal

class OfflineProcessWindow(qtw.QWidget):
    _back_to_offline = Signal()

    def __init__(self):
        super().__init__()

        self._main_layout = qtw.QVBoxLayout()

        self._init_ui()

        self.setLayout(self._main_layout)

    def _init_ui(self):
        self._create_frame_viewing_part()
        self._create_progress_update_part()
        self._create_other_part()

    def _create_frame_viewing_part(self):
        #creates 3 frames corresponding to the 3 most interesting parts that a video frame goes through during processing

        layout = qtw.QHBoxLayout()

        ver_layout_1 = qtw.QVBoxLayout()

        #the original frame from the video
        original_frame = qtw.QFrame()
        orig_btn = qtw.QPushButton("View Bigger")

        ver_layout_1.addWidget(original_frame)
        ver_layout_1.addWidget(orig_btn)

        ver_layout_2 = qtw.QVBoxLayout()

        #the frame for the moving region
        moving_region_frame = qtw.QFrame()
        mov_btn = qtw.QPushButton("view Bigger")

        ver_layout_2.addWidget(moving_region_frame)
        ver_layout_2.addWidget(mov_btn)

        ver_layout_3 = qtw.QVBoxLayout()

        #the original frame with the contours and tracking numbers added to it
        tracking_region_frame = qtw.QFrame()
        track_btn = qtw.QPushButton("View Bigger")

        ver_layout_3.addWidget(tracking_region_frame)
        ver_layout_3.addWidget(track_btn)

        layout.addLayout(ver_layout_1)
        layout.addLayout(ver_layout_2)
        layout.addLayout(ver_layout_3)

        self._main_layout.addLayout(layout)

    def _create_progress_update_part(self):
        progress_frame = qtw.QFrame()
        progress_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        layout = qtw.QVBoxLayout()

        for i in range(10):
            layout.addWidget(qtw.QLabel(f"Processing frame {i} ---> number of moving objects x --> total tracking objects y"))

        progress_frame.setLayout(layout)

        self._main_layout.addWidget(progress_frame)

    def _create_other_part(self):
        gui_progress_frame = qtw.QFrame()
        gui_progress_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        layout = qtw.QVBoxLayout()

        hor_layout_1 = qtw.QHBoxLayout()

        lbl = qtw.QLabel("Approximate number of frames:")
        lbl.setAlignment(Qt.AlignRight)
        frames_lbl = qtw.QLabel("734")
        frames_lbl.setAlignment(Qt.AlignLeft)

        # a progress bar
        progress_lbl = qtw.QLabel("23% Processed")
        progress_frames_lbl = qtw.QLabel("169 frames processed")

        hor_layout_1.addWidget(lbl)
        hor_layout_1.addWidget(frames_lbl,alignment=Qt.AlignLeft)
        hor_layout_1.addWidget(progress_lbl)
        hor_layout_1.addWidget(progress_frames_lbl)

        hor_layout_2 = qtw.QHBoxLayout()

        query_btn = qtw.QPushButton("Go To Query")

        cancel_btn = qtw.QPushButton("Cancel Processing")
        cancel_btn.clicked.connect(self._cancel)

        hor_layout_2.addWidget(query_btn)
        hor_layout_2.addWidget(cancel_btn)

        layout.addLayout(hor_layout_1)
        layout.addLayout(hor_layout_2)
        layout.setSizeConstraints(qtw.QLayout.SetDefaultConstraint,qtw.QLayout.SetFixedSize)

        gui_progress_frame.setLayout(layout)

        self._main_layout.addWidget(gui_progress_frame)

    def _cancel(self):
        self._back_to_offline.emit()

