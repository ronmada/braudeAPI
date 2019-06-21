import datetime
import Utils
from AbsGAClasses import Objective




class TableObjective(Objective):
    """
    allows us to calculate the objective of a solution, the constructor should be called by the solution
    the user inputs should be set as static attributes, the will be off by default.
    """

    max_objective=100
    specific_windows = False
    specific_free_days = False
    lecturers = False
    panelty_weight = 6
    free_days_weight = 4
    spesific_days_off_weight = 5
    specific_windows_weight = 2
    specific_lecturers_weight = 3

    def __init__(self,solution):
        self.solution = solution




    def evaluation(self):
        """
        :param solution:
        :param spesific_window: an array of tuples (day,period) - day 0-4, period - 0-12
        :return:
        """
        return (self.max_objective - ( (TableObjective.panelty_weight * self.Penalty() ) + self.fitness() ) )

    def Penalty(self,):
        return self.overlaps()

    def fitness(self,):
        fitness = 0
        fitness += self.windows()
        fitness += TableObjective.specific_windows_weight * self.spesific_window()
        fitness += TableObjective.free_days_weight * self.school_days()
        fitness += TableObjective.spesific_days_off_weight * self.specific_days_off()
        fitness += TableObjective.specific_lecturers_weight * self.specific_lecturers()
        fitness += self.classroom_proximity()
        return fitness

    def windows(self):
        """
        return the amount of windows
        """
        windows = 0
        for day in range(0,5):
            lects_in_day=[]
            for kita in self.solution.lectures:
                for lect in kita.lectures:
                    if lect.day_in_week == day:
                        lects_in_day.append(lect)

            lects_in_day = sorted(lects_in_day, key=lambda x: x.end_time, reverse=False)
            if len(lects_in_day)>1:
                hour = lects_in_day[0].end_time
                last_hour = lects_in_day[len(lects_in_day)-1].start_time
                while (hour < last_hour):
                    start_min = 30
                    end_min = 30
                    if hour.hour == 11:
                        start_min = 30
                        end_min = 20
                    if hour.hour >= 12:
                        start_min = 50
                        end_min = 50
                    start = datetime.datetime.strptime(str(hour.hour) + ':' + str(start_min), '%H:%M').time()
                    end = datetime.datetime.strptime(str(hour.hour + 1) + ':' + str(end_min), '%H:%M').time()
                    empty = True
                    for lect in lects_in_day:
                        if lect.start_time <= start and lect.end_time >= end:
                            empty = False
                    if empty:
                        windows +=1
                    hour = (datetime.datetime.combine(datetime.date(1,1,1),hour)+ datetime.timedelta(hours=1)).time()
        self.table_windows = windows
        return (windows)

    def spesific_window(self):
        """
        reeturn the amount of specific windows that were violated
        """
        spesific_window_desecrated = 0
        if self.specific_windows:
            new_list = []
            #parse from string to tuple
            for item in TableObjective.specific_windows:
                if type(item)==str:
                    new_list.append(Utils.string_to_int_tuple(item))
                else:
                    new_list.append(item)
            specific_windows = new_list
            for day,period in specific_windows:
                day = int(day)
                period = int(period)
                hour = period + 8
                start_min = 30
                end_min = 30
                if hour == 11:
                    start_min = 30
                    end_min = 20
                if hour >= 12:
                    start_min = 50
                    end_min = 50
                window_start = datetime.datetime.strptime(str(hour) + ':' + str(start_min), '%H:%M').time()
                window_end = datetime.datetime.strptime(str(hour + 1) + ':' + str(end_min), '%H:%M').time()
                desecrated = False
                for kita in self.solution.lectures:
                    for lect in kita.lectures:
                        if lect.day_in_week == day:
                            if lect.start_time <= window_start and lect.end_time >= window_end:
                                desecrated = True
                if desecrated:
                    spesific_window_desecrated+=1

        self.spesific_window_desecrated = spesific_window_desecrated
        return spesific_window_desecrated



    def overlaps(self):
        """
        return the amount of *lects* that overlap each other,
        important to note that its not per hour of overlaps but lectures
        """
        overlaps = 0
        for kita_one in self.solution.lectures:
            for lect in kita_one.lectures:
                for kita_two in self.solution.lectures:
                    for lect_two in kita_two.lectures:
                        if lect.day_in_week == lect_two.day_in_week:
                            if lect.start_time <= lect_two.start_time and lect.end_time > lect_two.start_time:
                                overlaps += 1
                            elif lect.start_time >= lect_two.start_time and lect.start_time < lect_two.end_time:
                                overlaps += 1
        overlaps = int((overlaps - len(self.solution.lectures))/2)
        self.overlaps_number = overlaps
        return overlaps


    def school_days(self):
        """
        return the amount of days that has classes in them
        """
        school_days = 0
        for day in range(0,5):
            empty = True
            for kita in self.solution.lectures:
                for lect in kita.lectures:
                    if lect.day_in_week == day:
                        empty = False
            if not empty:
                school_days+=1

        self.numer_of_school_days = school_days
        return school_days

    def specific_days_off(self):
        """
        return the amount of free days that were violated
        """
        days_violated = 0
        if TableObjective.specific_free_days:
            for day in TableObjective.specific_free_days:
                day = int(day)
                violated = False
                for kita in self.solution.lectures:
                    for lect in kita.lectures:
                        if lect.day_in_week == day:
                            violated = True
                if violated:
                    days_violated+=1
        self.days_violated = days_violated
        return days_violated

    def specific_lecturers(self):
        score =0
        lecturer_perfs =[]
        if TableObjective.lecturers:
            for item in TableObjective.lecturers:
                lecturer_perfs.append(Utils.string_to_int_tuple(item))
            for t in lecturer_perfs:
                c_id,c_type,name=t
                print ('ahahahahahahhahah : ' + str(c_id)+'|||'+ str(c_type)+'|||'+str(name))
                for lesson in self.solution.lectures:
                    if c_id.strip() == lesson.c_id.strip() and c_type.strip() == lesson.type.strip():
                        if len(name.split(' ')) >= 3:

                            if name.split(' ')[1] != lesson.lecturer.split(' ')[1] and name.split(' ')[2] != lesson.lecturer.split(' ')[2]:
                                score += 1
                        elif name.strip() != lesson.lecturer.strip():
                            score+=1
        self.specific_lecturers_violated = score
        return score


    def classroom_proximity(self):
        far_classes = 0

        for day in range(0,5):
            lects_in_day=[]
            for kita in self.solution.lectures:
                for lect in kita.lectures:
                    if lect.day_in_week == day:
                        lects_in_day.append(lect)

            lects_in_day = sorted(lects_in_day, key=lambda x: x.end_time, reverse=False)
            if len(lects_in_day)>1:
                last_room = 'dont_care'
                for lect in lects_in_day:
                    if last_room !='dont_care':
                        if 'p' in last_room.lower():
                            if 'p' not in lect.location.lower():
                                if last_end_time.hour == lect.start_time.hour:
                                    far_classes+=1
                        else:
                            if 'p' in lect.location.lower():
                                if last_end_time.hour == lect.start_time.hour:
                                    far_classes += 1

                    last_end_time = lect.end_time
                    last_room = lect.location
        self.far_classes =far_classes
        return far_classes



    def string_fitness_paramenters(self):
        return('\n' + 'score = ' + str(self.solution.objective.evaluation()) + '        '
                                              'windows = '+str(self.table_windows)+'      '
                                              'spesific_window_desecrated = '+str(self.spesific_window_desecrated) +'     '
                                              'overlaps = ' + str(self.overlaps_number) + '    '
                                              'school_days' + str(self.numer_of_school_days) + '    '
                                              'spesific days off violated = ' + str(self.days_violated) + '     '
                                              'specific_lecturers_violated = '+str(self.specific_lecturers_violated)+ '    '
                                              'far_classes = ' + str(self.far_classes))



