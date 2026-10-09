import PySide6.QtWidgets as qtw

from PySide6.QtCore import Qt

class QueryWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self._main_layout = qtw.QVBoxLayout()

        self._init_ui()

        self.setLayout(self._main_layout)

    def _init_ui(self):
        hor_layout = qtw.QHBoxLayout()

        self._create_query_insertion_part(hor_layout)
        self._create_processed_query_part(hor_layout)

        self._create_query_options_part(hor_layout)

        #hor_layout.addStretch(1)

        start_btn = qtw.QPushButton("Start Search and Retrieval")
        start_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        self._main_layout.addLayout(hor_layout)
        self._main_layout.addStretch(1)
        self._main_layout.addWidget(start_btn,alignment=Qt.AlignCenter)
        self._main_layout.addStretch(2)

    def _create_query_insertion_part(self,hor_layout):
        layout = qtw.QVBoxLayout()

        lbl = qtw.QLabel("Query Image")
        #layout.addWidget(lbl,alignment=Qt.AlignCenter)
        layout.addWidget(lbl)

        img_frame = qtw.QFrame()
        img_frame.setMaximumHeight(350)
        img_frame.setMinimumHeight(200)
        img_frame.setMaximumWidth(350)
        img_frame.setMinimumWidth(200)
        img_frame.setFixedHeight(400)
        img_frame.setFixedWidth(350)
        img_frame.setFrameStyle(qtw.QFrame.StyledPanel|qtw.QFrame.Sunken)
        #img_frame.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        layout.addWidget(img_frame)


        img_layout = qtw.QHBoxLayout()

        insert_image_btn = qtw.QPushButton("Insert\n Image")
        insert_image_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
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

    def _create_query_options_part(self,hor_layout):
        db_lbl = qtw.QLabel("Choose DB Table To Search From")

        db_combobox = qtw.QComboBox()
        db_combobox.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        db_combobox.addItems(["table_1","table_2","table_table_3"])

        colour_descriptor_cb = qtw.QCheckBox("Use Colour Descriptor")
        shape_descriptor_cb = qtw.QCheckBox("Use Shape Descriptor")
        category_cb = qtw.QCheckBox("Use specific category")

        cat_combobox = qtw.QComboBox()
        cat_combobox.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        cat_combobox.addItems(["placeholder_1","placeholder_2","placeholder_3"])

        #inserting into layout (vertical)
        ver_layout = qtw.QVBoxLayout()

        #ver_layout.addStretch(1)
        ver_layout.addWidget(db_lbl)
        ver_layout.addWidget(db_combobox)
        ver_layout.addWidget(colour_descriptor_cb)
        ver_layout.addWidget(shape_descriptor_cb)
        ver_layout.addWidget(category_cb)
        ver_layout.addWidget(cat_combobox)
        ver_layout.addStretch(1)

        hor_layout.addLayout(ver_layout)

    def _create_processed_query_part(self,hor_layout):
        layout = qtw.QVBoxLayout()

        lbl = qtw.QLabel("Processed Image")
        layout.addWidget(lbl,alignment=Qt.AlignCenter)

        img_frame = qtw.QFrame()
        img_frame.setMaximumHeight(350)
        img_frame.setMinimumHeight(200)
        img_frame.setMaximumWidth(350)
        img_frame.setMinimumWidth(200)
        img_frame.setFixedHeight(400)
        img_frame.setFixedWidth(350)
        #img_frame.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        img_frame.setFrameStyle(qtw.QFrame.StyledPanel|qtw.QFrame.Sunken)
        layout.addWidget(img_frame)
        layout.addStretch(1)

        #processed image options
        config_layout = qtw.QVBoxLayout()
        lbl = qtw.QLabel("Config Options")
        invert_btn = qtw.QPushButton("Invert Image")
        invert_btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)

        manual_thresh_cb = qtw.QCheckBox("Manual Threshold")

        manual_thresh_slider = qtw.QSlider(Qt.Orientation.Horizontal)
        manual_thresh_slider.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Preferred)
        manual_thresh_slider.setMinimum(0)
        manual_thresh_slider.setMaximum(255)

        config_layout.addWidget(lbl)
        config_layout.addWidget(invert_btn)
        config_layout.addWidget(manual_thresh_cb)
        config_layout.addWidget(manual_thresh_slider)
        config_layout.addStretch(1)


        hor_layout.addStretch(1)
        hor_layout.addLayout(config_layout)
        hor_layout.addStretch(1)
        hor_layout.addLayout(layout)
        hor_layout.addStretch(1)


