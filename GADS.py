
class Cluster:
    """
    holds courses
    """
    def __init__(self, id, courses):
        self.id = id
        self.courses = courses

    def __repr__(self):
        return "\nID: %s,\nCourses: %s" % (self.id, self.courses)


class Course:
    """
    just holds course groups or other courses
    """
    def __init__(self, id, name, kitas):
        self.id= id
        self.name = name
        self.groups=[]
        self.kitas=kitas
        g_id =0
        lects = parcts = labs = qandas = 0
        i=0
        for kita in kitas:
            #print("KITA:  " + str(kita.related_groups))
            #print("KITA type:  " + str(type(kita.related_groups)))
            if kita.related_groups!=None:
                # create group
                g_id+=1
                group = Course_Group(self.id,self.name,g_id,kita.related_groups)
                #print(kita.related_groups)
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

            if group_count ==0:
                #not in any group, create its own group
                g_id += 1
                group = Course_Group(self.id,self.name,g_id,[str(kita.g_number)])
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
            #print (len(group.lectures))
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

    def __repr__(self):
        return "\nCourse ID: %s,\nCourse Name: %s,\nkita: %s\n\n\n\n\n\n" \
               % (self.id, self.name, self.kitas)


class Course_Group():
    """
    holds lectures, practices, q&as, labs...
    """
    def __init__(self,id,name,g_id,related_courses):
        self.name=name
        self.id = id
        self.g_id=g_id
        self.related_courses=related_courses
        # better with dictoanry
        self.lectures = []
        self.practices = []
        self.q_and_as = []
        self.labs = []

    def __repr__(self):
        return "\nCourse ID: %s,\nCourse Name: %s,\nkita: %s, \nrelated courses: %s" \
               % (self.name, self.id, self.g_id, self.related_courses)

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
        self.lecturer = ""

        self.lectures = lectures
        if len(self.lectures)>0:
            self.lecturer = self.lectures[0].lecturer
        self.c_id=c_id

    def __repr__(self):
        return "\nClass type: %s,\ngroup number: %s,\nrelated groups: %s,\nlectures: %s,\nc id: %s" \
               % (self.type, self.g_number, self.related_groups, self.lectures, self.c_id)


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

    def __repr__(self):
        return "\nsemester: %s,\nday_in_week: %s,\nstart_time: %s,\nend_time: %s,\nlecturer: %s,\nlocation: %s\n" \
               % (self.semester, self.day_in_week, self.start_time, self.end_time, self.lecturer, self.location)