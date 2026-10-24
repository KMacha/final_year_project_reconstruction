import yaml
import PySide6.QtWidgets as qtw

from PySide6.QtCore import Qt
from pathlib import Path

class ConfigWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self._config_save_file_path = Path("./.gui_config.yaml")

        self._main_layout = qtw.QVBoxLayout()

        self._detectors = ["background_subtractor","three_frame_difference","Machine_Learning"]
        self._models = ["squeezenet_1_1"]

        self._init_ui()

        if not self._config_save_file_path.exists():
            self._default_values()
            self._save_configuration()
        else:
            self._set_values_from_configuration()

        self.setLayout(self._main_layout)

    def _init_ui(self):
        hor_layout = qtw.QHBoxLayout()
        self._main_layout.addLayout(hor_layout)

        left_part_layout = self._create_gui_left_part()
        hor_layout.addLayout(left_part_layout)
        hor_layout.addStretch(1)

        right_part_layout = self._create_gui_right_part()
        hor_layout.addLayout(right_part_layout)
        hor_layout.addStretch(1)

        self._create_buttons()

    def _create_gui_left_part(self)->qtw.QLayout:
        left_part_layout = qtw.QVBoxLayout()
        left_part_layout.addStretch(1)

        main_part_frame = self._create_main_part_config()
        left_part_layout.addWidget(main_part_frame)
        left_part_layout.addStretch(1)

        motion_part_frame = self._create_motion_part_config()
        left_part_layout.addWidget(motion_part_frame)
        left_part_layout.addStretch(1)

        return left_part_layout

    def _create_gui_right_part(self)->qtw.QLayout:
        right_part_layout = qtw.QVBoxLayout()

        db_part_frame = self._create_db_part_config()
        right_part_layout.addWidget(db_part_frame)
        right_part_layout.addStretch(1)

        model_part_frame = self._create_model_part_config()
        right_part_layout.addWidget(model_part_frame)
        right_part_layout.addStretch(1)

        object_tracker_part_frame = self._create_object_tracker_part_config()
        right_part_layout.addWidget(object_tracker_part_frame)
        right_part_layout.addStretch(1)

        return right_part_layout


    def _default_values(self):
        #default values for the main part
        self._video_dir_lbl.setText("./assets/videos")
        self._width_spinbox.setValue(1280)
        self._height_spinbox.setValue(720)
        self._show_gui_option.setCurrentIndex(0)
        self._gui_timer_spinbox.setValue(1)

        #default values for the motion part

        #measurement standard deviations
        self._x_std_spinbox.setValue(3)
        self._y_std_spinbox.setValue(3)
        self._width_std_spinbox.setValue(10)
        self._height_std_spinbox.setValue(10)

        self._contour_area_spinbox.setValue(150)
        self._detector_combobox.setCurrentIndex(0)

        #default values for the model part config
        self._model_name_cb.setCurrentIndex(0)
        self._cat_lbl.setText("./assets/model/pyt_classes.npz")
        self._weights_lbl.setText("./assets/model/pyt_squeezenet_model.pth")
        self._model_img_width_spinbox.setValue(224)
        self._model_img_height_spinbox.setValue(224)
        self._z_norm_cb.setCurrentIndex(0)

        #default values for the object tracker part config
        self._undetected_thresh_spinbox.setValue(20)
        self._tentative_thresh_spinbox.setValue(5)
        self._motion_thresh_spinbox.setValue(13.28)
        self._colour_thresh_spinbox.setValue(0.4)
        self._save_thresh_spinbox.setValue(32)
        self._start_track_id_spinbox.setValue(1)
        self._thumbnail_save_path_lbl.setText("./assets/.db/thumbnail_images")
        self._visualise_track_cb.setCurrentIndex(1)
        self._dry_run_cb.setCurrentIndex(0)

    #left part of window
    def _create_main_part_config(self)->qtw.QGroupBox:
        main_frame = qtw.QGroupBox("Main Config")
        main_frame.setAlignment(Qt.AlignHCenter)
        #main_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        main_frame_layout = qtw.QVBoxLayout()
        main_frame.setLayout(main_frame_layout)

        #part to change where the directory where the videos are located

        video_dir_layout =qtw.QHBoxLayout()
        main_frame_layout.addLayout(video_dir_layout)

        video_dir_lbl = qtw.QLabel("Video_dir:")
        #video_dir_lbl.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Minimum)

        self._video_dir_lbl = qtw.QLabel()
        #self._video_dir_lbl.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Minimum)
        #self._video_dir_lbl.setAlignment(Qt.AlignLeft)

        video_dir_change_btn = qtw.QPushButton("Change")
        video_dir_change_btn.clicked.connect(self._change_video_dir)
        #video_dir_change_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        video_dir_layout.addWidget(video_dir_lbl)
        video_dir_layout.addWidget(self._video_dir_lbl)
        video_dir_layout.addWidget(video_dir_change_btn)
        video_dir_layout.addStretch(1)

        #Part for setting maximum resolution that can be used while processing the videos
        #or rather the minimum resolution to reduce others to i.e. 1280 x 720

        resolution_layout = qtw.QHBoxLayout()
        main_frame_layout.addLayout(resolution_layout)

        width_lbl = qtw.QLabel("Width:")
        self._width_spinbox = qtw.QSpinBox()
        self._width_spinbox.setMinimum(10)
        self._width_spinbox.setMaximum(2560)

        height_lbl = qtw.QLabel("Height:")
        self._height_spinbox = qtw.QSpinBox()
        self._height_spinbox.setMinimum(10)
        self._height_spinbox.setMaximum(1440)

        resolution_layout.addWidget(width_lbl)
        resolution_layout.addWidget(self._width_spinbox)
        resolution_layout.addStretch(1)

        resolution_layout.addWidget(height_lbl)
        resolution_layout.addWidget(self._height_spinbox)
        resolution_layout.addStretch(2)

        other_hor_layout = qtw.QHBoxLayout()
        main_frame_layout.addLayout(other_hor_layout)

        show_gui_lbl = qtw.QLabel("Show GUI While Processing:")
        self._show_gui_option = qtw.QComboBox()
        self._show_gui_option.addItems(["Yes","No"])

        other_hor_layout.addWidget(show_gui_lbl)
        other_hor_layout.addWidget(self._show_gui_option)
        other_hor_layout.addStretch(1)

        other_hor_layout = qtw.QHBoxLayout()
        main_frame_layout.addLayout(other_hor_layout)

        gui_timer_lbl = qtw.QLabel("GUI Timer Speed:")
        self._gui_timer_spinbox = qtw.QSpinBox()
        self._gui_timer_spinbox.setMinimum(1)

        other_hor_layout.addWidget(gui_timer_lbl)
        other_hor_layout.addWidget(self._gui_timer_spinbox)
        other_hor_layout.addStretch(1)

        return main_frame

    def _create_motion_part_config(self)->qtw.QGroupBox:
        motion_frame = qtw.QGroupBox("Motion config")
        motion_frame.setAlignment(Qt.AlignHCenter)
        #motion_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        motion_frame_layout = qtw.QVBoxLayout()
        motion_frame.setLayout(motion_frame_layout)

        #part for changing the measurement stds

        centroid_layout = qtw.QHBoxLayout()
        motion_frame_layout.addLayout(centroid_layout)

        x_label = qtw.QLabel('x')
        self._x_std_spinbox = qtw.QDoubleSpinBox()
        self._x_std_spinbox.setMaximum(1e6)

        y_label = qtw.QLabel('y')
        self._y_std_spinbox = qtw.QDoubleSpinBox()
        self._y_std_spinbox.setMaximum(1e6)

        centroid_layout.addWidget(x_label)
        centroid_layout.addWidget(self._x_std_spinbox)
        centroid_layout.addStretch(1)

        centroid_layout.addWidget(y_label)
        centroid_layout.addWidget(self._y_std_spinbox)
        centroid_layout.addStretch(2)

        width_height_layout = qtw.QHBoxLayout()
        motion_frame_layout.addLayout(width_height_layout)

        width_label = qtw.QLabel("Width")
        self._width_std_spinbox = qtw.QDoubleSpinBox()
        self._width_std_spinbox.setMaximum(1e6)

        height_label = qtw.QLabel("Height")
        self._height_std_spinbox = qtw.QDoubleSpinBox()
        self._height_std_spinbox.setMaximum(1e6)

        width_height_layout.addWidget(width_label)
        width_height_layout.addWidget(self._width_std_spinbox)
        width_height_layout.addStretch(1)

        width_height_layout.addWidget(height_label)
        width_height_layout.addWidget(self._height_std_spinbox)
        width_height_layout.addStretch(2)

        #contour area threshold
        hor_layout = qtw.QHBoxLayout()
        motion_frame_layout.addLayout(hor_layout)

        contour_area_threshold_lbl = qtw.QLabel("Contour Area Threshold")
        self._contour_area_spinbox = qtw.QSpinBox()
        self._contour_area_spinbox.setMinimum(0)
        self._contour_area_spinbox.setMaximum(2560 * 1440)

        hor_layout.addWidget(contour_area_threshold_lbl)
        hor_layout.addWidget(self._contour_area_spinbox)
        hor_layout.addStretch(1)

        #motion detector type
        hor_layout = qtw.QHBoxLayout()
        motion_frame_layout.addLayout(hor_layout)

        detector_lbl = qtw.QLabel("Detector Type")
        self._detector_combobox = qtw.QComboBox()
        self._detector_combobox.addItems(self._detectors)

        hor_layout.addWidget(detector_lbl)
        hor_layout.addWidget(self._detector_combobox)
        hor_layout.addStretch(1)

        return motion_frame

    #left slots
    def _change_video_dir(self):
        video_dir = qtw.QFileDialog.getExistingDirectory(self)

        if video_dir and video_dir.strip():
            video_dir = video_dir.strip()
            self._video_dir_lbl.setText(video_dir)

    #right part of window
    def _create_db_part_config(self)->qtw.QGroupBox:
        db_frame = qtw.QGroupBox("DB Config")
        db_frame.setAlignment(Qt.AlignHCenter)
        #db_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        db_layout = qtw.QVBoxLayout()
        db_frame.setLayout(db_layout)

        items = {
            "Database Name:": "surveillance_project",
            "user:": "macha",
            "host:": "localhost"
        }

        for key,value in items.items():
            layout = qtw.QHBoxLayout()
            db_layout.addLayout(layout)

            lbl = qtw.QLabel(key)
            name_lbl = qtw.QLabel(value)

            layout.addWidget(lbl)
            layout.addWidget(name_lbl)
            layout.addStretch(1)

        db_layout.addStretch(1)

        return db_frame

    def _create_model_part_config(self)->qtw.QGroupBox:
        model_frame = qtw.QGroupBox("Model Config")
        model_frame.setAlignment(Qt.AlignHCenter)
        #model_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        model_layout = qtw.QVBoxLayout()
        model_frame.setLayout(model_layout)

        hor_layout = qtw.QHBoxLayout()
        model_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Name:")
        self._model_name_cb = qtw.QComboBox()
        self._model_name_cb.addItems(self._models)

        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._model_name_cb)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        model_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Category File Path(npz):")
        self._cat_lbl = qtw.QLabel()
        change_cat_file_btn = qtw.QPushButton("Change")
        change_cat_file_btn.clicked.connect(self._change_category_file)

        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._cat_lbl)
        hor_layout.addWidget(change_cat_file_btn)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        model_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Model Weights Path(pth):")
        self._weights_lbl = qtw.QLabel()
        change_weights_btn = qtw.QPushButton("Change")
        change_weights_btn.clicked.connect(self._change_model_weights_file)

        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._weights_lbl)
        hor_layout.addWidget(change_weights_btn)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        model_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Z-Norm:")
        self._z_norm_cb = qtw.QComboBox()
        self._z_norm_cb.addItems(["Yes","No"])

        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._z_norm_cb)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        model_layout.addLayout(hor_layout)

        width_lbl = qtw.QLabel("Image Width")
        self._model_img_width_spinbox = qtw.QSpinBox()
        self._model_img_width_spinbox.setMinimum(50)
        self._model_img_width_spinbox.setMaximum(2560)

        height_lbl = qtw.QLabel("Image Height")
        self._model_img_height_spinbox = qtw.QSpinBox()
        self._model_img_height_spinbox.setMinimum(50)
        self._model_img_height_spinbox.setMaximum(1440)

        hor_layout.addWidget(width_lbl)
        hor_layout.addWidget(self._model_img_width_spinbox)
        hor_layout.addStretch(1)

        hor_layout.addWidget(height_lbl)
        hor_layout.addWidget(self._model_img_height_spinbox)
        hor_layout.addStretch(2)


        return model_frame

    def _create_object_tracker_part_config(self)->qtw.QGroupBox:
        tracker_frame = qtw.QGroupBox("Object Tracker Config")
        tracker_frame.setAlignment(Qt.AlignHCenter)
        #tracker_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)

        tracker_layout = qtw.QVBoxLayout()
        tracker_frame.setLayout(tracker_layout)

        #thresholds
        thresh_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(thresh_layout)

        lbl = qtw.QLabel("Undetected Threshold:")
        self._undetected_thresh_spinbox = qtw.QSpinBox()
        self._undetected_thresh_spinbox.setMinimum(1)
        self._undetected_thresh_spinbox.setMaximum(300)

        thresh_layout.addWidget(lbl)
        thresh_layout.addWidget(self._undetected_thresh_spinbox)
        thresh_layout.addStretch(1)

        thresh_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(thresh_layout)

        lbl = qtw.QLabel("Tentative Track Threshold")
        self._tentative_thresh_spinbox = qtw.QSpinBox()
        self._tentative_thresh_spinbox.setMinimum(1)

        thresh_layout.addWidget(lbl)
        thresh_layout.addWidget(self._tentative_thresh_spinbox)
        thresh_layout.addStretch(1)

        thresh_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(thresh_layout)

        motion_lbl = qtw.QLabel("Motion Threshold:")
        self._motion_thresh_spinbox = qtw.QDoubleSpinBox()

        colour_lbl = qtw.QLabel("Colour Threshold:")
        self._colour_thresh_spinbox = qtw.QDoubleSpinBox()

        thresh_layout.addWidget(motion_lbl)
        thresh_layout.addWidget(self._motion_thresh_spinbox)
        thresh_layout.addWidget(colour_lbl)
        thresh_layout.addWidget(self._colour_thresh_spinbox)
        thresh_layout.addStretch(1)

        thresh_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(thresh_layout)

        save_lbl = qtw.QLabel("Save Tracks Threshold:")
        self._save_thresh_spinbox= qtw.QSpinBox()

        thresh_layout.addWidget(save_lbl)
        thresh_layout.addWidget(self._save_thresh_spinbox)
        thresh_layout.addStretch(1)

        tracker_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Start Track Id:")
        self._start_track_id_spinbox = qtw.QSpinBox()
        self._start_track_id_spinbox.setMinimum(1)
        self._start_track_id_spinbox.setMaximum(1e9)

        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._start_track_id_spinbox)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(hor_layout)

        thumbnail_lbl = qtw.QLabel("Thumbnail Save Path:")
        self._thumbnail_save_path_lbl = qtw.QLabel()
        thumbnail_save_path_change_btn = qtw.QPushButton("Change")
        thumbnail_save_path_change_btn.clicked.connect(self._change_thumbnail_save_path)

        hor_layout.addWidget(thumbnail_lbl)
        hor_layout.addWidget(self._thumbnail_save_path_lbl)
        hor_layout.addWidget(thumbnail_save_path_change_btn)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Dry Run:")
        self._dry_run_cb = qtw.QComboBox()
        self._dry_run_cb.addItems(["No","Yes"])

        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._dry_run_cb)
        hor_layout.addStretch(1)

        hor_layout = qtw.QHBoxLayout()
        tracker_layout.addLayout(hor_layout)

        lbl = qtw.QLabel("Visualise Tracking:")
        self._visualise_track_cb = qtw.QComboBox()
        self._visualise_track_cb.addItems(["No","Yes"])


        hor_layout.addWidget(lbl)
        hor_layout.addWidget(self._visualise_track_cb)
        hor_layout.addStretch(1)

        return tracker_frame

    #right slots
    def _change_category_file(self):
        cat_file_tpl = qtw.QFileDialog.getOpenFileName(self)

        cat_file = cat_file_tpl[0]

        if cat_file:
            self._cat_lbl.setText(cat_file)

    def _change_model_weights_file(self):
        weights_file_tpl = qtw.QFileDialog.getOpenFileName(self)

        weights_file = weights_file_tpl[0]

        if weights_file:
            self._weights_lbl.setText(weights_file)

    def _change_thumbnail_save_path(self):
        thumbnail_save_path = qtw.QFileDialog.getExistingDirectory(self)

        if thumbnail_save_path and thumbnail_save_path.strip():
            self._thumbnail_save_path_lbl.setText(thumbnail_save_path.strip())

    def _create_buttons(self):
        hor_layout = qtw.QHBoxLayout()

        self._default_btn = qtw.QPushButton("Reset To Default")
        self._default_btn.clicked.connect(self._default_values)

        self._save_btn = qtw.QPushButton("Save configuration")
        self._save_btn.clicked.connect(self._save_configuration)

        hor_layout.addWidget(self._default_btn)
        hor_layout.addStretch(1)
        hor_layout.addWidget(self._save_btn)
        #hor_layout.addStretch(1)

        self._main_layout.addLayout(hor_layout)

    def _check_bool_value(self,val:str)->bool:
        return True if val.lower() == "yes" else False

    def _get_str_value_from_bool(self,val:bool)->str:
        return "Yes" if val else "No"

    def _save_configuration(self):
        config = dict()

        #main part:
        config["main"] = dict()
        config["main"]["video_path"] = self._video_dir_lbl.text()
        config["main"]["min_width"] = self._width_spinbox.value()
        config["main"]["min_height"] = self._height_spinbox.value()
        config["main"]["show_gui"] = self._check_bool_value(self._show_gui_option.currentText())
        config["main"]["gui_speed"] = self._gui_timer_spinbox.value()

        #motion part:
        config["motion_detector"] = dict()
        config["motion_detector"]["measurement_stds"] = [
            self._x_std_spinbox.value(),
            self._y_std_spinbox.value(),
            self._width_std_spinbox.value(),
            self._height_std_spinbox.value()
        ]
        config["motion_detector"]["contour_area_threshold"] = self._contour_area_spinbox.value()
        config["motion_detector"]["detector_type"] = self._detector_combobox.currentText()

        #object tracker part
        config["object_tracker"] = dict()
        config["object_tracker"]["undetected_threshold"] = self._undetected_thresh_spinbox.value()
        config["object_tracker"]["tentative_track_threshold"] = self._tentative_thresh_spinbox.value()
        config["object_tracker"]["motion_threshold"] = self._motion_thresh_spinbox.value()
        config["object_tracker"]["colour_threshold"] = self._colour_thresh_spinbox.value()
        config["object_tracker"]["save_tracks_threshold"] = self._save_thresh_spinbox.value()
        config["object_tracker"]["start_track_id"] = self._start_track_id_spinbox.value()
        config["object_tracker"]["thumbnail_save_path"] = self._thumbnail_save_path_lbl.text()

        config["object_tracker"]["dry_run"] = self._check_bool_value(self._dry_run_cb.currentText())
        config["object_tracker"]["visualise"] = self._check_bool_value(self._visualise_track_cb.currentText())

        #model part
        config["model"] = dict()
        config["model"]["name"] =  self._model_name_cb.currentText()
        config["model"]["npz_file_path"] = self._cat_lbl.text()
        config["model"]["weights_file"] = self._weights_lbl.text()
        config["model"]["z_norm"] = self._check_bool_value(self._z_norm_cb.currentText())
        config["model"]["width"] = self._model_img_width_spinbox.value()
        config["model"]["height"] = self._model_img_height_spinbox.value()

        #db part
        config["db"] = dict()
        config["db"]["db_name"] = "surveillance_project"
        config["db"]["user"] = "macha"
        config["db"]["host"] = "localhost"


        try:
            with self._config_save_file_path.open('w') as bin_file_obj:
                yaml.safe_dump(config,bin_file_obj)
        except:
            print("Error")

    def _set_values_from_configuration(self):
        with self._config_save_file_path.open('r') as file_obj:
            config = yaml.safe_load(file_obj)

        #default values for the main part
        self._video_dir_lbl.setText(config.get("main",{}).get("video_path","./assets/videos"))
        self._width_spinbox.setValue(config.get("main",{}).get("min_width",1280))
        self._height_spinbox.setValue(config.get("main",{}).get("min_height",720))
        self._show_gui_option.setCurrentText(self._get_str_value_from_bool(config.get("main",{}).get("show_gui",True)))
        self._gui_timer_spinbox.setValue(config.get("main",{}).get("gui_speed",1))

        #default values for the motion part

        #measurement standard deviations
        stds = config.get("motion_detector",{}).get("measurement_stds",[3,3,10,10])
        self._x_std_spinbox.setValue(stds[0])
        self._y_std_spinbox.setValue(stds[1])
        self._width_std_spinbox.setValue(stds[2])
        self._height_std_spinbox.setValue(stds[3])

        self._contour_area_spinbox.setValue(config.get("motion_detector",{}).get("contour_area_threshold",150))
        self._detector_combobox.setCurrentText(config.get("motion_detector",{}).get("detector_type","background_subtractor"))

        #default values for the model part config
        self._model_name_cb.setCurrentText(config.get("model",{}).get("name","squeezenet_1_1"))
        self._cat_lbl.setText(config.get("model",{}).get("npz_file_path","./assets/model/pyt_classes.npz"))
        self._weights_lbl.setText(config.get("model",{}).get("weights_file","./assets/model/pyt_squeezenet_model.pth"))
        self._model_img_width_spinbox.setValue(config.get("model",{}).get("width",224))
        self._model_img_height_spinbox.setValue(config.get("model",{}).get("height",224))
        self._z_norm_cb.setCurrentText(self._get_str_value_from_bool(config.get("model",{}).get("z_norm",True)))

        #default values for the object tracker part config
        self._undetected_thresh_spinbox.setValue(config.get("object_tracker",{}).get("undetected_threshold",20))
        self._tentative_thresh_spinbox.setValue(config.get("object_tracker",{}).get("tentative_track_threshold",5))
        self._motion_thresh_spinbox.setValue(config.get("object_tracker",{}).get("motion_threshold",13.28))
        self._colour_thresh_spinbox.setValue(config.get("object_tracker",{}).get("colour_threshold",0.4))
        self._save_thresh_spinbox.setValue(config.get("object_tracker",{}).get("save_tracks_threshold",32))
        self._start_track_id_spinbox.setValue(config.get("object_tracker",{}).get("start_track_id",1))
        self._thumbnail_save_path_lbl.setText(config.get("object_tracker",{}).get("thumbnail_save_path","./assets/.db/thumbnail_images"))
        self._visualise_track_cb.setCurrentText(self._get_str_value_from_bool(config.get("object_tracker",{}).get("visualise",True)))
        self._dry_run_cb.setCurrentText(self._get_str_value_from_bool(config.get("object_tracker",{}).get("dry_run",False)))

