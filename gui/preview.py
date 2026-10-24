import time
import cv2
import PySide6.QtWidgets as qtw

from PySide6.QtCore import Signal,QTimer
from PySide6.QtGui import QImage,QPixmap

class PreviewVideoWindow(qtw.QWidget):
    _back_to_offline = Signal()

    def variable_config(self,video_path:str|None = None):
        self._video_path = video_path

        self._video_cap = None

        self._start_time_ms = 0
        self._end_time_ms = 0

        self._video_speed = 1

        self._video_paused = self._loop_video = False

        self._video_timer = QTimer()

    def __init__(self):
        super().__init__()

        self.variable_config()

        self._main_layout = qtw.QVBoxLayout()

        #signal to use to well signal we are going back
        #self._back_to_offline = Signal()

        self._init_ui()

        self.setLayout(self._main_layout)


    def _init_ui(self):
        video_frame = qtw.QFrame()

        video_layout = qtw.QVBoxLayout()

        self._video_lbl = qtw.QLabel()
        video_layout.addWidget(self._video_lbl)
        video_frame.setLayout(video_layout)

        self._main_layout.addWidget(video_frame)

        self._create_control_widget()

    def _create_control_widget(self):
        control_frame = qtw.QFrame()
        control_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Raised)

        control_layout = qtw.QHBoxLayout()

        lbl = qtw.QLabel("Current Speed:")
        self._video_speed_lbl = qtw.QLabel("1")
        self._speed_spinbox = qtw.QSpinBox()
        self._speed_spinbox.setMinimum(1)
        self._speed_spinbox.setMaximum(120)
        self._speed_spinbox.valueChanged.connect(self.change_video_speed)

        self._loop_btn = qtw.QPushButton("Loop")
        self._loop_btn.clicked.connect(self._loop_unloop_video)

        preview_again_btn = qtw.QPushButton("Preview Again")
        preview_again_btn.clicked.connect(self._restart_video)

        self._pause_btn = qtw.QPushButton("Pause")
        self._pause_btn.clicked.connect(self._pause_play_video)

        exit_btn = qtw.QPushButton("Exit")
        #exit_btn.clicked.connect(lambda:self._back_to_offline.emit)
        exit_btn.clicked.connect(self._exit)

        control_layout.addWidget(lbl)
        control_layout.addWidget(self._video_speed_lbl)
        control_layout.addWidget(self._speed_spinbox)
        control_layout.addWidget(self._loop_btn)
        control_layout.addWidget(preview_again_btn)
        control_layout.addWidget(self._pause_btn)
        control_layout.addWidget(exit_btn)

        control_layout.setSizeConstraint(qtw.QLayout.SetFixedSize)
        control_frame.setLayout(control_layout)

        self._main_layout.addStretch(1)
        self._main_layout.addWidget(control_frame)

    def _reset_gui(self):
        #resets the gui to the default options
        if self._video_cap is not None:
            self._video_cap.release()
            self._video_cap = None


        self._video_speed = 1
        self._video_paused = self._loop_video = False
        self._start_time_ms = self._end_time_ms = 0

        #reset the dynamic gui components
        self._pause_btn.setText("Pause")
        self._loop_btn.setText("Loop")

        #this will emit a value changed which will then take care of the speed label too... 
        self._speed_spinbox.setValue(self._video_speed)

        #stop the time as the video speed function does start the timer
        if self._video_timer.isActive():
            self._video_timer.stop()

    def _exit(self):
        self._back_to_offline.emit()

        self._reset_gui()

    def set_up_video(self,restart:bool=False,start_time_ms:float|None=None,end_time_ms:float|None=None):
        if self._video_path is None:
            message = "No Video to preview"
            qtw.QMessageBox.critical(self,"Error",message)
            return

        if self._video_cap is None:
            self._video_cap = cv2.VideoCapture(self._video_path)

        self._start_time_ms = start_time_ms
        self._end_time_ms = end_time_ms
        if start_time_ms is not None:
            self._video_cap.set(cv2.CAP_PROP_POS_MSEC,start_time_ms)

        if restart:
            self._video_cap.set(cv2.CAP_PROP_POS_MSEC,0)

        self._video_timer.timeout.connect(self._preview_video)
        self._video_timer.start(self._video_speed)

    def _restart_video(self):
        #just reset the video_capture object, that way restarting a video also respects whether the video had been paused or not
        print("speed:",self._video_speed)
        if self._video_cap is not None:
            start_time_ms = self._start_time_ms if self._start_time_ms else 0
            self._video_cap.set(cv2.CAP_PROP_POS_MSEC,start_time_ms)

            if not self._video_timer.isActive() and not self._video_paused:
                self._video_timer.start(self._video_speed)

            if self._video_paused:
                self._preview_video()

    def _loop_unloop_video(self):
        if self._loop_video:
            #unloop video
            self._loop_video = False
            self._loop_btn.setText("Loop")
        else:
            #loop video
            self._loop_video = True
            self._loop_btn.setText("Unloop")

    def _pause_play_video(self):
        if not self._video_paused:
            self._video_timer.stop()
            self._video_paused = True
            self._pause_btn.setText("Play")
        else:
            self._video_timer.start(self._video_speed)
            self._video_paused = False
            self._pause_btn.setText("Pause")

    def set_video_speed(self,video_speed:int):
        self._speed_spinbox.setValue(video_speed)
        self._video_timer.stop()

    def change_video_speed(self,video_speed:int):
        self._video_speed = video_speed

        self._video_speed_lbl.setText(str(video_speed))

        if self._video_timer.isActive():
            self._video_timer.start(video_speed)

    def _preview_video(self):
        #TODO: Perhaps add a check to check if _video_cap has anything --> first test and see if needed...
        ret,frame = self._video_cap.read()

        #only show a frame if a frame exists
        if ret:
            frame_timestamp = self._video_cap.get(cv2.CAP_PROP_POS_MSEC)
            if self._end_time_ms is not None and frame_timestamp >= self._end_time_ms:
                if self._loop_video:
                    start_time_ms = self._start_time_ms if self._start_time_ms else 0
                    self._video_cap.set(cv2.CAP_PROP_POS_MSEC,start_time_ms)
                else:
                    self._video_timer.stop()
                return

            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

            qt_image = QImage(
                frame,
                frame.shape[1],
                frame.shape[0],
                QImage.Format_RGB888
            )

            self._video_lbl.setPixmap(QPixmap.fromImage(qt_image))
        else:
            if self._loop_video:
                start_time_ms = self._start_time_ms if self._start_time_ms else 0
                self._video_cap.set(cv2.CAP_PROP_POS_MSEC,start_time_ms)

    #helper methods
    def set_video_path(self,video_path:str):
        self._video_path = video_path

