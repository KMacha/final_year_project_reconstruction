import numpy as np

#def get_kalman_filter_matrices(model_assumptions:dict,delta_t=1,acceleration_jerk=1e-9)->dict:
def get_kalman_filter_matrices(initial_measurements:dict,delta_t=1,measurement_stds:list=[3.0,3.0,5.0,5.0],process_noise_factor=0.9)->dict:
    #Modelling for constant velocity
    #state: [c_x,c_y,w,h,c_x_velocity,c_y_velocity]
    #state: [c_x,c_y,w,h,c_x_velocity,c_y_velocity,w_velocity,h_velocity]
    #measurements: [c_x,c_y,w,h] --> The measurements include only the centroid

    matrices = dict()

    matrices["observation_matrix"] = np.array([
        [1,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,0,0],
        [0,0,1,0,0,0,0,0],
        [0,0,0,1,0,0,0,0],
    ])

    #for the initial state, we give the correct values for time t=0
    matrices["initial_state"] = np.array(
        [
            initial_measurements["initial_x"],
            initial_measurements["initial_y"],
            initial_measurements["initial_w"],
            initial_measurements["initial_h"],
            0, #unknown velocity_x
            0, #unknown velocity_y
            0, #unknown width_velocity
            0, #unknown height_velocity
        ]
    ).reshape(-1,1)

    #for the state transition matrix 
    matrices["state_transition_matrix"] = np.array([
        [1,0,0,0,delta_t,0,0,0],
        [0,1,0,0,0,delta_t,0,0],
        [0,0,1,0,0,0,delta_t,0],
        [0,0,0,1,0,0,0,delta_t],
        [0,0,0,0,1,0,0,0],
        [0,0,0,0,0,1,0,0],
        [0,0,0,0,0,0,1,0],
        [0,0,0,0,0,0,0,1]
    ])

    #We initialise the filter with the first measurement,
    #the velocity is unknown hence a higher variance
    matrices["estimate_covariance_matrix"] = np.array([
        [measurement_stds[0]**2,0,0,0,0,0,0,0], #for x
        [0,measurement_stds[1]**2,0,0,0,0,0,0], #for y
        [0,0,measurement_stds[2]**2,0,0,0,0,0], #for w
        [0,0,0,measurement_stds[3]**2,0,0,0,0], #for h
        [0,0,0,0,500,0,0,0], #for vx
        [0,0,0,0,0,500,0,0], #for vy
        [0,0,0,0,0,0,500,0], #for vw
        [0,0,0,0,0,0,0,500], #for vh
    ])

    #we are modelling for a constant acceleration model, for now we make the assumption that the process model we have is correct
    #we use a relative low acceleration_jerk
    #we project the process noise using the state transition matrix 
    #ie. process_noise: Q = F @ Qa @ F.transpose()
    #where Qa, is a np.zeros matrix with 1s in the state that would induce noise, in our case it is the acceleration hence

    #it has a 1 in the cell tha correspond to acceleration of x, and also the cell corresponding to acceleration of y
    #and a 1 in the cells corresponding to acceleration for the width and height
    Qv_matrix = np.array([
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,1,0,0,0],
        [0,0,0,0,0,1,0,0],
        [0,0,0,0,0,0,1,0],
        [0,0,0,0,0,0,0,1]
    ])

    #we then use a low acceleration jerk, since this toy problem we have modelled isn't really noisy
    matrices["process_noise_matrix"] = (matrices["state_transition_matrix"] @ Qv_matrix @ matrices["state_transition_matrix"].T) * process_noise_factor
    #matrices["process_noise_matrix"] = np.array([0])


    return matrices
