from GADS import Course,Course_Group,Kita,Lect,Cluster
import GADS
import load_courses
from prettytable import PrettyTable
import random
import datetime
import Utils
from AbsGAClasses import Solution
from TableObjective import TableObjective


class TableSolution(Solution):
    """
    represents an individual in the genetic algorithm
    this representation follows the rules we set in our book
    a solution need to have the ability to crossover with another solution, to mutate, and to calculate fitness
    """
    # static variable for the solution structure
    structure = []

    def __init__(self,lectures=False):
        """
        create a empty solution
        """
        # arrange the courses in a more easy to work with way

        if lectures!=False:
            self.lectures = lectures
            return
        self.lectures=[]
        for item in TableSolution.structure:
            if type(item) == GADS.Course:
                for group in item.groups:
                    self.arrange_course_group(group)
                    for kita_type in group.lect_dict.keys():
                        for kita in group.lect_dict[kita_type]:
                            kita.c_id=kita.c_id.strip()
                            for lect in kita.lectures:
                                if type(lect.start_time) == str:
                                    lect.start_time = datetime.datetime.strptime(lect.start_time[1:], '%H:%M').time()
                                if type(lect.end_time) == str:
                                    lect.end_time = datetime.datetime.strptime(lect.end_time[1:], '%H:%M').time()
                                if type(lect.day_in_week)== str:
                                    lect.day_in_week = ord(lect.day_in_week[1]) - ord('א')
            else:
                for course in item.courses:
                    for group in course.groups:
                        self.arrange_course_group(group)
                        for kita_type in group.lect_dict.keys():
                            for kita in group.lect_dict[kita_type]:
                                kita.c_id = kita.c_id.strip()
                                for lect in kita.lectures:
                                    if type(lect.start_time) == str:
                                        lect.start_time = datetime.datetime.strptime(lect.start_time[1:],
                                                                                     '%H:%M').time()
                                    if type(lect.end_time) == str:
                                        lect.end_time = datetime.datetime.strptime(lect.end_time[1:], '%H:%M').time()
                                    if type(lect.day_in_week) == str:
                                        lect.day_in_week = ord(lect.day_in_week[1]) - ord('א')

        for item in TableSolution.structure:
            if type(item) == GADS.Course:
                self.pick_courase(item,False)
            # else its a cluster
            else:
                self.pick_cluster(item)

    def arrange_course_group(self,group):
        """
        change kita lectures structer to be a dict
        """
        group.lect_dict = {}
        lects = []
        for lect in group.lectures:
            lect.type= 'lecture'
            lects.append(lect)
        group.lect_dict['lecture'] = lects
        parcts = []
        for parc in group.practices:
            parc.type = 'practice'
            parcts.append(parc)
        group.lect_dict['practice'] = parcts
        q_and_as = []
        for q in group.q_and_as:
            q.type = 'q_and_a'
            q_and_as.append(q)
        group.lect_dict['q_and_a'] = q_and_as
        labs = []
        for lab in group.labs:
            lab.type = 'lab'
            labs.append(lab)
        group.lect_dict['lab'] = labs


    def lect_otigins(self,lect):
        if lect.cluster == False:
            cluster = False
            for item in TableSolution.structure:
                if type(item) == GADS.Course:
                    if item.id==lect.course:
                        course = item
        else:
            for item in TableSolution.structure:
                if type(item) == GADS.Cluster:
                    if item.id == lect.cluster:
                        cluster = item
            for c in cluster.courses:
                if c.id==lect.course:
                    course = c
        for g in course.groups:
            if lect in g.lect_dict[lect.type]:
                group = g
        return (group,course,cluster)

    def mutation(self):
        lect = random.choice(self.lectures)
        # 1 = kita 2 = group 3 = course
        choise_array = [1,2,3]
        group, course, cluster = self.lect_otigins(lect)

        new_lect = lect
        while len (choise_array)>0:
            choise = random.choice(choise_array)
            # kita
            if choise == 1:
                if len(group.lect_dict[lect.type])>1:
                    new_lect = random.choice(group.lect_dict[lect.type])
                    new_lect.group = group.g_id
                    new_lect.course = course.id
                    new_lect.cluster = cluster
                    if cluster != False:
                        new_lect.cluster = cluster.id
                    # actually replace lecture
                    for n, i in enumerate(self.lectures):
                        if i == lect:
                            self.lectures[n] = new_lect
                            return

                else:
                    choise_array.remove(1)
                    continue
            if choise == 2:
                if len(course.groups) >1:
                    new_group = random.choice(course.groups)
                    for n, i in enumerate(self.lectures):
                        if i.course == lect.course and i.cluster == lect.cluster and i.group == lect.group:
                            new_lect = random.choice(new_group.lect_dict[i.type])
                            new_lect.group = new_group.g_id
                            new_lect.course = course.id
                            new_lect.cluster = cluster
                            if cluster != False:
                                new_lect.cluster = cluster.id
                            for n, i in enumerate(self.lectures):
                                if i == lect:
                                    self.lectures[n] = new_lect
                                    return
                else:
                    choise_array.remove(2)
                    continue

            if choise == 3:
                if cluster != False and len(cluster.courses)>1:
                    to_remove = []
                    for n, i in enumerate(self.lectures):
                        if i.course == lect.course and i.cluster == lect.cluster and i.group == lect.group:
                            to_remove.append(n)
                    first_index = to_remove[0]
                    for n in to_remove:
                        self.lectures.pop(first_index)


                    new_course = random.choice(cluster.courses)
                    new_group = random.choice(new_course.groups)
                    for type in new_group.lect_dict.keys():
                        if len(new_group.lect_dict[type])>0:
                            new_lect = random.choice(new_group.lect_dict[type])
                            new_lect.group = new_group.g_id
                            new_lect.course = new_course.id
                            new_lect.cluster = cluster.id
                            self.lectures.insert(first_index,new_lect)
                            first_index+=1
                    return

                else:
                    choise_array.remove(3)
                    continue

    @staticmethod
    def cross_over(first_solution,second_solution):
        """
        cross over by grouping into course of clusteer groups, and by random deciding at what level to cross
        (kita/group/course)
        :param first_solution:
        :param second_solution:
        :return:
        """
        new_solution_lects=[]
        for lesson in first_solution.lectures:
            lesson.checked_one = False
        for lesson in second_solution.lectures:
            lesson.checked_two = False


        for lesson in first_solution.lectures:
            if lesson.checked_one == True:
                continue
            # create 2 lists of related lectures in both solutions
            group,course,cluster = first_solution.lect_otigins(lesson)
            first_list= []
            seconf_list = []
            choise_array=[1,2]

            change_level = 0
            #        (kita/group/course)
            if lesson.cluster != False:
                for lect in first_solution.lectures:
                   if lect.checked_one == False and lesson.cluster == lect.cluster:
                        lect.checked_one = True
                        first_list.append(lect)
                for lect in second_solution.lectures:
                   if lect.checked_two == False and lesson.cluster == lect.cluster:
                        lect.checked_two = True
                        seconf_list.append(lect)
            else:
                for lect in first_solution.lectures:
                    if lect.cluster == False and lect.course == lesson.course:
                        lect.checked_one = True

                        first_list.append(lect)
                for lect in second_solution.lectures:
                    if lect.cluster == False and lect.course == lesson.course:
                        lect.checked_two = True
                        seconf_list.append(lect)

            if len(first_list)>0:
                if first_list[0].course == seconf_list[0].course:
                    same_group = True
                    for l in seconf_list:
                        if l not in group.lect_dict[l.type]:
                            same_group = False
                    if same_group:
                        change_level=1
                    else:
                        change_level=2
                else:
                    change_level=3

                if change_level == 0:
                    print ('wtf')
                    exit(840)
                # kita change
                if change_level == 1:
                    for n, i in enumerate(first_list):
                        choise = random.choice(choise_array)
                        if choise == 1:
                            new_lect = i
                            new_solution_lects.append(new_lect)
                        else:
                            for lect in seconf_list:
                                if lect.type == i.type:
                                    new_lect = lect
                                    new_solution_lects.append(new_lect)
                # group change or cluster change
                if change_level == 2 or change_level == 3:
                    choise = random.choice(choise_array)
                    if choise == 1:
                        for lect in first_list:
                            new_lect = lect
                            new_solution_lects.append(new_lect)
                    else:
                        for lect in seconf_list:
                            new_lect = lect
                            new_solution_lects.append(new_lect)
        return TableSolution(lectures = new_solution_lects)


    def pick_courase(self,item,cluster):
        """
        pick by random group and and lectures for each type of lecture
        3 attributes are added to Kita's attributes:
        1. group - the group id
        2. course - the course id
        3. cluster - the cluster id
        :param item: course
        """
        if (len(item.groups)<1):
            return
        group = random.choice(item.groups)
        if len(group.lectures)>0:
            lect = random.choice(group.lectures)
            lect.group = group.g_id
            lect.course = item.id
            lect.cluster = cluster
            self.lectures.append(lect)
        if len(group.practices)>0:
            lect = random.choice(group.practices)
            lect.group = group.g_id
            lect.course = item.id
            lect.cluster = cluster
            self.lectures.append(lect)
        if len(group.q_and_as)>0:
            lect = random.choice(group.q_and_as)
            lect.group = group.g_id
            lect.course = item.id
            lect.cluster = cluster
            self.lectures.append(lect)
        if len (group.labs)>0:
            lect = random.choice(group.labs)
            lect.group = group.g_id
            lect.course = item.id
            lect.cluster = cluster
            self.lectures.append(lect)
    def pick_cluster(self,cluster):
        course = random.choice(cluster.courses)
        self.pick_courase(course,cluster.id)

    def string_table(self):
        """
        just for testing an option to print the table as a pretty table
        :return:
        """
        t = PrettyTable(['e', 'd', 'c', 'b', 'a','day' ])
        # create rows:
        for i in range(0,12):
            row_hour=i+8
            start_min = 30
            end_min = 30
            if row_hour == 11:
                start_min = 30
                end_min = 20
            if row_hour >= 12:
                start_min = 50
                end_min = 50
            row_start = datetime.datetime.strptime(str(row_hour) + ':' +str(start_min), '%H:%M').time()
            row_end = datetime.datetime.strptime(str(row_hour + 1)+ ':' +str(end_min), '%H:%M').time()
            row=['','','','','',str(row_start) + '-' + str(row_end)]
            for kita in self.lectures:
                for lect in kita.lectures:
                    if lect.start_time <= row_start and lect.end_time >= row_end:
                        row[4-lect.day_in_week] = row[4-lect.day_in_week] + kita.c_id + ' ' + kita.type +' '+lect.location +' '+ str(kita.cluster) + ' ' +str(lect.start_time) +' '+str(lect.end_time) + ' -- '
            t.add_row(row)
        return(str(t))

    def ecxel_table(self,row,worksheet):
        for i in range(0, 12):
            row_hour = i + 8
            start_min = 30
            end_min = 30
            if row_hour == 11:
                start_min = 30
                end_min = 20
            if row_hour >= 12:
                start_min = 50
                end_min = 50
            row_start = datetime.datetime.strptime(str(row_hour) + ':' + str(start_min), '%H:%M').time()
            row_end = datetime.datetime.strptime(str(row_hour + 1) + ':' + str(end_min), '%H:%M').time()
            for kita in self.lectures:
                for day in range(0,5):
                    msg = ''
                    for lect in kita.lectures:
                        if lect.start_time <= row_start and lect.end_time >= row_end and day == lect.day_in_week:
                            msg = msg +( kita.c_id + ' ' + kita.type +' '+lect.location +' '+ str(kita.cluster) + ' ' +str(lect.start_time) +' '+str(lect.end_time) + ' -- ')
                    worksheet.write(row+i,4-day,msg)

if __name__== "__main__":
    # activation via command line is a possibility

    args = Utils.parse_args()
    TableObjective.specific_windows = args.specific_windows
    TableObjective.specific_free_days = args.specific_days_off
    TableObjective.lecturers = args.lecturer
    courses,clusters = load_courses.Classes().run(args)
    structure = courses + clusters
    print (structure)
    TableSolution.structure=structure
    s = TableSolution()
    s.string_table()
    print ('score = '+ str(s.objective.evaluation()))
    b = TableSolution()
    b.string_table()
    print('score = ' + str(b.objective.evaluation()))
    baby = TableSolution()
    baby.string_table()
    print('score = ' + str(baby.objective.evaluation()))
    baby_two = TableSolution()
    baby_two.string_table()
    print('score = ' + str(baby_two.objective.evaluation()))
    baby_two.mutation()
    baby_two.string_table()
    TableSolution.cross_over(baby, baby_two).string_table()

