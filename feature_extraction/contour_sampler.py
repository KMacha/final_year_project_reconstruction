import cv2
import numpy as np

def euclidean(a,b):
    a = np.array(a)
    b = np.array(b)

    return np.sqrt(np.sum(np.square(a-b)))

def interpolate_new_point(new_point_distance:float,start_point:tuple|np.ndarray,end_point:tuple|np.ndarray,line_distance:float)->tuple[float,float]:
    #where:
    #new_point_distance is the distance we desire the new point to be from start_point
    #start_point is the start co-ordinate of the line and
    #end_point is the end co-ordinate of that line
    #line_distance: euclidean(start_point,end_point) or || end_point - start_point ||

    #convert them to arrays incase they are not arrays:
    start_point = np.array(start_point)
    end_point = np.array(end_point)

    #where unit vec represents by how much we move 1 unit from start_point heading towards end_point
    unit_vec = (end_point - start_point)/line_distance


    #with unit_vec, we can find by how much we should move from start_point to get to our new point using v0 + pd*unit_vec
    return start_point + new_point_distance * unit_vec

def sample_contour_points(contour_points:list|np.ndarray,total_samples:int=64):
    shape_perimeter = cv2.arcLength(contour_points,True)

    #where sample_distance is the arc length
    sample_distance = temp_sample_distance = shape_perimeter/total_samples

    sampled_points = [contour_points[0]]

    #the next contour_point is always the line_end_point
    line_start_point = contour_points[0]
    i = 1

    line_distance = euclidean(line_start_point,contour_points[i])

    n = len(contour_points)
    while len(sampled_points) < total_samples:
        #when distance between two points of the contour is great than our sample distance
        if line_distance > temp_sample_distance:
            new_point = interpolate_new_point(
                new_point_distance = temp_sample_distance,
                start_point = line_start_point,
                end_point = contour_points[i],
                line_distance = line_distance
            )
            sampled_points.append(new_point)

            #reduce distance by the temp_sample_distance, 
            #explanation: because distance was the distance of the whole line and the new point gotten is 
            #+temp_sample_distance away from the start_point of the line, hence we subtract temp_sample_distance from the line distance
            #and set the new line start_poit as the new point
            line_start_point = new_point
            line_distance-=temp_sample_distance

            #after getting a point, we reset the temp_sample_distance
            #as we want to find points that are sample_distance away from each other
            #we reset, because temp_sample_distance will be reduced in the other conditional blocks
            temp_sample_distance = sample_distance
        elif line_distance < temp_sample_distance:
            #explanation:
            #the line_distance is less than the distance for the point we want, hence
            #first subtract the line_distance from the temp_sample_distance, this is because we then
            #set, the line_end_point to be the line_start_point, hence we subtract line_distance from temp_sample_distance, because the new line_start_point
            #is acting like a waypoint to the point we need something like at the start the line was
            # l_s_p------l_e_p-----d_p, where l_s_p and l_e_p are line_start_point and end_point respectively, and d_p is the desired_point (sample_poit)
            temp_sample_distance-=line_distance
            line_start_point = contour_points[i]
            i = (i+1)%n

            line_distance = euclidean(line_start_point,contour_points[i])
        else:
            #when line_distance and the temp_sample_distance are equal, using a diagram like above it means
            # l_s_p--------[l_e_p|d_p] i.e. the line_end_point is exactly the sample_point we want
            #then the line_end_point becomes our new line_start_point, and we reset back the sample_distance
            sampled_points.append(contour_points[i])
            line_start_point = contour_points[i]
            i = (i+1)%n

            line_distance = euclidean(line_start_point,contour_points[i])

            #reset back the sample_distance
            temp_sample_distance = sample_distance


    #print(sampled_points)


    #print("sample distance:",sample_distance)

    return np.array(sampled_points)
