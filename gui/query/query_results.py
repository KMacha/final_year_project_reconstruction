import cv2
import numpy as np
import PySide6.QtWidgets as qtw

from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QPixmap,QAction

from gui.preview import PreviewVideoWindow

class QueryResultsWindow(qtw.QStackedWidget):
    _back_to_querying = Signal()

    def __init__(self,db_obj):
        super().__init__()

        self._previous_query_results,self._query_results = list(),list()

        self._images_per_row = 5
        self._db_obj = db_obj

        #self._results_layout = qtw.QVBoxLayout()

        self._preview_window = PreviewVideoWindow()

        self._main_results_widget = qtw.QWidget()

        self._headers_frame = qtw.QFrame()
        self._headers_layout = qtw.QHBoxLayout()
        self._headers_frame.setLayout(self._headers_layout)

        self._results_widget = qtw.QWidget()
        self._results_layout = qtw.QVBoxLayout()
        self._results_widget.setLayout(self._results_layout)

        self._main_layout = qtw.QVBoxLayout()


        #init the ui for the results_widget before adding it to the scrollarea
        self._init_ui()

        self._scroll_area = qtw.QScrollArea()
        self._scroll_area.setWidget(self._results_widget)
        self._scroll_area.setWidgetResizable(True)

        self._main_layout.addWidget(self._headers_frame)
        self._main_layout.addWidget(self._scroll_area)

        self._main_results_widget.setLayout(self._main_layout)

        self.addWidget(self._main_results_widget)
        self.addWidget(self._preview_window)

        self.setCurrentWidget(self._main_results_widget)

        self._preview_window._back_to_offline.connect(lambda: self.setCurrentWidget(self._main_results_widget))

    def _create_header(self):
        back_to_querying_btn = qtw.QPushButton("Back To Querying")
        back_to_querying_btn.clicked.connect(self._back_to_query)
        self._headers_layout.addWidget(back_to_querying_btn)

        self._back_to_previous_results_btn = qtw.QPushButton("Back To Previous Results")
        self._back_to_previous_results_btn.setEnabled(False)

        self._back_to_previous_results_btn.clicked.connect(self._back_to_previous_results)
        self._headers_layout.addWidget(self._back_to_previous_results_btn)

        self._headers_layout.addStretch(1)

        self._header_res_lbl = qtw.QLabel()
        self._headers_layout.addWidget(self._header_res_lbl)

        #self._headers_layout.addStretch(1)

        all_res_btn = qtw.QPushButton("Show all Results")
        all_res_btn.clicked.connect(lambda: self._clear_results_layout(self._results_layout))
        self._headers_layout.addWidget(all_res_btn)

        self._headers_layout.addStretch(1)

    def _init_ui(self):
        self._create_header()

    def show_results(self,query_results:list[dict],refined_results:bool=False):
        self._clear_results_layout(layout = self._results_layout)

        if refined_results:
            #when refining results from previous results, store the previous results, so we can have a way of going back to them
            if len(self._previous_query_results) and self._previous_query_results[-1] != self._query_results:
                self._previous_query_results.append(self._query_results)
            else:
                self._previous_query_results.append(self._query_results)
        else:
            #when not refining, if there are no previous_query_results, add the current ones to the previous list, for incase we start refining
            #we won't loose the reference to the original result, i.e. index 0, always holds the reference to the original results that came from the querying process not the refining process
            if len(self._previous_query_results) <= 1:
                self._previous_query_results.append(query_results)
                self._back_to_previous_results_btn.setEnabled(False)

        self._query_results = query_results

        self._header_res_lbl.setText(f"Showing Top {len(query_results)} Results")

        row_layout = None
        for i,query_res in enumerate(query_results):
            if i%self._images_per_row == 0:
                row_layout = qtw.QHBoxLayout()
                self._results_layout.addLayout(row_layout)

            img_path = query_res["thumbnail_image_path"]
            img_cat = query_res["category"]
            thumbnail_frame = self.create_thumbnail_frame(
                idx = i,
                thumbnail_img_path = img_path,
                img_category = img_cat
            )
            row_layout.addWidget(thumbnail_frame)

        self._scroll_area.setWidget(self._results_widget)
        #self._main_layout.addWidget(self._scroll_area)

    def create_thumbnail_frame(self,idx:int,thumbnail_img_path:str,img_category:str="other")->qtw.QFrame:
        frame_layout = qtw.QVBoxLayout()

        thumbnail_frame = qtw.QFrame()
        thumbnail_frame.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Sunken)
        thumbnail_frame.setLayout(frame_layout)

        thumbnail_frame.setMinimumSize(200,200)
        thumbnail_frame.setContextMenuPolicy(Qt.CustomContextMenu)
        thumbnail_frame.customContextMenuRequested.connect(
            lambda pos: self._thumbnail_frame_context_menu(idx,thumbnail_frame,pos)
        )

        thumbnail_lbl = qtw.QLabel()
        img_pixmap = QPixmap(thumbnail_img_path)
        #thumbnail_lbl.setPixmap(img_pixmap.scaled(
        #    thumbnail_lbl.size(),
        #    Qt.KeepAspectRatio
        #))
        thumbnail_lbl.setPixmap(img_pixmap)
        thumbnail_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(thumbnail_lbl)

        thumbnail_cat_lbl = qtw.QLabel(img_category)
        thumbnail_cat_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(thumbnail_cat_lbl)


        btn_layout = qtw.QHBoxLayout()

        preview_video_btn = qtw.QPushButton("Preview\n Video")
        preview_video_btn.clicked.connect(lambda: self._preview_result(idx = idx))

        refine_search_btn = qtw.QPushButton("Use To\n Refine Search")
        refine_search_btn.clicked.connect(lambda: self._refine_search_with_result(idx = idx))

        btn_layout.addWidget(preview_video_btn)
        btn_layout.addWidget(refine_search_btn)

        frame_layout.addLayout(btn_layout)

        return thumbnail_frame

    #slots
    def _back_to_query(self):
        self._back_to_querying.emit()

    def _back_to_previous_results(self):
        self.show_results(self._previous_query_results.pop())

    def _clear_results_layout(self,layout):
        while (item:=layout.takeAt(0)) is not None:
            widget = item.widget()
            child_layout = item.layout()

            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_results_layout(child_layout)

            del item

    def _thumbnail_frame_context_menu(self,idx,frame,pos):
        preview_video_action = QAction("Preview Video",frame)
        preview_video_action.triggered.connect(lambda: self._preview_result(idx))

        refine_search_using_colour_action = QAction("Refine Search Using Colour Feature",frame)
        refine_search_using_colour_action.triggered.connect(lambda: self._refine_search_with_result(idx,"colour"))

        refine_search_using_shape_action = QAction("Refine Search Using Shape Feature",frame)
        refine_search_using_shape_action.triggered.connect(lambda: self._refine_search_with_result(idx,"shape"))

        refine_search_action = QAction("Refine Search Using Both Features",frame)
        refine_search_action.triggered.connect(lambda: self._refine_search_with_result(idx))

        context_menu = qtw.QMenu(frame)

        context_menu.addAction(preview_video_action)
        context_menu.addAction(refine_search_using_colour_action)
        context_menu.addAction(refine_search_using_shape_action)
        context_menu.addAction(refine_search_action)

        context_menu.exec(frame.mapToGlobal(pos))

    def _preview_result(self,idx:int):
        video_path = "/home/macha/Programming/projects/final_year_project_recreation/assets/videos/vtest.avi"
        #video_path = self._query_results[idx]["video_path"]
        start_timestamp = self._query_results[idx]["start_timestamp"]
        end_timestamp = self._query_results[idx]["end_timestamp"]

        print(f"Start time stamp: {start_timestamp}")
        print(f"end time stamp: {end_timestamp}")

        self.setCurrentWidget(self._preview_window)

        self._preview_window.set_video_speed(30)
        self._preview_window.set_video_path(video_path)
        self._preview_window.set_up_video(
            start_time_ms = start_timestamp,
            end_time_ms = end_timestamp
        )

    def _refine_results_by_all_features(self,idx:int,results:list,limit:int=20)->list:
        query_colour_feature = np.array(self._query_results[idx]["colour_histogram"]).astype(np.float32)
        #shape_feature = np.array(self._query_results[idx]["shape_feature"]).astype(np.float32)

        colour_costs = np.array([cv2.compareHist(query_colour_feature,np.array(result["colour_histogram"]).astype(np.float32),cv2.HISTCMP_BHATTACHARYYA) for result in results])
        shape_costs = np.array([result["shape_cost"] for result in results])

        costs = 0.5*colour_costs + 0.5*shape_costs

        results_costs = sorted(zip(results,costs),key=lambda x: x[1])

        return [result for result,_ in results_costs[:limit]]

    def _refine_results_by_colour(self,idx:int,results:list,limit:int=20)->list:
        query_colour_feature = np.array(self._query_results[idx]["colour_histogram"]).astype(np.float32)

        colour_costs = [cv2.compareHist(query_colour_feature,np.array(result["colour_histogram"]).astype(np.float32),cv2.HISTCMP_BHATTACHARYYA) for result in results]

        results_costs = sorted(zip(results,colour_costs),key=lambda x: x[1])

        return [result for result,_ in results_costs[:limit]]

    def _refine_search_with_result(self,idx:int,features:str="all"):
        match features:
            case "shape":
                self._back_to_previous_results_btn.setEnabled(True)

                results = self._db_obj.query_by_shape_feature(
                    table_name = "test",
                    shape_feature = self._query_results[idx]["shape_feature"]
                )

                self.show_results(
                    query_results = results,
                    refined_results = True
                )


            case "colour":
                self._back_to_previous_results_btn.setEnabled(True)

                results = self._db_obj.query_by_colour_feature(table_name = "test")

                results = self._refine_results_by_colour(idx,results)

                self.show_results(
                    query_results = results,
                    refined_results = True
                )
            case _:
                self._back_to_previous_results_btn.setEnabled(True)

                results = self._db_obj.query_by_all_features(
                    table_name = "test",
                    shape_feature = self._query_results[idx]["shape_feature"]
                )

                results = self._refine_results_by_all_features(idx,results)

                self.show_results(
                    query_results = results,
                    refined_results = True
                )



