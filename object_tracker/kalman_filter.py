import numpy as np

class KalmanFilter:
    def __init__(
        self,*,
        observation_matrix:np.ndarray,
        initial_state:np.ndarray,
        state_transition_matrix:np.ndarray,
        estimate_covariance_matrix:np.ndarray,
        measurement_covariance_matrix:np.ndarray,
        process_noise_matrix:np.ndarray=np.array(0)
    ):
        #initialisation of the matrices and initial state
        self.observation_matrix = observation_matrix
        self.state_transition_matrix = state_transition_matrix
        self.measurement_covariance_matrix = measurement_covariance_matrix
        self.process_noise_matrix = process_noise_matrix

        #initial state initialisation
        self.curr_state_estimate = initial_state
        self.curr_estimate_covariance_matrix = estimate_covariance_matrix

        #after the initial initialisation we do the prediction for the next state
        #self.predict()

    def predict(self):
        #we don't yet model for a control variable
        #state extrapolation equation 
        self.next_state_prediction = self.state_transition_matrix @ self.curr_state_estimate

        #covariance extrapolation equation
        self.next_estimate_covariance_prediction =\
            self.state_transition_matrix @ self.curr_estimate_covariance_matrix @ self.state_transition_matrix.T + self.process_noise_matrix

        return self.next_state_prediction


    def _calculate_kalman_gain(self,*,predicted_estimate_covariance:np.ndarray,measurement_noise:np.ndarray)->np.ndarray:
        #where predicted_estimate_covariance, is the covariance that was predicted would be for this time step from the previous time step
        #measurement noise is an array for the measurement covariance 
        #kalman gain, calculated as:
        # predicted_estimate_covariance @ observation_matrix.T @ np.linalg.inv(observation_matrix @ predicted_estimate_covariance @ observation_matrix.T + measurement_noise)
        #broken down below

        first_res = predicted_estimate_covariance @ self.observation_matrix.T
        second_res = np.linalg.inv(self.observation_matrix @ first_res + measurement_noise)

        return first_res @ second_res

    def _update_state(self,*,pred_state_estimate:np.ndarray,kalman_gain:np.ndarray,measurement:np.ndarray)->np.ndarray:
        #where pred_state_estimate, is the state_estimate that was predicted would be for this time step from the previous time step

        return pred_state_estimate + kalman_gain @ (measurement - self.observation_matrix @ pred_state_estimate)

    def _update_estimate_covariance(self,*,predicted_estimate_covariance:np.ndarray,kalman_gain:np.ndarray,measurement_noise:np.ndarray)->np.ndarray:
        #where predicted_estimate_covariance, is the covariance that was predicted would be for this time step from the previous time step
        #measurement noise is an array for the measurement covariance 
        #estimate covariance updated using the covariance update equation:
        # (identity_matrix - kalman_gain @ observation_matrix) @ predicted_estimate_covariance --> a simpler equation that isn't mathematically stable
        # simpler_equation @ (identity_matrix - kalman_gain @ observation_matrix).T + kalman_gain @ measurement_noise + kalman_gain.T
        #the second longer equation broken down below:

        temp_part_1 = np.eye(kalman_gain.shape[0]) - kalman_gain @ self.observation_matrix
        simpler_equation = temp_part_1 @ predicted_estimate_covariance

        temp_part_2 = simpler_equation @ temp_part_1.T

        return temp_part_2 + kalman_gain @ measurement_noise @ kalman_gain.T


    def update(self,measurement:np.ndarray)->np.ndarray:
        #for update, we first calculate the kalman gain, then update state and the estimate covariance

        #kalman gain
        kalman_gain = self._calculate_kalman_gain(
            predicted_estimate_covariance = self.next_estimate_covariance_prediction,
            measurement_noise = self.measurement_covariance_matrix
        )

        #state update
        self.curr_state_estimate = self._update_state(
            pred_state_estimate = self.next_state_prediction,
            kalman_gain = kalman_gain,
            measurement = measurement
        )

        #estimate covariance update
        self.curr_estimate_covariance_matrix = self._update_estimate_covariance(
            predicted_estimate_covariance = self.next_estimate_covariance_prediction,
            kalman_gain = kalman_gain,
            measurement_noise = self.measurement_covariance_matrix,
        )

        return self.curr_state_estimate,self.curr_estimate_covariance_matrix

