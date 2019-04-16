from recognizer import PDollar, Template, Point
import xml.etree.ElementTree as ET
import errno
import glob
import pickle
import os

path = "dataset\\*\\*.xml"
files = glob.glob(path)
exists = os.path.isfile('data.p')
exists_exe = os.path.isfile('exe_data.p')

dict_data = {
    'user_pool': [],
    'gesture_pool': [],
    'template_list': {}
}

dict_data_exe = {
    'user_pool': [],
    'gesture_pool': [],
    'template_list_exe': []
}

'''
load_all

input: None
output: template list

Reads data from the xml files.
'''
def load_all():
    print("Loading files...")
    if exists:
        f = open('data.p', 'r')
        loaded_dict = pickle.load(f)
        f.close()
        return loaded_dict

    for f in files:
        tree = ET.parse(f) 
        # get root element 
        root = tree.getroot()
        gesture_type = root.attrib['Name'].split('~')[0]
        user = root.attrib['Subject']

        if user not in dict_data['user_pool']:
            dict_data['user_pool'].append(user)
            dict_data['template_list'][user] = []

        if gesture_type not in dict_data['gesture_pool']:
            dict_data['gesture_pool'].append(gesture_type)
        points = []

        strokeID = 1

        for item in root.findall('./Stroke'):
            # iterate child elements of item 
            for child in item:
                points.append(Point(int(child.attrib['X']), int(child.attrib['Y']), strokeID))
            strokeID += 1

        dict_data['template_list'][user].append(Template(gesture_type, points))


    if(len(dict_data['template_list']) > 0): print("Loading success.")

    f = open('data.p', 'w')
    pickle.dump(dict_data, f)
    f.close()
    return dict_data

'''
load_all

input: None
output: template list

Reads data from the xml files for the demo application.
'''
def load_for_exe():

    print("Loading files...")

    path = "dataset\\*\\*.xml"
    files = glob.glob(path)

    for f in files:
        tree = ET.parse(f) 
        # get root element 
        root = tree.getroot()
        gesture_type = root.attrib['Name'].split('~')[0]
        user = root.attrib['Subject']

        if user not in dict_data_exe['user_pool']:
            dict_data_exe['user_pool'].append(user)
            # dict_data_exe['template_list_exe'][user] = []

        if gesture_type not in dict_data_exe['gesture_pool']:
            dict_data_exe['gesture_pool'].append(gesture_type)
        points = []

        strokeID = 1

        for item in root.findall('./Stroke'):
            # iterate child elements of item 
            for child in item:
                points.append(Point(int(child.attrib['X']), int(child.attrib['Y']), strokeID))
            strokeID += 1

        dict_data_exe['template_list_exe'].append(Template(gesture_type, points))


    if(len(dict_data_exe['template_list_exe']) > 0): print("Loading success.")

    return dict_data_exe