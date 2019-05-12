
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import pickle
import json

#cant run without this:
chrome_driver_exe=r'C:\Users\ronma\GYGY\chromedriver'

course_number = '3'

# kita might have 2 lect for example hedva lecture has 2 lectures one on wednesday the other monday
# in case of 2 lectures , the lecturer is chosen by first lecturer in the lects (might not be good but lets not push it)
# in related groups one if one lect is in the other's related groups then thery are related (no need for vice versa)

class Course:
    """
    just holds course groups or other courses
    """
    def __init__(self, id, course_name, kitas):
        self.id= id
        self.course_name = course_name
        self.groups=[]
        g_id =0
        lects = parcts = labs = qandas = 0
        for kita in kitas:
            if kita.related_groups!=None:
                # create group
                g_id+=1
                group = Course_Group(self.id,self.course_name,g_id,kita.related_groups)
                print(kita.related_groups)
                self.groups.append(group)

        for kita in kitas:
            group_count = 0
            for group in self.groups:
                if kita.g_number.strip() in group.related_courses or any(kita.g_number.strip() in s for s in group.related_courses):
                    group_count+=1
                    if kita.type == 'תרגיל':
                        parcts+=1
                        group.practices.append(kita)
                    elif kita.type == 'הרצאה':
                        group.lectures.append(kita)
                        lects+=1
                    elif kita.type == 'מעבדה':
                        group.labs.append(kita)
                        labs+=1
                    elif kita.type == 'שו"ת':
                        group.q_and_as.append(kita)
                        qandas+=1
            print("Group count:::   " + str(group_count))
            if group_count ==0:
                #not in any group, create its own group
                g_id += 1
                group = Course_Group(self.id,self.course_name,g_id,[str(kita.g_number)])
                if kita.type == 'תרגיל':
                    group.practices.append(kita)
                    parcts += 1
                elif kita.type == 'הרצאה':
                    group.lectures.append(kita)
                    lects += 1
                elif kita.type == 'מעבדה':
                    group.labs.append(kita)
                    labs += 1
                elif kita.type == 'שו"ת':
                    group.q_and_as.append(kita)
                    qandas += 1
                self.groups.append(group)
        # delete invalid groups lects = parcts = labs = qandas
        for group in self.groups:
            print (len(group.lectures))
            if lects > 0 and len(group.lectures) == 0:
                self.groups.remove(group)
            elif parcts > 0 and len(group.practices) == 0:
                self.groups.remove(group)
            elif labs > 0 and len(group.labs) == 0:
                self.groups.remove(group)
            elif qandas > 0 and len(group.q_and_as) == 0:
                self.groups.remove(group)

        final_groups=[]
        for group in self.groups:
            add = True
            for new_group in final_groups:
                if group.related_courses == new_group.related_courses:
                    add = False
            if add:
                final_groups.append(group)
        self.groups=final_groups



class Course_Group():
    """
    holds lectures, practices, q&as, labs...
    """
    def __init__(self,id,name,g_id,related_courses):
        self.name=name
        self.id = id
        self.g_id=g_id
        self.related_courses=related_courses
        self.lectures = []
        self.practices = []
        self.q_and_as = []
        self.labs = []


class Kita:
    """
    holds lectures (might be more then one)
    """
    def __init__(self,type,g_number,related_groups,lectures,c_id):
        """
        :param type:
        :param g_number:
        :param related_groups:
        :param lectures:
        :param lecturer:
        """
        self.type=type
        self.g_number = g_number
        self.related_groups = related_groups
        self.lectures = lectures
        self.lecturer =""
        self.c_id=c_id


class Lect:
    """
    a pure simple lecture
    """
    def __init__(self,semester,day_in_week,start_time,end_time,lecturer,location):
        self.semester = semester
        self.day_in_week = day_in_week
        self.start_time=start_time
        self.end_time=end_time
        self.lecturer=lecturer
        self.location=location


