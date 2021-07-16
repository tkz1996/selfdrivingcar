import numpy as np



def get_direction(ROI, resolution, vectors):
    if vectors is None:
        return None

    x_points = []
    xc, yc = resolution[1]//2, resolution[0]*(ROI)
    #Finding the x-pixel position for every y-pixel position yc for all vectors
    for line in vectors:
        x1,y1,x2,y2 = line[0]
        y = y2 - y1
        if y == 0:
            continue
        m = (x2-x1)/(y)
        c = x1 - m*y1
        x_points.append(c)
    
    if len(x_points) == 0:
        return None
    total_angle = 0 #In radians
    for x in x_points:
        total_angle += np.arctan((x-xc)/(2*yc))
    
    return int(total_angle/len(x_points)*180/np.pi)
