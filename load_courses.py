from GADS import Course,Course_Group,Kita,Lect,Cluster
from application import findCourse, decodejson
import os
import argparse

class Classes:

    def __init__(self):
        self.courses=[]
        self.clusters=[]

    def setup_main(self):
        args = self.parse()
        self.run(args)

    def run(self,args):
        """

        :param args: args.courses = list of courses id's || and args.clusters = list of lists of courses
        :return: (self.courses,self.clusters)
        """
        if args.courses:
            for course in args.courses:
                self.courses.append(self.deserializeJson(course))
            i=1
            for course in self.courses:
                print("loads_courses.py: COURSE HERE (number: " + str (i) + ")""  Course Info:  " + str(course))
                i=i+1
        cluster_id = 0
        if len(args.cluster)>0:
            for cluster in args.cluster:
                cluster_id+=1
                new_cluster=Cluster(cluster_id,[])
                for course in cluster:
                    new_cluster.courses.append(self.deserializeJson(course))
                self.clusters.append(new_cluster)
                print("loads_courses.py: CLUSTER HERE:  " + str(self.clusters))

        return self.courses, self.clusters



    def deserializeJson(self,course_id):
        course=findCourse(course_id)
        coursereturn = decodejson(self,course)
        print("Course is:" + str(coursereturn))
        return coursereturn

    def parse(self):
        parser = argparse.ArgumentParser(description='get courses and clusters')
        parser.add_argument('-courses', nargs='+',type=str,default= False,
                            help='a course number')
        parser.add_argument('-cluster',type=str, nargs='+', action='append', default= [],
                            help='for each - group a group containing the courses will be added')

        return parser.parse_args()




if __name__== "__main__":
    # activation via command line is a possibility
    Classes().setup_main()

