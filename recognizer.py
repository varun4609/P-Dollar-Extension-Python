import os
import math
import errno

'''
class User

Purpose of this class is to map the input templates to
a particular user. It does this by storing the user ID
and the template in each instance object
'''   
class User:
    def __init__(self, number, template):
        self.number = number
        self.template = template


'''
class Point

Purpose of this class is to store the information about
a single point in the point cloud.
Each instance stores the x and y co-ordinates as well as
the strokeID of the stoke that the point belongs to.
'''
class Point:
    def __init__(self, x, y, stroke_id=None):
        self.x = x
        self.y = y
        self.stroke_id = stroke_id



'''
class User

Purpose of this class is to store a list of points that belong
to a particular point cloud along with the name of the template.
It stores the point list by invoking the __init__ method of the
list super class.
'''
class Template(list):
    def __init__(self, name, points):
        self.name = name
        super(Template, self).__init__(points)


'''
class User

This class contains all of the $P algorithm logic incuding the
pre-processing methods namely scale, resample, translate.
The constructor of this class takes a list of templates as 
input and stores them into its instance variable which is then
used for recognition.
'''
class PDollar:
    
    '''
    Constructor

    input: list of templates
    output: None

    Stores a list of templates in its instance variable self.templates.
    '''
    def __init__(self, templates):
        self.templates = templates

    '''
    Represent

    input: list of templates
    output: None

    Generates the N-best-list of recognition results.
    '''
    def _repr(self, templates):
        N_best_list = []
        N_best_list.sort(key=lambda tup: tup[1])
        if len(N_best_list) > 20:
            del N_best_list[-1]

    '''
    path_len

    input: list of points
    output: Length of path

    Returns total length of path from start point to end point following
    all the points in between
    '''
    def path_len(self, points):
        d = 0

        for i in range(1, len(points)):
            if points[i].stroke_id == points[i - 1].stroke_id:
                d += self.euclidean_distance(points[i - 1], points[i])
        return d
    
    '''
    greedy_five

    input: list of points, template, N
    output: minimum distance between the two point clouds

    Returns total length of path from start point to end point following
    all the points in between
    '''
    def greedy_five(self, points, template, n):
        e = 0.5
        step = int(math.floor(n ** (1 - e)))
        temp_min = float("inf")

        for i in range(0, n, step):
            d_1 = self.cloud_dist(points, template, n, i)
            d_2 = self.cloud_dist(template, points, n, i)
            temp_min = min(temp_min, d_1, d_2)
            #print (temp_min)
        return temp_min

    '''
    euclidean_distance

    input: two points
    output: euclidean distance

    Returns total euclidean distance between the two points
    '''
    def euclidean_distance(self, point_1, point_2):
        return math.hypot(point_1.x - point_2.x,
                          point_1.y - point_2.y)

    '''
    recognize

    input: candidate, N(default value 32)
    output: template with minimum distance score

    With the help of pre-processing function, it calculates the template
    with minimum score.
    '''
    def recognize(self, points, n=32):

        N_best_list = []
        count = 0
        res_count = 0
        result = None
        points = self.normalize(points, n)
        score = float("inf")
        
        for template in self.templates:
            template = self.normalize(template, n)
            d = self.greedy_five(points, template, n)
            
            if score > d:
                score = d
                result = template
                res_count = count

            N_best_list.append((count, d))
            N_best_list.sort(key=lambda tup: tup[1])
            if len(N_best_list) > 20:
                del N_best_list[-1]

            count += 1
        #score = max((math.ceil(score) - score), 0)
        if result is None or score == 0:
            return None, score
        return result.name, score, res_count, N_best_list

    
    '''
    cloud_dist

    input: points, templare
    output: total distance

    Returns the total distance between two point clouds
    '''
    def cloud_dist(self, points, template, n, start):
        matched = [False] * n
        ret_val = 0
        i = start

        while True:
            temp_min = float("inf")
            index = None
            for j in [x for x, b in enumerate(matched) if not b]:
                d = self.euclidean_distance(points[i], template[j])
                if d < temp_min:
                    temp_min = d
                    index = j
            matched[index] = True
            weight = 1 - ((i - start + n) % n) / n
            ret_val += weight * temp_min
            i = (i + 1) % n
            if i == start:
                break
        return ret_val

    '''
    normalize

    input: point cloud
    output: normalized point cloud

    Performs pre-processing functions and returns the new
    point cloud
    '''
    def normalize(self, points, n):
        points = self.resample(points, n)
        points = self.scale(points)
        points = self.translate(points, n)
        return points


    '''
    translate

    input: point cloud
    output: translated point cloud

    Translates point cloud to (0,0)
    '''
    def translate(self, points, n):
        if isinstance(points, Template):
            new_points = Template(points.name, [])
        else:
            new_points = []

        x = 0
        y = 0
        for p in points:
            x += p.x
            y += p.y
        x /= n
        y /= n

        for p in points:
            q = Point((p.x - x),
                      (p.y - y),
                      p.stroke_id)
            new_points.append(q)
        return new_points

    def resample(self, points, n):
        I = self.path_len(points) / (n - 1)
        D = 0
        if isinstance(points, Template):
            new_points = Template(points.name, [points[0]])
        else:
            new_points = [points[0]]

        i = 1
        while True:
            if points[i].stroke_id == points[i - 1].stroke_id:
                d = self.euclidean_distance(points[i - 1], points[i])
                if D + d >= I:
                    q = Point(points[i - 1].x + ((I - D) / d) * (points[i].x - points[i - 1].x),
                              points[i - 1].y + ((I - D) / d) * (points[i].y - points[i - 1].y))
                    q.stroke_id = points[i].stroke_id
                    new_points.append(q)
                    points.insert(i, q)
                    D = 0
                else:
                    D += d
            i += 1
            if i == len(points):
                break
        if len(new_points) == n - 1:
            p = points[-1]
            new_points.append(Point(p.x, p.y, p.stroke_id))
        return new_points

    

    '''
    scale

    input: point cloud
    output: scaled point cloud

    Scales the input point cloud to a pre decided scaling value
    '''
    def scale(self, points):
        x_min = float("inf")
        x_max = 0
        y_min = float("inf")
        y_max = 0

        if isinstance(points, Template):
            new_points = Template(points.name, [])
        else:
            new_points = []

        for p in points:
            x_min = min(x_min, p.x)
            x_max = max(x_max, p.x)
            y_min = min(y_min, p.y)
            y_max = max(y_max, p.y)
        scale = max(x_max - x_min, y_max - y_min)

        for p in points:
            q = Point((p.x - x_min) / scale,
                      (p.y - y_min) / scale,
                      p.stroke_id)
            new_points.append(q)
        return new_points