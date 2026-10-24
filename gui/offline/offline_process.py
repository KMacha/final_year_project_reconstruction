import time
import yaml
import cv2
import PySide6.QtWidgets as qtw

from PySide6.QtCore import Qt,Signal,QTimer
from PySide6.QtGui import QPixmap,QImage

from motion_detection.detector import Detector
from object_tracker.object_tracker import ObjectTracker
from main import process_frame

class OfflineProcessWindow(qtw.QWidget):
    _back_to_offline = Signal()

    def _init_vars(self):
        self._detector_obj = None
        self._tracker_obj = None
        self._video_path = None
        self._video_cap = None
        self._video_timer = QTimer()

    def __init__(self):
        super().__init__()

        self._init_vars()
        self._main_layout = qtw.QVBoxLayout()

        self._init_ui()

        self.setLayout(self._main_layout)

    def _init_ui(self):
        self._create_frame_viewing_part()
        #self._create_progress_update_part()
        self._create_progress_update_part()

    def _create_frame_viewing_part(self):
        #creates 3 frames corresponding to the 3 most interesting parts that a video frame goes through during processing

        layout = qtw.QHBoxLayout()
        self._frame_view_widget = qtw.QWidget()
        self._frame_view_widget.setLayout(layout)

        ver_layout_1 = qtw.QVBoxLayout()

        #the original frame from the video
        frame_layout_1 = qtw.QVBoxLayout()
        original_frame = qtw.QFrame()
        original_frame.setLayout(frame_layout_1)
        self._original_frame_lbl = qtw.QLabel()
        frame_layout_1.addWidget(self._original_frame_lbl)

        orig_btn = qtw.QPushButton("View Bigger")

        ver_layout_1.addWidget(original_frame)
        ver_layout_1.addWidget(orig_btn)

        ver_layout_2 = qtw.QVBoxLayout()
        frame_layout_2 = qtw.QVBoxLayout()

        #the frame for the moving region
        moving_region_frame = qtw.QFrame()
        moving_region_frame.setLayout(frame_layout_2)
        self._moving_region_lbl = qtw.QLabel()
        frame_layout_2.addWidget(self._moving_region_lbl)

        mov_btn = qtw.QPushButton("view Bigger")

        ver_layout_2.addWidget(moving_region_frame)
        ver_layout_2.addWidget(mov_btn)

        ver_layout_3 = qtw.QVBoxLayout()
        frame_layout_3 = qtw.QVBoxLayout()

        #the original frame with the contours and tracking numbers added to it
        tracking_region_frame = qtw.QFrame()
        tracking_region_frame.setLayout(frame_layout_3)
        self._tracking_region_lbl = qtw.QLabel()
        frame_layout_3.addWidget(self._tracking_region_lbl)

        track_btn = qtw.QPushButton("View Bigger")

        ver_layout_3.addWidget(tracking_region_frame)
        ver_layout_3.addWidget(track_btn)

        layout.addLayout(ver_layout_1)
        layout.addLayout(ver_layout_2)
        layout.addLayout(ver_layout_3)

        #self._main_layout.addLayout(layout)
        self._main_layout.addWidget(self._frame_view_widget)
        self._main_layout.addStretch(1)

    def _create_progress_update_part_not_worked(self):
        progress_frame = qtw.QFrame()
        progress_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        layout = qtw.QVBoxLayout()

        for i in range(10):
            layout.addWidget(qtw.QLabel(f"Processing frame {i} ---> number of moving objects x --> total tracking objects y"))

        progress_frame.setLayout(layout)

        self._main_layout.addWidget(progress_frame)

    def _create_progress_update_part(self):
        gui_progress_frame = qtw.QFrame()
        gui_progress_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        layout = qtw.QVBoxLayout()

        hor_layout_1 = qtw.QHBoxLayout()

        lbl = qtw.QLabel("Approximate number of frames:")
        lbl.setAlignment(Qt.AlignRight)
        self._frames_lbl = qtw.QLabel()
        self._frames_lbl.setAlignment(Qt.AlignLeft)

        # a progress bar
        self._progress_bar = qtw.QProgressBar()
        #self._progress_bar.setAlignment(Qt.Horizontal)
        self._progress_frames_lbl = qtw.QLabel()

        hor_layout_1.addWidget(lbl)
        hor_layout_1.addWidget(self._frames_lbl,alignment=Qt.AlignLeft)
        hor_layout_1.addWidget(self._progress_bar)
        hor_layout_1.addWidget(self._progress_frames_lbl)

        hor_layout_2 = qtw.QHBoxLayout()

        query_btn = qtw.QPushButton("Go To Query")

        finish_cancel_btn = qtw.QPushButton("Exit")
        finish_cancel_btn.clicked.connect(self._cancel_finish)

        #hor_layout_2.addWidget(query_btn)
        hor_layout_2.addWidget(finish_cancel_btn)

        layout.addLayout(hor_layout_1)
        layout.addLayout(hor_layout_2)
        layout.setSizeConstraints(qtw.QLayout.SetDefaultConstraint,qtw.QLayout.SetFixedSize)

        gui_progress_frame.setLayout(layout)

        self._main_layout.addWidget(gui_progress_frame)
        self._main_layout.addStretch(1)

    def _cancel_finish(self):
        self._back_to_offline.emit()

        if self._video_cap is not None:
            self._video_cap.release()
            self._video_cap = None

        self._video_timer.stop()

    def configure_vars(self,table_name:str='test_table',show_visualisations:bool=True,video_file_path:str=''):
        with open("./.gui_config.yaml",'r') as file_obj:
            self._config = yaml.safe_load(file_obj)

        if show_visualisations:
            #we set the config variables for showing guis to true
            self._config["main"]["show_gui"] = True
        else:
            #set the config variables for showing guis to false
            self._config["main"]["show_gui"] = False
            self._config["object_tracker"]["visualise"] = False

        self._detector_obj = Detector(
            detector_type = self._config["motion_detector"]["detector_type"],
            contour_area_thresh= self._config["motion_detector"]["contour_area_threshold"]
        )

        self._config["db"]["table_name"] = table_name

        self._tracker_obj = ObjectTracker(
            tracker_config = self._config["object_tracker"],
            model_config = self._config["model"],
            db_config = self._config["db"],
            video_file_path = video_file_path
        )

    def set_video_path(self,video_path:str):
        self._video_path = video_path

    def process_video(self,draw:bool = True):
        if self._video_path is not None:
            self._video_cap = cv2.VideoCapture(self._video_path)

        #minimum resolution 1280 x 720
        MIN_WIDTH = self._config["main"]["min_width"]

        width = self._video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self._video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._approx_number_frames = int(self._video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._frames_lbl.setText(f"{self._approx_number_frames} frames")
        self._progress_bar.setMaximum(self._approx_number_frames)

        resize_frame = False
        max_dim = max(width,height)

        #we have 1280 x 720 as the largest resolution we are going to use without resizing
        #if a frame is larger than it, we scale it to 1280 x 720
        scale_factor = 1.0
        if max_dim > MIN_WIDTH:
            resize_frame = True
            scale_factor = MIN_WIDTH/max_dim

        self._processed_frames = 0

        if draw:
            self._frame_view_widget.show()
        else:
            self._frame_view_widget.hide()

        self._video_timer.timeout.connect(
            lambda: self.process_video_frame(
                resize_frame = resize_frame,
                scale_factor = scale_factor,
                draw = draw
            )
        )
        #self.timer.timeout.connect(self.process_video_frame_with_draw)

        self._start_time = time.perf_counter()
        self._video_timer.start(self._config["main"]["gui_speed"])

    def process_video_frame(self,resize_frame:bool=False,scale_factor:float=1.0,draw:bool=True):
        ret,frame = self._video_cap.read()

        if ret:
            frame_timestamp = self._video_cap.get(cv2.CAP_PROP_POS_MSEC)

            working_frame, motion_img = process_frame(
                orig_frame = frame,
                frame_timestamp = frame_timestamp,
                detector_obj = self._detector_obj,
                tracker_obj = self._tracker_obj,
                measurements_std_list = self._config["motion_detector"]["measurement_stds"],
                resize_frame = resize_frame,
                scale_factor = scale_factor,
                draw = draw
            )

            self._processed_frames+=1

            self._progress_frames_lbl.setText(f"{self._processed_frames} processed frames")
            self._progress_bar.setValue(self._processed_frames)

            if draw:
                frame = cv2.cvtColor(cv2.resize(frame,(400,400)),cv2.COLOR_BGR2RGB)
                working_frame = cv2.cvtColor(cv2.resize(working_frame,(400,400)),cv2.COLOR_BGR2RGB)
                #motion_img = cv2.cvtColor(motion_img,cv2.COLOR_BGR2RGB)
                motion_img = cv2.resize(motion_img,(400,400))

                orig_qimage = QImage(
                    frame,
                    frame.shape[1],
                    frame.shape[0],
                    QImage.Format_RGB888
                )

                working_qimage = QImage(
                    working_frame,
                    working_frame.shape[1],
                    working_frame.shape[0],
                    QImage.Format_RGB888
                )

                motion_qimage = QImage(
                    motion_img,
                    motion_img.shape[1],
                    motion_img.shape[0],
                    QImage.Format_Grayscale8
                )

                self._original_frame_lbl.setPixmap(QPixmap.fromImage(orig_qimage))
                self._moving_region_lbl.setPixmap(QPixmap.fromImage(motion_qimage))
                self._tracking_region_lbl.setPixmap(QPixmap.fromImage(working_qimage))
        else:
            self._video_timer.stop()

            #save the last of any remaining tracks
            self._tracker_obj.save_object_tracks()

            self._end_time = time.perf_counter()
            duration = self._end_time - self._start_time

            print(f"Duration: {duration:.3f} seconds")

            self._progress_bar.setValue(self._approx_number_frames)

