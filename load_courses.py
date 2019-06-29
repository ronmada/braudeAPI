from GADS import Course,Course_Group,Kita,Lect,Cluster
from flask_restful import  abort
import copy , argparse , pymongo ,json

uri = "mongodb://sagi-ron-db:V9YEv49oFLGNEYkVDT0hcYodsYHIhsGcumNuyppyWzP0HojUTqQuboe9DXhbqEMRU1JQlvl0NFoBy09AeicdbA==@sagi-ron-db.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)

db = client['adata']
mycorcl = db["coursescol"]

class Classes:

    def __init__(self):
        self.courses=[]
        self.clusters=[]

    def setup_main(self):
        args = self.parse()
        self.run(args)

    def run(self,courses,clusters):
        """

        :param args: args.courses = list of courses id's || and args.clusters = list of lists of courses
        :return: (self.courses,self.clusters)
        """
        if len(courses)>0:
            for course in courses:
                self.courses.append(self.deserializeJson(course))
            i=1
            for course in self.courses:
                print("loads_courses.py: COURSE HERE (number: " + str (i) + ")""  Course Info:  " + str(course))
                i=i+1
        cluster_id = 0
        if len(clusters)>0:
            for cluster in clusters:
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


def findCourse(course_id):
    doc_count = int(mycorcl.count_documents({"__Course__.id": course_id}))
    print("Docs found:" + str(doc_count))
    if int(doc_count) > 1:
        print("course_id {} appears more than once on DB".format(course_id))
        abort(1, message="course_id {} appears more than once on DB".format(course_id))
    elif doc_count == 0:
        print("Course ID: " + str(course_id) + " doesn't exist")
        abort(404, message="Course ID: {} doesn't exist".format(course_id))
    course = mycorcl.find_one({"__Course__.id" : course_id}, {"_id": 0})
    print("Course ID:" + str(course_id))
    #print("Course:" + str(course))
    return course

def decodejson(self,courseobj):
    serialized = json.dumps(courseobj, indent=4, cls=CustomEncoder)
    deserialized = json.loads(serialized, object_hook=decode_object)
    return deserialized


def insert_docs():
    print("INSERTING")
    with open('all_courses_final_edition.json', 'r') as f:
        datastore = json.load(f)
    datastore_copy = copy.deepcopy(datastore)
    print("Total number of documents found before insertion:" + str(mycorcl.count()))
    x = mycorcl.insert_many(datastore)
    print("Mongo Message:" + str(x))
    print("Total Number of Documents found after insertion:" + str(mycorcl.count()))
    #print("|DATASTORE STARTS HERE|" + str(datastore_copy) + "|AFTER DATASTORE ENDS HERE|") # all inserted documents
    with open('datastore.json', 'w', encoding='utf-8') as f:
        f.write(str(datastore))
    return datastore_copy

def dropcollection():
    mycorcl.drop()
    print("Collection dropped")

def getallcourses():
    courselist = []
    for course in mycorcl.find({}, {"_id": 0}):
        courselist.append(course)
    print("Total Number of Documents Found: " + str(int(mycorcl.count_documents({}))))
    return courselist


def decode_object(o):
    if '__Course__' in o:
        a = Course(0, "fifi", [])
        a.__dict__.update(o['__Course__'])
        return a
    elif '__Course_Group__' in o:
        a = Course_Group(0, "name", 0, [])
        a.__dict__.update(o['__Course_Group__'])
        return a
    elif '__Kita__' in o:
        a = Kita("type", 0, [], [], 0)
        a.__dict__.update(o['__Kita__'])
        a.lecturer = a.lectures[0].lecturer
        return a
    elif '__Lect__' in o:
        a = Lect("", "", "", "", "", "")
        a.__dict__.update(o['__Lect__'])
        return a
    return o


class CustomEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        return {'__{}__'.format(o.__class__.__name__): o.__dict__}

if __name__== "__main__":
    # activation via command line is a possibility
    Classes().setup_main()

