import cv2
import sys
import PySide6.QtWidgets as qtw
from PySide6.QtCore import Qt

from pathlib import Path

from gui.offline.offline_process import OfflineProcessWindow
from gui.preview import PreviewVideoWindow

class OfflineWindow(qtw.QStackedWidget):
    def __init__(self):
        super().__init__()

        #get the offlineprocessing window
        self._offline_processing_window = OfflineProcessWindow()

        #add it to the stackedwidget
        self.addWidget(self._offline_processing_window)

        #get preview window and add it to stackedwidget
        self._video_preview_window = PreviewVideoWindow()
        self.addWidget(self._video_preview_window)

        #init some variables
        self._video_path = None
        self._table_name = None


        self._offline_widget = qtw.QWidget()
        self._offline_widget_layout = qtw.QVBoxLayout()

        self._init_offline_widget_ui()

        self._offline_widget.setLayout(self._offline_widget_layout)

        #add the offline_widget to the stackedwidget
        self.addWidget(self._offline_widget)
        self.setCurrentWidget(self._offline_widget)


        #connecting to the back signals from the windows
        self._video_preview_window._back_to_offline.connect(lambda: self.setCurrentWidget(self._offline_widget))
        self._offline_processing_window._back_to_offline.connect(lambda: self.setCurrentWidget(self._offline_widget))

    def _init_offline_widget_ui(self):
        hor_layout = qtw.QHBoxLayout()

        self._create_video_part(hor_layout)

        self._create_table_part(hor_layout)

        self._offline_widget_layout.addLayout(hor_layout)
        self._offline_widget_layout.addStretch(1)

        #we create it and directly place it in the main layout (vertical layout)
        self._create_process_preview_btns()

    def _create_video_part(self,hor_layout):
        ver_layout_1 = qtw.QVBoxLayout()

        #widgets in the first vertical layout
        enter_video_btn = qtw.QPushButton("Enter\n Surveillance Footage")
        enter_video_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        enter_video_btn.clicked.connect(self.get_video_file)

        self._video_lbl = qtw.QLabel("Video Name: video name")
        self._video_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._video_lbl.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Plain)
        self._video_lbl.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Fixed)

        self._create_video_info_frame()

        #adding widgets for the first vertical layout
        ver_layout_1.addWidget(enter_video_btn)
        ver_layout_1.addWidget(self._video_lbl)
        ver_layout_1.addWidget(self._video_info_frame)
        ver_layout_1.addStretch(1)

        hor_layout.addLayout(ver_layout_1)

    def _create_table_part(self,hor_layout):
        ver_layout_2 = qtw.QVBoxLayout()

        #widgets in the second vertical layout
        tbl_hor_layout = qtw.QHBoxLayout()

        lbl = qtw.QLabel("Table Name:")
        lbl.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Fixed)
        tbl_hor_layout.addWidget(lbl)

        self._table_lbl = qtw.QLabel('')
        #self._table_lbl.setSizePolicy(qtw.QSizePolicy.Minimum,qtw.QSizePolicy.Fixed)
        self._table_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        #self._table_lbl.setFrameStyle(qtw.QFrame.Box | qtw.QFrame.Plain)
        tbl_hor_layout.addWidget(self._table_lbl)
        #tbl_hor_layout.addStretch(1)

        self._change_table_name_frame = self._create_change_table_frame()

        self._table_btn = qtw.QPushButton("Change Table Name")
        self._table_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        self._table_btn.clicked.connect(lambda: self._change_table_name_frame.setEnabled(True))
        self._table_btn.setEnabled(False)


        #adding widgets for the second vertical layout
        #ver_layout_2.setSpacing(0)
        ver_layout_2.setContentsMargins(90,1,1,1)
        ver_layout_2.addLayout(tbl_hor_layout)
        ver_layout_2.addWidget(self._table_btn)
        ver_layout_2.addWidget(self._change_table_name_frame)
        ver_layout_2.addStretch(1)

        hor_layout.addLayout(ver_layout_2)

    def _create_process_preview_btns(self):
        #layouts and widgets for the processing buttons
        hor_layout = qtw.QHBoxLayout()
        ver_layout_3 = qtw.QVBoxLayout()

        preview_video_btn = qtw.QPushButton("Preview Video")
        preview_video_btn.clicked.connect(self.preview_video)

        process_video_btn = qtw.QPushButton("Process Video")
        process_video_btn.clicked.connect(self.process_video)

        self._process_chck_btn = qtw.QCheckBox("Show Video While Processing")

        #adding the processing widgets into the layouts
        hor_layout.addWidget(preview_video_btn,alignment=Qt.AlignBottom)

        ver_layout_3.addWidget(self._process_chck_btn,alignment=Qt.AlignRight)
        ver_layout_3.addWidget(process_video_btn)

        hor_layout.addLayout(ver_layout_3)

        self._offline_widget_layout.addLayout(hor_layout)
        self._offline_widget_layout.addStretch(1)

    def _create_video_info_frame(self):
        self._video_info_frame = qtw.QFrame()
        self._video_info_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)
        self._video_info_frame.setEnabled(False)
        #self._video_info_frame.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Fixed)
        layout = qtw.QVBoxLayout()
        layout.setSizeConstraints(qtw.QLayout.SetDefaultConstraint,qtw.QLayout.SetFixedSize)
        #layout.setContentsMargins(0,0,0,0)

        self._codec_label = qtw.QLabel("Codec:")
        self._resolution_label = qtw.QLabel("Video Resolution:")
        self._frame_rate = qtw.QLabel("Frame Rate:")
        self._frame_count = qtw.QLabel("Frame Count:")
        self._save_db_name = qtw.QLabel("Database:")
        self._save_tbl_name = qtw.QLabel("Table_Name:")


        layout.addWidget(self._codec_label)
        layout.addWidget(self._resolution_label)
        layout.addWidget(self._frame_rate)
        layout.addWidget(self._save_db_name)
        layout.addWidget(self._save_tbl_name)

        self._video_info_frame.setLayout(layout)

    def _create_change_table_frame(self):
        frame = qtw.QFrame()
        frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)
        frame.setEnabled(False)

        layout = qtw.QGridLayout()
        layout.setSizeConstraints(qtw.QLayout.SetDefaultConstraint,qtw.QLayout.SetFixedSize)
        #layout.setContentsMargins(0,0,0,0)

        self._table_line_edit = qtw.QLineEdit()
        self._table_line_edit.textChanged.connect(self._table_lbl.setText)

        save_btn = qtw.QPushButton("Save")
        save_btn.clicked.connect(self.save_new_table_name)

        cancel_btn = qtw.QPushButton("Cancel")
        cancel_btn.clicked.connect(lambda: frame.setEnabled(False))

        layout.addWidget(self._table_line_edit,0,0,1,6)
        layout.addWidget(save_btn,1,4)
        layout.addWidget(cancel_btn,1,5)

        frame.setLayout(layout)

        return frame

    #slots for various of the signals

    def get_video_file(self):
        #returns a tuple with the first item being the path
        results = qtw.QFileDialog.getOpenFileName(self)

        video_path = results[0]

        if video_path:
            self._video_path = Path(video_path)
            video_name = self._video_path.stem
            self.get_and_set_video_metadata(video_name)
            self._video_lbl.setText(f"Video Name: {video_name}")
        else:
            print("No file selected")

    def get_and_set_video_metadata(self,video_name:str):
        if self._video_path is not None:
            video_cap = cv2.VideoCapture(self._video_path)

            video_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_fps = video_cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_codec = int(video_cap.get(cv2.CAP_PROP_FOURCC))

            #to get the name of the video codec
            video_codec_name = video_codec.to_bytes(4,byteorder=sys.byteorder).decode()

            self._video_info_frame.setEnabled(True)
            self._codec_label.setText(f"Video Codec: {video_codec_name}")
            self._resolution_label.setText(f"Video Resolution: {video_width} x {video_height}")
            self._frame_rate.setText(f"Frame Rate: {video_fps} fps")
            self._frame_count.setText(f"Approx Frame Count: {frame_count:,} frames")

            #save table name -> basically the video name split using _ instead of spaces where applicable
            self._table_name = '_'.join(video_name.split())
            self._save_tbl_name.setText(f"Table Name: {self._table_name}")

            self._table_line_edit.setText(self._table_name)
            self._table_lbl.setText(self._table_name)
            self._table_btn.setEnabled(True)

    def save_new_table_name(self):
        if new_tbl_name.strip():
            self._table_name = new_tbl_name
            self._table_lbl.setText(self._table_name)
            self._save_tbl_name.setText(f"Table Name: {self._table_name}")
        else:
            self._table_lbl.setText(self._table_name)
            self._table_line_edit.setText(self._table_name)

        self._change_table_name_frame.setEnabled(False)

    def process_video(self):
        show_video_gui = False

        if self._process_chck_btn.checkState() == Qt.Checked:
            message = (
                "Showing Videos while processing will slow down the processing.\n"
                "Depending on the system, the processing slow down might be significant or it might be insignificant.\n"
                "\n\nDo you want to continue with showing videos on?"
            )

            btn = qtw.QMessageBox.question(self,"Warning",message)

            if btn == qtw.QMessageBox.Yes:
                show_video_gui = True

            print("Showing video?",show_video_gui)

        self.setCurrentWidget(self._offline_processing_window)


    def preview_video(self):
        if self._video_path:
            self.setCurrentWidget(self._video_preview_window)
            self._video_preview_window.set_video_path(video_path = self._video_path)
            self._video_preview_window.set_up_video()
        else:
            message = (
                "No video selected...\n"
                "Please Select a video using the <b>Enter Surveillance Footage</b> Button"
            )

            qtw.QMessageBox.information(self,"No Video",message)
