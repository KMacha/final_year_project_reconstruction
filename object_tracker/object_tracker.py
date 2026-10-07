import time
import uuid
import cv2
import numpy as np

from scipy.optimize import linear_sum_assignment
from pathlib import Path

from object_tracker.kalman_matrix_configs import get_kalman_filter_matrices
from object_tracker.kalman_filter import KalmanFilter
from classifier.inference import Inference
from database.database import Database

#maintains an object track, i.e. a kalman filter dedicated to tracking one object
class ObjectTrack(KalmanFilter):
    def _configure_variables(self,track_id):
        self.track_id = track_id

        #variable to control whether this track is a tentative one, or whether it has been observed multiple times
        #to be an established (confirmed) track
        self.confirmed_track = False

        #variable to keep track of how many times this track has gone without a detection 
        self.total_undetected_frames = 0

        #variable to keep track of how many times this track has tracked an object.
        self.num_frames_tracked = 0


    def __init__(
        self,
        initial_measurements:dict,
        delta_t:float,
        measurement_stds:list[float],
        track_id:int,
        track_bbox:tuple|None=None,
        track_colour_hist:np.ndarray|None=None,
        track_shape_feature:np.ndarray|None = None,
        thumbnail_image:np.ndarray|None = None,
        thumbnail_area:float = 0,
        track_start_timestamp:float|None = None,
        alpha:float=0.1
    ):
        #initialising some needed variables
        self.bbox = track_bbox
        self.track_colour_hist = track_colour_hist
        self.track_shape_feature = track_shape_feature
        self.alpha = alpha
        self.track_start_timestamp = track_start_timestamp
        self.track_end_timestamp = track_start_timestamp

        #the thumbnail image will be used to get the image category later before saving
        self.thumbnail_area = thumbnail_area
        self.thumbnail_image = thumbnail_image

        matrices = get_kalman_filter_matrices(
            initial_measurements = initial_measurements,
            delta_t = delta_t,
            measurement_stds = measurement_stds
        )

        measurement_covariance_matrix = np.diag(np.square(measurement_stds))

        #retired
        #measurement_covariance_matrix = np.array([
        #    [measurement_stds**2,0],
        #    [0,measurement_stds**2]
        #])

        #initialise the kalman filter
        super().__init__(
            observation_matrix = matrices["observation_matrix"],
            initial_state = matrices["initial_state"],
            state_transition_matrix = matrices["state_transition_matrix"],
            estimate_covariance_matrix = matrices["estimate_covariance_matrix"],
            measurement_covariance_matrix = measurement_covariance_matrix,
            process_noise_matrix = matrices["process_noise_matrix"]
        )

        #configure needed variables to maintain the object track
        self._configure_variables(track_id)

        #it has just been initialised hence set to 1
        self.num_frames_tracked = 1

        #after initialisation first predict for the next state
        self.predict()


    #helper methods
    def is_tentative_track(self)->bool:
        return not self.confirmed_track

    def is_confirmed_track(self)->bool:
        return self.confirmed_track

    def get_total_tracked_frames(self)->int:
        return self.num_frames_tracked

    def get_total_undetected_frames(self)->int:
        return self.total_undetected_frames

    def get_bbox(self)->tuple:
        return self.bbox

    def get_thumbnail_image(self):
        return self.thumbnail_image

    def get_save_info(self):
        #returns the information about this track, as a dict,
        #where the keys are the column names as in the database/ saving medium for easy saving
        return {
            "total_frames_tracked": self.num_frames_tracked,
            "colour_histogram":self.track_colour_hist.tolist(),
            "shape_feature": self.track_shape_feature.tolist(),
            "start_timestamp": self.track_start_timestamp,
            "end_timestamp": self.track_end_timestamp,
        }

    def set_confirmed(self,is_confirmed:bool=True):
        self.confirmed_track = is_confirmed

    def update_thumbnail_image(self,thumbnail_image:np.ndarray|None,thumbnail_area:float=0):
        if thumbnail_image is not None and thumbnail_area > self.thumbnail_area:
            self.thumbnail_image = thumbnail_image

    def update_shape_feature_info(self,shape_feature):
        if shape_feature is None:
            return

        self.track_shape_feature = (1-self.alpha) * self.track_shape_feature + self.alpha * shape_feature

    def update_colour_info(self,colour_hist):
        if colour_hist is None:
            return

        if self.track_colour_hist is None:
            self.track_colour_hist = colour_hist
        else:
            self.track_colour_hist = (1 - self.alpha) * self.track_colour_hist + self.alpha * colour_hist

    def update_time(self,track_timestamp):
        if self.track_start_timestamp is None:
            self.track_start_timestamp = track_timestamp

        self.track_end_timestamp = track_timestamp

    def set_bbox(self,bbox:tuple):
        self.bbox = bbox


    def _get_colour_distance(self,colour_hist)->np.float64:
        return cv2.compareHist(self.track_colour_hist,colour_hist,cv2.HISTCMP_BHATTACHARYYA)

    def _get_motion_cost(self,measurement:tuple)->np.float64:
        measurement_arr = np.array(measurement).reshape(-1,1)

        #get the predicted next measurement from the whole state
        pred_state = self.next_state_prediction[:4]

        #get first the difference between the measurement and state 
        diff_z_s = measurement_arr - pred_state

        #get the covariance 
        cov = self.observation_matrix @ self.next_estimate_covariance_prediction @ self.observation_matrix.T + self.measurement_covariance_matrix

        motion_cost = (diff_z_s.T @ np.linalg.inv(cov) @ diff_z_s).item()

        return motion_cost


    def get_cost(self,measurement:tuple,measured_colour_hist=None)->(np.float64,np.float64):
        #squared mahalanobis distance
        #mahalanobis distance: np.sqrt((x-y).T @ np.linalg.inv(covariance_x_y) @ (x-y))

        motion_cost = self._get_motion_cost(measurement)

        colour_distance = None
        if measured_colour_hist is not None:
            colour_distance = cv2.compareHist(self.track_colour_hist,measured_colour_hist,cv2.HISTCMP_BHATTACHARYYA)

        return motion_cost,colour_distance

    def blind_predict(self):
        #blind predict, basically when the object_track hasn't been associated with any detection,
        #use the predicted states, to get future predictions
        #add to the number of times the track hasn't been detected
        self.total_undetected_frames+=1

        #set predictions to the current estimates and then predict
        self.curr_state_estimate = self.next_state_prediction
        self.curr_estimate_covariance_matrix = self.next_estimate_covariance_prediction

        self.predict()

    def update_predict(self,measurement:tuple|list):
        #updates/corrects  and predicts for the next state
        measurement = np.array(measurement).reshape(-1,1)

        self.update(measurement = measurement)
        self.predict()

        #reset undetected frames if needed
        self.total_undetected_frames=0

        #track is tracking an object, hence increment
        self.num_frames_tracked+=1


