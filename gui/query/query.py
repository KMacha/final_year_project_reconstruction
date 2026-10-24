import cv2
import numpy as np
import PySide6.QtWidgets as qtw

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QImage

from gui.query.query_results import QueryResultsWindow

from feature_extraction.colour_descriptor import get_colour_descriptor
from feature_extraction.shape_descriptor import get_fourier_descriptor
from motion_detection.detector import get_contours
from database.database import Database

class QueryWindow(qtw.QStackedWidget):
    def __init__(self):
        super().__init__()

        self._db_obj = Database({
            "db_name":"surveillance_project",
            "user": "macha",
            "host": "localhost",
            "table_name": None
        })

        self._selected_category = None
        self._thresh_img = None
        self._use_colour_descriptor = self._use_shape_descriptor = False

        self._query_results_widget = QueryResultsWindow(
            db_obj = self._db_obj
        )

        self._query_widget = qtw.QWidget()
        self._main_layout = qtw.QVBoxLayout()

        self._init_ui()

        self._query_widget.setLayout(self._main_layout)

        self.addWidget(self._query_results_widget)
        self.addWidget(self._query_widget)

        self.setCurrentWidget(self._query_widget)

        self._query_results_widget._back_to_querying.connect(lambda: self.setCurrentWidget(self._query_widget))

    def _init_ui(self):
        hor_layout = qtw.QHBoxLayout()

        self._create_query_insertion_part(hor_layout)
        self._create_processed_query_part(hor_layout)

        self._create_query_options_part(hor_layout)

        #hor_layout.addStretch(1)

        start_btn = qtw.QPushButton("Start Search and Retrieval")
        start_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        start_btn.clicked.connect(self.search_and_retrieval)

        self._main_layout.addLayout(hor_layout)
        self._main_layout.addStretch(1)
        self._main_layout.addWidget(start_btn,alignment=Qt.AlignCenter)
        self._main_layout.addStretch(2)

    def _create_query_insertion_part(self,hor_layout):
        layout = qtw.QVBoxLayout()

        lbl = qtw.QLabel("Query Image")
        #layout.addWidget(lbl,alignment=Qt.AlignCenter)
        layout.addWidget(lbl)

        frame_ver_layout = qtw.QVBoxLayout()
        img_frame = qtw.QFrame()
        img_frame.setLayout(frame_ver_layout)

        img_frame.setMaximumHeight(350)
        img_frame.setMinimumHeight(200)
        img_frame.setMaximumWidth(350)
        img_frame.setMinimumWidth(200)
        img_frame.setFixedHeight(400)
        img_frame.setFixedWidth(350)
        img_frame.setFrameStyle(qtw.QFrame.StyledPanel|qtw.QFrame.Sunken)

        self._query_img_lbl = qtw.QLabel()
        frame_ver_layout.addWidget(self._query_img_lbl)
        #img_frame.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        layout.addWidget(img_frame)


        img_layout = qtw.QHBoxLayout()

        insert_image_btn = qtw.QPushButton("Insert\n Image")
        insert_image_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        insert_image_btn.clicked.connect(self.insert_image)

        sketch_image_btn = qtw.QPushButton("Sketch\n Image")
        sketch_image_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        img_layout.setSpacing(0)
        img_layout.addWidget(insert_image_btn,alignment=Qt.AlignCenter)
        img_layout.addWidget(sketch_image_btn,alignment=Qt.AlignCenter)
        img_layout.addStretch(1)
        #img_layout.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        layout.addLayout(img_layout)
        layout.addStretch(1)

        hor_layout.addLayout(layout)

    def _get_categories(self)->list:
        cat_path = "./assets/model/pyt_classes.npz"

        npz_obj = np.load(cat_path)

        return npz_obj["arr_0"]

    def _create_query_options_part(self,hor_layout):
        db_lbl = qtw.QLabel("Choose DB Table To Search From")

        self._db_tbl_combobox = qtw.QComboBox()
        self._db_tbl_combobox.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        #TODO: Make it dynamic perhaps using MVC???? 
        #TODO: Because of incase of when someone does processing of video and then comes straight to querying, the newly created
        #table won't be available
        tables = self._db_obj._get_db_tables()
        self._db_tbl_combobox.addItems(tables)

        colour_descriptor_cb = qtw.QCheckBox("Use Colour Descriptor")
        colour_descriptor_cb.stateChanged.connect(self._set_colour_descriptor_usage)

        shape_descriptor_cb = qtw.QCheckBox("Use Shape Descriptor")
        shape_descriptor_cb.stateChanged.connect(self._set_shape_descriptor_usage)

        category_cb = qtw.QCheckBox("Use specific category")
        category_cb.stateChanged.connect(self._enable_disable_category_search)

        self._cat_combobox = qtw.QComboBox()
        self._cat_combobox.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        self._cat_combobox.setEnabled(False)

        self._categories = self._get_categories()
        self._cat_combobox.addItems(self._categories)
        self._cat_combobox.currentTextChanged.connect(self._change_query_category)

        #inserting into layout (vertical)
        ver_layout = qtw.QVBoxLayout()

        #ver_layout.addStretch(1)
        ver_layout.addWidget(db_lbl)
        ver_layout.addWidget(self._db_tbl_combobox)
        ver_layout.addWidget(colour_descriptor_cb)
        ver_layout.addWidget(shape_descriptor_cb)
        ver_layout.addWidget(category_cb)
        ver_layout.addWidget(self._cat_combobox)
        ver_layout.addStretch(1)

        hor_layout.addLayout(ver_layout)

    def _create_processed_query_part(self,hor_layout):
        layout = qtw.QVBoxLayout()

        lbl = qtw.QLabel("Processed Image")
        layout.addWidget(lbl,alignment=Qt.AlignCenter)

        frame_layout = qtw.QVBoxLayout()
        img_frame = qtw.QFrame()
        img_frame.setLayout(frame_layout)
        img_frame.setMaximumHeight(350)
        img_frame.setMinimumHeight(200)
        img_frame.setMaximumWidth(350)
        img_frame.setMinimumWidth(200)
        img_frame.setFixedHeight(400)
        img_frame.setFixedWidth(350)
        #img_frame.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        img_frame.setFrameStyle(qtw.QFrame.StyledPanel|qtw.QFrame.Sunken)

        self._processed_img_lbl = qtw.QLabel()
        frame_layout.addWidget(self._processed_img_lbl)

        layout.addWidget(img_frame)
        layout.addStretch(1)

        #processed image options
        config_layout = qtw.QVBoxLayout()
        lbl = qtw.QLabel("Config Options")

        invert_btn = qtw.QPushButton("Invert Image")
        invert_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        invert_btn.clicked.connect(self.invert_image)

        self._manual_thresh_cb = qtw.QCheckBox("Manual Threshold")
        self._manual_thresh_cb.stateChanged.connect(self._enable_manual_thresholding)

        self._manual_thresh_slider = qtw.QSlider(Qt.Orientation.Horizontal)
        self._manual_thresh_slider.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        self._manual_thresh_slider.setMinimum(0)
        self._manual_thresh_slider.setMaximum(255)
        self._manual_thresh_slider.valueChanged.connect(self.process_by_manual_threshold)
        self._manual_thresh_slider.setEnabled(False)

        config_layout.addWidget(lbl)
        config_layout.addWidget(invert_btn)
        config_layout.addWidget(self._manual_thresh_cb)
        config_layout.addWidget(self._manual_thresh_slider)
        config_layout.addStretch(1)


        hor_layout.addStretch(1)
        hor_layout.addLayout(config_layout)
        hor_layout.addStretch(1)
        hor_layout.addLayout(layout)
        hor_layout.addStretch(1)

    def _sort_by_all_features(self,query_colour_feature:np.ndarray,results:list[dict],limit:int=20)->list[dict]:
        colour_costs = np.array([cv2.compareHist(query_colour_feature,np.array(result["colour_histogram"]).astype(np.float32),cv2.HISTCMP_BHATTACHARYYA) for result in results])
        shape_costs = np.array([result["shape_cost"] for result in results])

        costs = 0.5*colour_costs + 0.5*shape_costs

        results_costs = sorted(zip(results,costs),key=lambda x: x[1])

        return [result for result,_ in results_costs[:limit]]

    def _get_top_k_colour_results(self,colour_feature,results:list,limit:int=20)->list[dict]:
        colour_costs = [cv2.compareHist(colour_feature,np.array(result["colour_histogram"]).astype(np.float32),cv2.HISTCMP_BHATTACHARYYA) for result in results]

        results_costs = sorted(zip(results,colour_costs),key=lambda x: x[1])

        return [result for result,_ in results_costs[:limit]]

    #slots
    def _change_query_category(self,selected_category:str):
        self._selected_category = selected_category

    def insert_image(self):
        img_path_tpl = qtw.QFileDialog.getOpenFileName(self)

        img_path = img_path_tpl[0]

        if img_path:
            pixmap = QPixmap(img_path)

            self._query_img = cv2.resize(cv2.imread(img_path),(300,300))
            query_qimg = QImage(
                self._query_img,
                self._query_img.shape[1],
                self._query_img.shape[0],
                QImage.Format_BGR888
            )
            self._query_img_lbl.setPixmap(QPixmap.fromImage(query_qimg))

            self.process_query_image()
        else:
            print("File not selected")

    def process_query_image(self):
        query_img = cv2.cvtColor(self._query_img,cv2.COLOR_BGR2GRAY)
        query_img = cv2.GaussianBlur(query_img,(5,5),0)
        _,self._thresh_img = cv2.threshold(query_img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        processed_qimg = QImage(
            self._thresh_img,
            self._thresh_img.shape[1],
            self._thresh_img.shape[0],
            QImage.Format_Grayscale8
        )

        self._processed_img_lbl.setPixmap(QPixmap.fromImage(processed_qimg))

    def _enable_manual_thresholding(self,state:int):
        if state == Qt.Checked.value:
            self._manual_thresh_slider.setEnabled(True)
        else:
            self._manual_thresh_slider.setEnabled(False)

    def process_by_manual_threshold(self,thresh_val):
        query_img = cv2.cvtColor(self._query_img,cv2.COLOR_BGR2GRAY)
        query_img = cv2.GaussianBlur(query_img,(5,5),0)

        _,self._thresh_img = cv2.threshold(query_img,thresh_val,255,cv2.THRESH_BINARY)

        processed_qimg = QImage(
            self._thresh_img,
            self._thresh_img.shape[1],
            self._thresh_img.shape[0],
            QImage.Format_Grayscale8
        )

        self._processed_img_lbl.setPixmap(QPixmap.fromImage(processed_qimg))

    def invert_image(self):
        self._thresh_img = cv2.bitwise_not(self._thresh_img)
        processed_qimg = QImage(
            self._thresh_img,
            self._thresh_img.shape[1],
            self._thresh_img.shape[0],
            QImage.Format_Grayscale8
        )

        self._processed_img_lbl.setPixmap(QPixmap.fromImage(processed_qimg))

    def search_and_retrieval(self):
        filter_str,filter_tpl = None,None

        vals_dict = dict()

        shape_descriptor = None
        colour_descriptor = None
        contour = None

        if self._thresh_img is not None and (self._use_shape_descriptor or self._use_colour_descriptor):
            print("using shape descriptor")
            contour = get_contours(
                thresh_img = self._thresh_img,
                return_all=False
            )

            #we only pass in the contour and leave the other as default as was used for the offline processing
            if self._use_shape_descriptor:
                shape_descriptor = get_fourier_descriptor(contour = contour).tolist()

        if self._use_colour_descriptor:
            print("Using colour descriptor")
            if contour is not None:
                x,y,w,h = cv2.boundingRect(contour)
                x_1 = x+w
                y_1 = y+h

                bboxes = [(x,x_1,y,y_1)]

                colour_descriptor = get_colour_descriptor(
                    frame = self._query_img,
                    contours = [contour],
                    images_bboxes = bboxes
                )[0]


        if self._selected_category:
            filter_str = "category = %(cat)s"
            vals_dict["cat"] = self._selected_category

        results = list()

        if self._use_shape_descriptor and not self._use_colour_descriptor:
            results = self._db_obj.query_by_shape_feature(
                table_name = "test",
                shape_feature = str(shape_descriptor),
                filter_str = filter_str,
                vals_dict = vals_dict
            )
        elif self._use_colour_descriptor and not self._use_shape_descriptor:
            results = self._db_obj.query_by_colour_feature(
                table_name = "test",
                filter_str = filter_str,
                vals_dict = vals_dict
            )

            results = self._get_top_k_colour_results(colour_descriptor,results)
        elif self._use_colour_descriptor and self._use_shape_descriptor:
            print("querying with both")
            results = self._db_obj.query_by_all_features(
                table_name = "test",
                shape_feature = str(shape_descriptor),
                filter_str = filter_str,
                vals_dict = vals_dict
            )

            results = self._sort_by_all_features(
                query_colour_feature = colour_descriptor,
                results = results
            )
            #print(len(results))
        else:
            results = self._db_obj.query(
                table_name = "test",
                filter_str = filter_str,
                vals_dict = vals_dict,
            )
        #print(results)

        self._query_results_widget.show_results(results)
        self.setCurrentWidget(self._query_results_widget)


    def _set_colour_descriptor_usage(self,value):
        self._use_colour_descriptor = value == Qt.Checked.value

    def _set_shape_descriptor_usage(self,value):
        self._use_shape_descriptor = value == Qt.Checked.value

    def _enable_disable_category_search(self,value:int):
        if value == Qt.Checked.value:
            self._cat_combobox.setEnabled(True)

            #once the combobox is enabled, we set the first category as the selected one
            #since it wouldn't emit the currentTextChanged signal
            self._selected_category = self._categories[0]
        else:
            self._cat_combobox.setEnabled(False)

            #when not using the categories set to None (obviously)
            self._selected_category = None
