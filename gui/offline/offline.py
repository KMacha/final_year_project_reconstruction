import PySide6.QtWidgets as qtw
from PySide6.QtCore import Qt

class OfflineWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self._main_layout = qtw.QVBoxLayout()

        self._init_ui()

        self.setLayout(self._main_layout)

    def _init_ui(self):
        hor_layout = qtw.QHBoxLayout()

        self._create_video_part(hor_layout)

        self._create_table_part(hor_layout)

        self._main_layout.addLayout(hor_layout)
        self._main_layout.addStretch(1)

        #we create it and directly place it in the main layout (vertical layout)
        self._create_process_preview_btns()

    def _create_video_part(self,hor_layout):
        ver_layout_1 = qtw.QVBoxLayout()

        #widgets in the first vertical layout
        enter_btn = qtw.QPushButton("Enter\n Surveillance Footage")
        enter_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        video_lbl = qtw.QLabel("Video Name: video name")
        video_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        #video_lbl.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Plain)
        #video_lbl.setSizePolicy(qtw.QSizePolicy.Minimum,qtw.QSizePolicy.Fixed)

        self._create_video_info_frame()

        #adding widgets for the first vertical layout
        ver_layout_1.addWidget(enter_btn)
        ver_layout_1.addWidget(video_lbl)
        ver_layout_1.addWidget(self._video_info_frame)
        ver_layout_1.addStretch(1)

        hor_layout.addLayout(ver_layout_1)

    def _create_table_part(self,hor_layout):
        ver_layout_2 = qtw.QVBoxLayout()

        #widgets in the second vertical layout
        table_lbl = qtw.QLabel("Table Name: my table blah blah")
        #table_lbl.setSizePolicy(qtw.QSizePolicy.Minimum,qtw.QSizePolicy.Fixed)
        table_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        #table_lbl.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Plain)

        table_btn = qtw.QPushButton("Change Table Name")
        table_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        self._change_table_name_frame = self._create_change_table_frame()

        #adding widgets for the second vertical layout
        #ver_layout_2.setSpacing(0)
        ver_layout_2.setContentsMargins(90,1,1,1)
        ver_layout_2.addWidget(table_lbl)
        ver_layout_2.addWidget(table_btn)
        ver_layout_2.addWidget(self._change_table_name_frame)
        ver_layout_2.addStretch(1)

        hor_layout.addLayout(ver_layout_2)

    def _create_process_preview_btns(self):
        #layouts and widgets for the processing buttons
        hor_layout = qtw.QHBoxLayout()
        ver_layout_3 = qtw.QVBoxLayout()

        preview_video_btn = qtw.QPushButton("Preview Video")
        process_video_btn = qtw.QPushButton("Process Video")
        process_chck_btn = qtw.QCheckBox("Show Video While Processing")

        #adding the processing widgets into the layouts
        hor_layout.addWidget(preview_video_btn,alignment=Qt.AlignBottom)

        ver_layout_3.addWidget(process_chck_btn,alignment=Qt.AlignRight)
        ver_layout_3.addWidget(process_video_btn)

        hor_layout.addLayout(ver_layout_3)

        self._main_layout.addLayout(hor_layout)
        self._main_layout.addStretch(1)

    def _create_video_info_frame(self):
        self._video_info_frame = qtw.QFrame()
        self._video_info_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)
        #self._video_info_frame.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Fixed)
        layout = qtw.QVBoxLayout()
        layout.setSizeConstraints(qtw.QLayout.SetDefaultConstraint,qtw.QLayout.SetFixedSize)
        #layout.setContentsMargins(0,0,0,0)

        self._codec_label = qtw.QLabel("Codec: this is my codec")
        self._resolution_label = qtw.QLabel("Video Resolution: 1920 x 1080")
        self._frame_rate = qtw.QLabel("Frame Rate: 30 fps")
        self._save_db_name = qtw.QLabel("Database: db_name")
        self._save_tbl_name = qtw.QLabel("Table_Name: my table blah blah")


        layout.addWidget(self._codec_label)
        layout.addWidget(self._resolution_label)
        layout.addWidget(self._frame_rate)
        layout.addWidget(self._save_db_name)
        layout.addWidget(self._save_tbl_name)

        self._video_info_frame.setLayout(layout)

    def _create_change_table_frame(self):
        frame = qtw.QFrame()
        frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        layout = qtw.QGridLayout()
        layout.setSizeConstraints(qtw.QLayout.SetDefaultConstraint,qtw.QLayout.SetFixedSize)
        #layout.setContentsMargins(0,0,0,0)

        line_edit = qtw.QLineEdit()
        save_btn = qtw.QPushButton("Save")
        cancel_btn = qtw.QPushButton("Cancel")

        layout.addWidget(line_edit,0,0,1,6)
        layout.addWidget(save_btn,1,4)
        layout.addWidget(cancel_btn,1,5)

        frame.setLayout(layout)

        return frame