class ObjectTracker:
    def __init__(
        self,
        undetected_threshold:int = 20,
        tentative_track_threshold:int = 5,
        motion_threshold:float=13.28,
        colour_threshold:float = 0.4,
        save_tracks_threshold:int = 32,
        start_track_id:int=1,
        thumbnail_save_path:Path = Path("./assets/.db/thumbnail_images"),
        table_name:str = "test",
        db_name:str = "surveillance_project"
    ):
        #important thresholds, one for the threshold of when we proclaim a track to be prime for deletetion. (i.e. when it hasn't been detected, or rather
        #assigned a detected for UNDETECTED_THRESHOLD
        #the other threshold is for checking by how many frames we need to have detected a certain object, first for its track to be confirmed, or else for deletion
        self.UNDETECTED_THRESHOLD = undetected_threshold
        self.TENTATIVE_TRACK_THRESHOLD = tentative_track_threshold

        #Threshold for the motion given by squared mahalanobis distance by which if the cost is above this threshold, we refuse it
        self.MOTION_THRESHOLD = motion_threshold

        #threshold for the colour, by which if the colour_distance is above this threshold, we refuse it
        self.COLOUR_THRESHOLD = colour_threshold

        #threshold number for when tracks that have already been completed are going to be saved
        self.save_tracks_threshold = save_tracks_threshold

        # a big number to set as cost after we pre-gate
        #Also used to reject any assignments which are assigned to this cost
        self.INFINITY_VAL = 1e15

        self.object_tracks = list()

        #holds the object tracks which are going to be saved to a database after crossing the threshold (save_tracks_threshold)
        self.object_tracks_for_saving = list()
        self.curr_track_id = start_track_id

        #inference obj
        self.inference_obj = Inference(
            model_name = "squeezenet_1_1",
            npz_file_path = "./assets/model/pyt_classes.npz",
            weights_file = "./assets/model/pyt_squeezenet_model.pth"
        )

        self.table_name = table_name
        self.db_obj = Database(
            db_name = db_name,
            table_name = table_name
        )

        self.thumbnail_save_path = thumbnail_save_path/table_name
        self.thumbnail_save_path.mkdir(parents=True,exist_ok=True)


        #variable to keep track of how many objects have really been tracked (not including tentative ones)
        #simulating what would be stored in a 'database'
        self.valid_tracks_tracked = 0

    def track(
        self,
        detections:list[tuple],
        detected_bboxes:list[tuple],
        detected_colours_info:list,
        detected_shape_info:list,
        measurement_stds:float,
        orig_bboxes:list[tuple],
        delta_t:float=1,
        orig_frame:np.ndarray = None,
        working_frame:np.ndarray=None,
        frame_timestamp:float=0
    ):
        #where detections is a list of tuples containing the measurements, i.e. [(c_x,c_y,w,h),(c_x_1,c_y_1,w_1,h_1),...]
        #detected_bboxes is a list of tuples contatining the detections bbox co-ordinates [(x,x1,y,y1),(...),...]
        #detected_colours_info contains colour information for the detected objects
        #measurement_stds is a list of the std of the detector in giving the measurements 
        #delta_t is the time difference between measurements, given in frames 

        if len(self.object_tracks) == 0:
            self._initialise_new_object_tracks(
                orig_frame = orig_frame,
                detections = detections,
                detected_orig_bboxes = orig_bboxes,
                delta_t = delta_t,
                measurement_stds = measurement_stds,
                detected_objects_colour_info = detected_colours_info,
                detected_shape_info = detected_shape_info,
                track_start_timestamp = frame_timestamp,
            )
        else:
            #we have new detections, and we also have object_tracks that are already existing
            #get the cost matrix for detections to object_tracks, with pre-gated costs
            cost_matrix = self._get_cost_matrix(
                detections = detections,
                detected_colours_info = detected_colours_info
            )

            #returns:
            # assigned_idxs is a list containing tuple of (assigned_tracks_idxs,assigned_detection_idxs)
            # unassigned_tracks_idxs is a list containing the indexes of tracks not assigned
            # unassigned_detections is a list containing the indexes of the detections not assigned
            assigned_idxs,unassigned_tracks_idxs,unassigned_detections_idxs = self._assign_tracks_and_detections(
                cost_matrix = cost_matrix,
                object_track_idxs = set(range(len(self.object_tracks))),
                detection_idxs = set(range(len(detections)))
            )

            self._track_for_assigned_tracks(
                assigned_idxs = assigned_idxs,
                detections = detections,
                detected_bboxes = detected_bboxes,
                detected_orig_bboxes = orig_bboxes,
                detected_colours_info = detected_colours_info,
                detected_shape_info = detected_shape_info,
                track_timestamp = frame_timestamp,
                orig_frame = orig_frame
            )

            #TODO:Make better
            #we draw from here since the unassigned tracks function deletes from the list
            #which will reduce its size
            if working_frame is not None:
                self.visualise_tracked_ids(
                    working_frame,
                    object_tracks = [self.object_tracks[idx] for idx,_ in assigned_idxs]
                )

            #returns thos tracks that should be deleted.
            track_idxs_for_deletion = self._track_for_unassigned_tracks(unassigned_tracks_idxs)

            #unassigned_detections are new detections hence initialise them?
            self._initialise_new_object_tracks(
                orig_frame = orig_frame,
                detections = [detections[idx] for idx in unassigned_detections_idxs],
                detected_orig_bboxes = [orig_bboxes[idx] for idx in unassigned_detections_idxs],
                delta_t = delta_t,
                measurement_stds = measurement_stds,
                detected_objects_colour_info =[detected_colours_info[idx] for idx in unassigned_detections_idxs],
                detected_shape_info = [detected_shape_info[idx] for idx in unassigned_detections_idxs],
                track_start_timestamp = frame_timestamp
            )

            if len(self.object_tracks_for_saving) >= self.save_tracks_threshold:
                self.save_object_tracks()

            #TODO: Better way for deletion?
            #Finally delete the tracks that were marked for deletion
            tracks_for_deletion = [self.object_tracks[idx] for idx in track_idxs_for_deletion]
            for object_track in tracks_for_deletion:
                self.object_tracks.remove(object_track)

        return working_frame


    def save_object_tracks(self):
        print("Saving")
        thumbnail_images = list()

        if len(self.object_tracks_for_saving) == 0:
            return

        #first get the thumbnail image for each object track for classification
        for object_track in self.object_tracks_for_saving:
            thumbnail_images.append(object_track.get_thumbnail_image())

        #where predictions is a list whose elements are a tuple of (class_label,prob)
        start_time = time.perf_counter()

        #run classification
        predictions = self.inference_obj.predict(imgs = thumbnail_images,threshold=0.3)

        end_time = time.perf_counter()

        duration = end_time - start_time

        print(f"The Duration: {duration:.3f} Seconds")

        object_tracks_save_data = list()
        for object_track,(category,category_prob) in zip(self.object_tracks_for_saving,predictions):
            save_info = object_track.get_save_info()

            object_thumbnail_image = object_track.get_thumbnail_image()
            thumbnail_save_path = self.thumbnail_save_path/f"{uuid.uuid4().hex}.jpg"

            cv2.imwrite(thumbnail_save_path,object_thumbnail_image)

            #print("*"*50)
            #print("*"*50,"\n")

            save_info["category"] = category
            save_info["category_probability"] = category_prob
            save_info["thumbnail_image_path"] = str(thumbnail_save_path.absolute())

            #print("frames tracked:",save_info["total_frames_tracked"])
            #print(f"Category: {save_info['category']}, prob: {save_info['category_probability']:.3f}")
            #print(f"Thumbnail: {save_info['thumbnail_image_path']}")
            #print("colour_histogram:",save_info["colour_histogram"].shape)
            #print("shape_feature:",save_info["shape_feature"].shape)
            #print("start_timestamp:",save_info["start_timestamp"])
            #print("end_timestamp:",save_info["end_timestamp"])

            #print("\n"+"*"*50)
            #print("*"*50,"\n")

            object_tracks_save_data.append(save_info)

        #save to the database
        if len(object_tracks_save_data):
            self.db_obj.insert(
                table_name = self.table_name,
                insertion_data = object_tracks_save_data
            )

        #empty the list after saving
        self.object_tracks_for_saving = list()


    def visualise_tracked_ids(self,working_frame:np.ndarray,object_tracks:list):
        for track_obj in object_tracks:
            track_bbox = track_obj.get_bbox()
            track_id = track_obj.track_id

            if track_bbox is not None:
                #where top_x and top_y are the top_left (x,y) co-ordinates of the bbox
                top_x,top_y = track_bbox[0],track_bbox[2]
                cv2.putText(working_frame,str(track_id),(top_x,top_y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0))

    def count_valid_tracks(self):
        for track_obj in self.object_tracks:
            if track_obj.is_confirmed_track():
                self.valid_tracks_tracked+=1

    def get_total_tracks(self)->int:
        #Assumption is that this get_total_tracks function is called at the end of the video
        #hence we check of all the remaining tracks, how many are valid and we add them to the
        #total of the valid ones that were deleted before
        self.count_valid_tracks()
        return self.valid_tracks_tracked


    def _initialise_new_object_tracks(
        self,
        orig_frame,
        detections:list[tuple],
        detected_orig_bboxes:list[tuple],
        delta_t:float,
        measurement_stds:list,
        detected_objects_colour_info:list,
        detected_shape_info:list,
        track_start_timestamp: float
    ):
        #see track function for explanation of parameters
        zipped_things = zip(detections,detected_orig_bboxes,detected_objects_colour_info,detected_shape_info)
        for (c_x,c_y,w,h),(x,x_1,y,y_1),object_colour_hist,object_shape_info in zipped_things:

            track_obj = ObjectTrack(
                initial_measurements = {"initial_x":c_x,"initial_y":c_y,"initial_w":w,"initial_h":h},
                delta_t = delta_t,
                measurement_stds = measurement_stds,
                track_colour_hist = object_colour_hist,
                track_shape_feature = object_shape_info,
                track_id = self.curr_track_id,
                thumbnail_image = orig_frame[y:y_1,x:x_1],
                thumbnail_area = abs((x-x_1)*(y-y_1)),
                track_start_timestamp = track_start_timestamp
            )
            self.object_tracks.append(track_obj)

            self.curr_track_id+=1

    def _track_for_assigned_tracks(
        self,
        assigned_idxs:list,
        detections:list,
        detected_bboxes:list,
        detected_orig_bboxes:list,
        detected_colours_info:list,
        detected_shape_info:list,
        track_timestamp:float,
        orig_frame:np.ndarray
    ):
        #assigned_idxs is a list containing tuples of track_idx to detection_idx
        #detections is a list of all the detections
        #detected_bboxes is a list of all the bboxes
        #detected_colours_info is a list of all the colour info
        #detected_shape_info is a list of all the shape info
        #track_timestamp is the timestamp for when the detected objects were taken from the working_frame

        for t_idx,d_idx in assigned_idxs:
            track_obj = self.object_tracks[t_idx]
            measurement = detections[d_idx]

            track_obj.set_bbox(detected_bboxes[d_idx])
            x,x_1,y,y_1 = detected_orig_bboxes[d_idx]

            #TODO: Perhaps only update the colour info when we are very confident about the colour threshold
            track_obj.update_colour_info(detected_colours_info[d_idx])
            track_obj.update_shape_feature_info(detected_shape_info[d_idx])
            track_obj.update_thumbnail_image(
                thumbnail_image = orig_frame[y:y_1,x:x_1],
                thumbnail_area = abs((x-x_1)*(y-y_1))
            )
            track_obj.update_time(track_timestamp = track_timestamp)

            track_obj.update_predict(measurement = measurement)

            #mark tentative_tracks above threshold as confirmed
            if track_obj.is_tentative_track() and track_obj.get_total_tracked_frames() > self.TENTATIVE_TRACK_THRESHOLD:
                track_obj.set_confirmed()

    def _track_for_unassigned_tracks(self,unassigned_tracks_idxs:list)->list:
        #returns tracks to be deleted
        track_idxs_for_deletion = list()
        for track_idx in unassigned_tracks_idxs:
            track_obj = self.object_tracks[track_idx]
            track_obj.blind_predict()

            if track_obj.is_tentative_track() and track_obj.get_total_undetected_frames() >= self.TENTATIVE_TRACK_THRESHOLD:
                #delete track_obj that is tentative and past its threshold
                #self.object_tracks.pop(track_idx)
                #del self.object_tracks[track_idx]
                track_idxs_for_deletion.append(track_idx)
                continue

            if track_obj.get_total_undetected_frames() > self.UNDETECTED_THRESHOLD:
                #track_obj should be deleted, as it is possible it has gone out of frame
                #depending on what you are doing, this would be the point to save any objects that are above a certain detected threshold?
                #self.object_tracks.pop(track_idx)
                #del self.object_tracks[track_idx]
                track_idxs_for_deletion.append(track_idx)

                self.object_tracks_for_saving.append(track_obj)

                #this isn't a tentative track, meaning it had been successfully tracked before deletion
                self.valid_tracks_tracked+=1

        return track_idxs_for_deletion

    def _pre_gate_cost(self,cost:tuple)->float:
        #currently contains only the motion threshold, will be important once we apply
        #appearance and all that
        motion_cost = cost[0]
        colour_cost = cost[1]

        #we gate on both the motion_cost and colour_cost when available
        #then use the motion_cost to build the cost_matrix
        if motion_cost > self.MOTION_THRESHOLD:
            return self.INFINITY_VAL

        if colour_cost and colour_cost > self.COLOUR_THRESHOLD:
            return self.INFINITY_VAL

        return motion_cost

    def _get_cost_matrix(self,detections:list,detected_colours_info:list)->np.ndarray:
        #added pre-gating
        #TODO: Refactor to a better optimised way
        cost_matrix = list()

        for object_track in self.object_tracks:
            track_row_cost = list()

            for detection,colour_hist in zip(detections,detected_colours_info):
                cost = object_track.get_cost(detection,colour_hist)

                track_row_cost.append(self._pre_gate_cost(cost))

                #retired --> commented out for quick testing 
                #track_row_cost.append(cost)
                #print(object_track.get_cost(detection))

            cost_matrix.append(track_row_cost)

        return np.array(cost_matrix)

    #TODO: Refactor to use sets and indexes instead of the objects themselves??
    def _assign_tracks_and_detections(self,cost_matrix:np.ndarray,object_track_idxs:set,detection_idxs:set)->tuple[list[tuple],list,list]:
        #cost_matrix contains already gated costs
        #object_track_idxs is a set containing all the track idxs
        #detection_idxs is a set containing all the detection idxs
        #we return assigned_track_idxs and their detections
        #unassigned_track_idxs,detection_idxs

        tracks_idxs,detections_idxs = linear_sum_assignment(cost_matrix)

        matched_tracks_detections = [(i,j) for i,j in zip(tracks_idxs,detections_idxs) if cost_matrix[i][j] < self.INFINITY_VAL]

        assigned_tracks_idxs = set(track_idx for track_idx,_ in matched_tracks_detections)
        assigned_detections_idxs = set(detection_idx for _,detection_idx in matched_tracks_detections)

        #find the set difference between all_idxs and assigned ones to get the unassigned ones 
        unassigned_tracks_idxs = object_track_idxs - assigned_tracks_idxs
        unassigned_detections_idxs = detection_idxs - assigned_detections_idxs

        #assertion to ensure our short code above is fine and doing what we want
        assert len(matched_tracks_detections) + len(unassigned_tracks_idxs) == len(object_track_idxs)
        assert len(matched_tracks_detections) + len(unassigned_detections_idxs) == len(detection_idxs)

        return matched_tracks_detections,unassigned_tracks_idxs,unassigned_detections_idxs
