from flask import Flask, jsonify, abort , send_from_directory
from flask_restful import Resource, Api, reqparse, abort
import pymongo
import bson.json_util
import json, copy, ast, sys
from GA import run
from GADS import Cluster,Course,Course_Group,Kita,Lect
from load_courses import findCourse, decodejson


# to run app from POWERSHELL:
# Set-Item Env:FLASK_APP ".\application.py"
# flask run
app = Flask(__name__)
api = Api(app)
uri = "mongodb://ronsagi:aGhDWNKX0QWEriojd9mG9y7zB0vZNQ79dBpnm6DrSkio3gndDMWSMvm4EMmqy1qmoE7bt38GMWxM6FuK0P3oJA==@ronsagi.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
db = client['adata']
mycol = db["customers"]
mycorcl = db["coursescol"]

parser = reqparse.RequestParser()

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    "todo3": {'task': 'profit!'},
}

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
  return send_from_directory('./', path)


@app.route('/')
def root():
  return send_from_directory('./', 'index.html')

'''
@app.route('/')
def index():
    return "Hello, Worlds@@!"
'''
@app.errorhandler(500)
def server_error(e):
  return 'An internal error occurred [application.py] %s' % e, 500

@app.route('/todo/api/v1.0/tasks/<int:task_id>/', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/checkDB', methods=['GET'])
def checkDBexistence():
    dblist = client.list_database_names()
    if "adata" in dblist:
        return ("The database exists.")
    return ("not exists")


@app.route('/checkCollection', methods=['GET'])
def checkCollectionexistence():
    x = mycol.find_one({}, {"_id": 0})
    return jsonify(x)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/rere')


class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        parser.add_argument("task")
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


api.add_resource(TodoList, '/todos')


class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        parser.add_argument("task")
        args = parser.parse_args()
        print(args)
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


api.add_resource(Todo, '/todos/<todo_id>')


class Insert_one(Resource):
    def post(self):
        parser.add_argument("name")
        parser.add_argument("age", type=int)
        args = parser.parse_args()
        print(args)
        x = mycol.insert_one(args)
        print(x)
        return "Okay"


api.add_resource(Insert_one, '/inserto')


class Post_one(Resource):
    def post(self):
        parser.add_argument("name")
        parser.add_argument("age", type=int)
        args = parser.parse_args()
        myquery = ({"name": "something11", "age": 22})
        print(args.name)
        print("age:" + str(args.age))
        newvalues = {"$set": {"name": args.name, "age": args.age}}
        print(newvalues)
        x = mycol.update_one(myquery, newvalues)
        print("Status Msg:" + str(x))
        return "Okay"


api.add_resource(Post_one, '/postto')

'''
class Put_one(Resource):
    def put(self,name_id):
        parser.add_argument("name")
        parser.add_argument("age",type=int)
        args = parser.parse_args()
        x = abortif(name_id)
        print("SOURCE:" + str(x))
        dest_ = { "$set": { "name":args.name ,"age":args.age} }
        print("DEST:" + str(dest_))
        y=mycol.update_one(x,dest_)
        print(y)
        z=int(mycol.count_documents({"name": args.name,"age":args.age }))
        print("Num of Docs:" + str(z))
        final_= mycol.find_one({"name":args.name, "age":args.age },{"_id" : 0})
        return jsonify(final_)

api.add_resource(Put_one, '/putto/<name_id>')
'''


class insertDocs(Resource):
    def get(self):
        print("INSERTING")
        with open('all_courses_final.json', 'r') as f:
            datastore = json.load(f)
        datastore_copy = copy.deepcopy(datastore)
        print("Total number of documents found before insertion:" + str(mycorcl.count()))
        x = mycorcl.insert_many(datastore)
        print("Mongo Message:" + str(x))
        print("Total Number of Documents found after insertion:" + str(mycorcl.count()))
        #print("|DATASTORE STARTS HERE|" + str(datastore_copy) + "|AFTER DATASTORE ENDS HERE|") # all inserted documents
        with open('datastore.json', 'w', encoding='utf-8') as f:
            f.write(str(datastore))
        return jsonify(datastore_copy)


api.add_resource(insertDocs, '/insertdocs')


class dropColl(Resource):
    def get(self):
        mycorcl.drop()
        print("Collection dropped")
        return "collection dropped"


api.add_resource(dropColl, '/dropcoll')


class getAllCourses(Resource):
    def get(self):
        y = []
        for x in mycorcl.find({}, {"_id": 0}):
            y.append(x)
        print("Total Number of Documents Found: " + str(int(mycorcl.count_documents({}))))
        return jsonify(y)


api.add_resource(getAllCourses, '/getallcor')


class getCourseJson(Resource):
    def get(self,course_id):
        # parser.add_argument("course")
        # args = parser.parse_args()
        course = findCourse(course_id)
        print("Course ID:" + str(course_id))
        print("Course:" + str(course))
        return jsonify(course)


api.add_resource(getCourseJson, '/getcorj/<course_id>')


# class getCourseGA(Resource):
def getCourseGA(self, course_id):
    course = findCourse(course_id)
    return course


# api.add_resource(getCourseGA, '/getcorga/<course_id>')

class getCourse_(Resource):
    def get(self, course_id):
        course = getCourseGA(self, course_id)
        # print(course["kita"])
        return jsonify(course)


api.add_resource(getCourse_, '/getcorga/<course_id>')





class Start_GA(Resource):
    #def get(self,courses,clusters,specific_windows,specific_days_off,lecturers):
    """
    example run(['11231','61992','11102'],[['61958', '11102'],['61963','61964','61965']],['(0,2)', '(1,2)', '(2,2)', '(3,2)', '(4,2)'],['0', '2', '4'],['(11102,practice,"דר אדר רון")'])

    :param courses: list of course ids in strings
    :param clusters: lists of lists (clusters) of course id's as strings
    :param specific_windows: list of tuples as strings. for each specific window : (day,period) like so (0,0) means: (yum aleph, 8:30-9:30)') as a string
    :param specific_days_off: list of ints as strings , for each specific day off add: day1 day2... like so -specific_days_off [0,4]
    :param lecturers: list of tuples as strings, add specific prefered lecturer to a courses lectuer  (c_id,lect lype, name)
                             like so (61132,practice,"שגיא אריאלי"), this should only be used for courses and not clusters)
    :return:
    """
    # run(courses,clusters,specific_windows,specific_days_off,lecturers)



    def get(self):
        return (run(['11231','61992','11102'],[['61958', '11102'],['61963','61964','61965']],['(0,2)', '(1,2)', '(2,2)', '(3,2)', '(4,2)'],['0', '2', '4'],['(11102,practice,"דר אדר רון")']))


api.add_resource(Start_GA, '/start_ga')

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
        a.lecturer = a.lectures[0].lecturer
        return a
    elif '__Lect__' in o:
        a = Lect("","","","","","")
        a.__dict__.update(o['__Lect__'])
        return a
    return o
    
class CustomEncoder(json.JSONEncoder): 
     def default(self, o):  # pylint: disable=E0202
         return {'__{}__'.format(o.__class__.__name__): o.__dict__}