def main():

    # load website
    browser = webdriver.Chrome(executable_path=chrome_driver_exe)
    for i in range(99999,9999999):
        course_number = str(i)
        print (i)
        browser.get('https://info.braude.ac.il/yedion/fireflyweb.aspx?prgname=Enter_Search')
        # Wait 20 seconds for page to load
        timeout = 20
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH,"// span[@class ='fa fa-print']")))
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()

        # find course
        inputElement = browser.find_element_by_id("SubjectCode")
        inputElement.send_keys(course_number)
        inputElement.send_keys(Keys.ENTER)
        browser.find_element_by_name("B2").click()
        # parse page of lectures
        #lectures = []
        source = str(browser.page_source)
        #course base parsing:
        course_name = None
        for line in source.split('\n'):
            if '<h1 style="text-align:center">' in line:
                course_name = line.split('<h1 style="text-align:center">')[1].split('</h1>')[0].replace('קורס','')
                course_name = course_name.strip()
            elif '<input type="button" name="B2" value="פרטים נוספים" class="btn-u  btn-u-light-green" onclick="SubmitForm' in line:
                id = line.split('"SubmitForm')
                id = id[1].split(',')[3].replace("'", '').replace('-N', '').strip()
        if course_name == None:
            continue
        #lectures pasring
        classes = source.split('<div style="text-align:right" class="text">')
        kitas =[]

        for kita in classes:
            related_groups = None
            splited = kita.split('\n')
            type = None
            for line in splited:
                if 'קורס מסוג ' in line:
                    type = line.split('קורס מסוג ')[1]

                elif 'קבוצה :' in line:
                    g_number = (line.split('קבוצה :')[1]).replace('</span>','').replace(' ','')

                elif '<b> <span style="color: green" class="text">' in line:
                    try:
                        related_groups=line.split('<b> <span style="color: green" class="text">')[1]\
                        .split('קבוצות הקשורות לקורס זה :')[1]\
                            .split('</span></b>')[0]
                        related_groups = related_groups.replace(' ','').replace(')','')
                        related_groups = related_groups.split(',')
                    except:
                        pass



            if type is not None:
                multy = kita.split('style="text-align:right" role="row"')
                lects=[]

                for lecture in multy:
                    if '</td>' in lecture and 'טבלה ריקה' not in lecture:
                        lecture=lecture.split(r'</td>')
                        semester = lecture[0].split(r'<td>')[1].replace(' ','')
                        day_in_week= lecture[1].split(r'<td>')[1].replace(' ','')
                        start = lecture[2].split(r'<td>')[1].replace(' ','')
                        end = lecture[3].split(r'<td>')[1].replace(' ','')
                        lecturer = lecture[4].split(r'<td>')[1]
                        location = lecture[5].split(r'<td>')[1].replace(' ','')

                        lect = Lect(semester,day_in_week,start,end,lecturer,location)
                        lects.append(lect)

                if len(lects) <1:
                    continue
                lecture = Kita(type,g_number,related_groups,lects,id)
                kitas.append(lecture)

        course = Course(id,course_name,kitas)

        groupssss=[]

        for group in course.groups:
            print('g = ' + str(group.lectures) + ' ' + str(group.practices) + ' ' + str(group.labs) + ' ' + str(
                group.q_and_as))
            lectures =[]
            practices=[]
            labs = []
            q_and_as = []
            for kita in group.lectures:
                lectsss =[]
                for lect in kita.lectures:
                    lectOBJArr = {
                        "Semester": lect.semester,
                        "Day": lect.day_in_week,
                        "Start time": lect.start_time,
                        "End time": lect.end_time,
                        "Lecturer name": lect.lecturer,
                        "Class location": lect.location
                    }
                    lectsss.append(lectOBJArr)
                kitaaaOBJArr = {
                    "Class type": lecture.type,
                    "group number": lecture.g_number,
                    "Related groups": lecture.related_groups,
                    "Lecture": lectsss,
                    "c ID": lecture.c_id,
                    "lecturer": lecture.lecturer
                }
                lectures.append(kitaaaOBJArr)


            for kita in group.practices:
                lectsss = []
                for lect in kita.lectures:
                    lectOBJArr = {
                        "Semester": lect.semester,
                        "Day": lect.day_in_week,
                        "Start time": lect.start_time,
                        "End time": lect.end_time,
                        "Lecturer name": lect.lecturer,
                        "Class location": lect.location
                    }
                    lectsss.append(lectOBJArr)
                kitaaaOBJArr = {
                    "Class type": lecture.type,
                    "group number": lecture.g_number,
                    "Related groups": lecture.related_groups,
                    "Lecture": lectsss,
                    "c ID": lecture.c_id,
                    "lecturer": lecture.lecturer
                }
                practices.append(kitaaaOBJArr)

            for kita in group.labs:
                kitaaa = {}
                lectsss = []
                for lect in kita.lectures:
                    lectOBJArr = {
                        "Semester": lect.semester,
                        "Day": lect.day_in_week,
                        "Start time": lect.start_time,
                        "End time": lect.end_time,
                        "Lecturer name": lect.lecturer,
                        "Class location": lect.location
                    }
                    lectsss.append(lectOBJArr)
                kitaaaOBJArr = {
                    "Class type": lecture.type,
                    "group number": lecture.g_number,
                    "Related groups": lecture.related_groups,
                    "Lecture": lectsss,
                    "c ID": lecture.c_id,
                    "lecturer": lecture.lecturer
                }
                labs.append(kitaaaOBJArr)



            for kita in group.q_and_as:
                lectsss = []
                for lect in kita.lectures:
                    lectOBJArr = {
                        "Semester": lect.semester,
                        "Day": lect.day_in_week,
                        "Start time": lect.start_time,
                        "End time": lect.end_time,
                        "Lecturer name": lect.lecturer,
                        "Class location": lect.location
                    }
                    lectsss.append(lectOBJArr)
                kitaaaOBJArr = {
                    "Class type": lecture.type,
                    "group number": lecture.g_number,
                    "Related groups": lecture.related_groups,
                    "Lecture": lectsss,
                    "c ID": lecture.c_id,
                    "lecturer": lecture.lecturer
                }
                q_and_as.append(kitaaaOBJArr)


            groupOBJ = {
                "name" : group.name,
                "id" : group.id,
                "g_id" : group.g_id,
                "related_courses" : group.related_courses,
                "lectures" : lectures,
                "practices" : practices,
                "q_and_as" : q_and_as,
                "labs" : labs
            }
            groupssss.append(groupOBJ)

        courseOBJ = {
            "Course ID": course.id,
            "Course Name": course.course_name,
            "groups": groupssss
        }

        #for group in course.groups:
            #print ('g = ' + str(group.lectures) + ' ' + str(group.practices)+ ' '+ str(group.labs) + ' ' + str(group.q_and_as))
        with open('all_courses_final.json', 'a', encoding='utf-8') as f:  # writing JSON object
            #json.dump(course, f, indent=4,)
            json.dump(course,f, indent=4, cls=CustomEncoder)
            #serialized = json.dumps(course, indent=4, cls=CustomEncoder)
            #deserialized = json.loads(serialized, object_hook=decode_object)
            #print ("HEYHEYHEY" + str(deserialized.groups[0].lectures[0].lectures[0].location))
            f.write(",")
        z=json.dumps(course, indent=4, cls=CustomEncoder)
        print("JSON STARTS HERE:||" + str(z) + "||JSON ENDS HERE")






    print('done')
    time.sleep(90)


class CustomEncoder(json.JSONEncoder): 
     def default(self, o):  # pylint: disable=E0202
         return {'__{}__'.format(o.__class__.__name__): o.__dict__}


def decode_object(o):
     
    if '__Course__' in o:
        a = Course( 0, "fifi", [])
        a.__dict__.update(o['__Course__'])
        return a
 
    elif '__Course_Group__' in o:
        a = Course_Group(0,"name",0,[])
        a.__dict__.update(o['__Course_Group__'])
        return a
    elif '__Kita__' in o:
        a = Kita("type",0,[],[],0)
        a.__dict__.update(o['__Kita__'])
        return a
    elif '__Lect__' in o:
        a = Lect("","","","","","")
        a.__dict__.update(o['__Lect__'])
        return a
    return o


if __name__ == '__main__':
    main()