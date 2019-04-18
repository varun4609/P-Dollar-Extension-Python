from recognizer import PDollar, Template, Point

import xml.etree.ElementTree as ET
import errno
import glob
import random
import trial
import csv

'''
some_load

input: None
output: template list

Helper function used by the reading logic.
'''
def some_load():
    path = "dataset\\*\\*.xml"
    files = glob.glob(path)
    user_pool = []
    gesture_pool = []
    template_list = []

    print("Loading user pool and gesture types")

    for f in files:
        tree = ET.parse(f) 
        root = tree.getroot()
        gesture_type = root.attrib['Name'].split('~')[0]

        if gesture_type not in gesture_pool:
            gesture_pool.append(gesture_type)

        user = root.attrib['Subject']
        if user not in user_pool:
            user_pool.append(user)
    print("Done")

'''
load_templates

input: files
output: template list

Loads the templates once they are read.
'''
def load_templates(user, files):
    for f in files:
        tree = ET.parse(f) 
        # get root element 
        root = tree.getroot()
        gesture_type = root.attrib['Name'].split('~')[0]
        points = []
        strokeID = 1

        for item in root.findall('./Stroke'):
            # iterate child elements of item 
            for child in item:
                points.append(Point(int(child.attrib['X']), int(child.attrib['Y']), strokeID))
            strokeID += 1

        #print(gesture_type)
        template_list.append(Template(gesture_type, points)) 

    return template_list


'''
user_dependant

input: users, templates, gestures, # of gesture types
output: accuracy

Implements the random-100 algorithm for user-dependent testing.
'''
def user_dependant(user_pool, template_pool, gesture_pool, num_gestures_per_user):

    log_f = open('log_file.csv', 'wb')
    writer = csv.writer(log_f, delimiter = ',')
    writer.writerow(["Recognition Log: Varun Patni // $P // Navigation gestures // USER-DEPENDANT RANDOM-100"])
    writer.writerow(["User[all-users]", "GestureType[all-gestures-types]", "RandomIteration[1to100]",
         "#ofTrainingExamples[E]", "TotalSizeOfTrainingSet[count]", "TrainingSetContents[specific-gesture-instances]",
         "Candidate[specific-instance]", "RecoResultGestureType[what-was-recognized]", "CorrectIncorrect[1or0]",
         "RecoResultScore", "RecoResultBestMatch[specific-instance]", "RecoResultNBestSorted[instance-and-score]"])

    print("Starting testing...")
    for user in user_pool:
        score = 0.0
        count = 0.0
        # print("Loading templates for user " + user)
        # print("Done")

        for num_training_templates in range(1,4):
            
            for i in range(0, 100):
                training_set = []
                testing_set = []
                template_list = template_pool[user]

                # create training set
                index_str = []
                for g in gesture_pool:
                    tr_g_pool = []
                    tr_g_pool_index = []

                    for x in template_list:
                        if x.name == g: 
                            tr_g_pool.append(x)
                            tr_g_pool_index.append(template_list.index(x))
                    
                    for i in range(1, num_training_templates + 1):
                        temp = random.choice(tr_g_pool)
                        training_set.append(temp)
                        index_str.append(tr_g_pool_index[tr_g_pool.index(temp)])
                        tr_g_pool.remove(temp)
                

                tr_str = "{"
                count1 = 0
                for tr in training_set:
                    tr_str = tr_str + "p" + user + "-" + tr.name + "-" +  str((index_str[count1] % 100) % 10 if index_str[count1] >= 100 else index_str[count1] % 10) + ","
                    count1 += 1
                
                tr_str += "}"

                template_list = [x for x in template_list if x not in training_set]
               
                # create testing set
                test_index = []
                t1 = []
                for g in gesture_pool:
                    ts_g_pool = [x for x in template_list if x.name == g]
                    if len(ts_g_pool) == 0:
                        continue
                    for x in ts_g_pool:
                        test_index.append(template_pool[user].index(x))
                    temp = random.choice(ts_g_pool)
                    testing_set.append(temp)
                    t1.append(template_pool[user].index(temp))
                
                count1 = 0
                for test in testing_set:
                    count += 1
                    expected = test.name
                    rec = PDollar(training_set)
                    result = rec.recognize(test)

                    if (expected == result[0]):
                        score += 1

                    if result[0] == None:
                        continue

                    n_list = "{"
                    for res in result[3]:
                        n_list += 'p' + user + "-" + training_set[res[0]].name + "-" + str((index_str[result[2]]% 100) % 10 if index_str[result[2]] >= 100 else index_str[result[2]] % 10) + "," + str(res[1]) + ","
                    n_list += "}"

                    writer.writerow(['p'+user, test.name, i, num_training_templates, len(training_set), tr_str, 
                        "p" + user + "-" + test.name + "-" + str((t1[count1] % 100) % 10 if t1[count1] >= 100 else t1[count1] % 10),
                        result[0], 1 if (expected == result[0]) else 0, result[1], (index_str[result[2]]% 100) % 10 if index_str[result[2]] >= 100 else index_str[result[2]] % 10, n_list])
                    count1+=1
                
            accuracy = float(score/count)
            print("Accuracy: %.5f" % accuracy)
    log_f.close()

'''
main

input: None
output: None

Entry point for the testing fucntion
'''
def main():
    print("Loading data...")
    load_dict = trial.load_all()
    print("Done.")
    user_dependant(load_dict['user_pool'], load_dict['template_list'], load_dict['gesture_pool'], len(load_dict['gesture_pool']))

if __name__ == "__main__":
    main()
