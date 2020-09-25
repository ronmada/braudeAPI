from flask import Flask, jsonify, send_from_directory
from flask_restful import Resource, Api, reqparse
from GA import run
import load_courses
from flask_cors import CORS
from Utils import parse_args
from TableSolution import TableSolution
#hello
# to run app from POWERSHELL:
# Set-Item Env:FLASK_APP ".\application.py"
# flask run
app = Flask(__name__)
CORS(app)
api = Api(app)


parser = reqparse.RequestParser()


@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory('./dist', path)


@app.route('/')
def root():
    return send_from_directory('./dist', 'index.html')

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory('./dist', 'index.html')



@app.errorhandler(500)
def server_error(e):
    return 'An internal error occurred [application.py] %s' % e, 500


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/rere')


class insertDocs(Resource):
    def get(self):
        return jsonify(load_courses.insert_docs())

api.add_resource(insertDocs, '/insertdocs')


class dropColl(Resource):
    def get(self):
        load_courses.dropcollection()
        return "collection dropped"

api.add_resource(dropColl, '/dropcoll')


class tester(Resource):
    def get(self):
        return jsonify("TEST OK")

api.add_resource(tester, '/testy')

class getAllCourses(Resource):
    def get(self):
        return jsonify(load_courses.getallcourses())

api.add_resource(getAllCourses, '/getallcor')


class getCourseJson(Resource):
    def get(self,course_id):
        return jsonify(load_courses.findCourse(course_id))

api.add_resource(getCourseJson, '/getcorj/<course_id>')


class getCourseJson2(Resource):
    def get(self):
        parser.add_argument("courseid")
        args = parser.parse_args()
        print("COURSEID:" + str(args.courseid))
        course = load_courses.findCourse(args.courseid)
        #print("Course:" + str(course))
        courselist = []
        courselist.append(course)
        return jsonify(course)

api.add_resource(getCourseJson2, '/getcorjs')


class Start_GA(Resource):
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
        parser.add_argument('courses', type=str, default=False,action='append',
                          help='a course number')
        parser.add_argument('cluster', type=str, action='append', default=[],
                          help='for each - group a group containing the courses will be added')
        parser.add_argument('specific_windows', action='append', type=str, default=False,
                          help='for each specific window : add -spedific_window (day,period) like so (0,0) means:'
                               ' (yum aleph, 8:30-9:30)')

        parser.add_argument('specific_days_off', action='append', type=str, default=False,
                          help='for each specific day off add: -specific_days_off day1 day2... like so -specific_days_off 0 4')
        parser.add_argument('lecturer', action='append', type=str, default=False,
                          help='add specific prefered lecturer to a courses lectuer -lecturer (c_id,lect lype, name)'
                               ' like so (61132,practice,"שגיא אריאלי"), this hould only be used for courses and '
                               'not clusters')
        parser.add_argument('specific_windows_weight', default=False,
                            help='the weight of specific_windows')
        parser.add_argument('specific_days_off_weight', default=False,
                            help='the weight of specific_days_off')
        parser.add_argument('specific_lecturer_weight', default=False,
                            help='the weight of specific_lecturer')
        args = parser.parse_args()
        #courses fix
        if args['courses']:
            courses =args['courses'][0].split(' ')
            args['courses'] = courses
        else:
            args['courses'] = []
        #cluster fix
        clusters = []
        for clust in args['cluster']:
            cluster = clust.split(' ')
            clusters.append(cluster)
        args['cluster'] = clusters
        # specific_windows fix
        if args['specific_windows']:
            specific_windows = args['specific_windows'][0].split(' ')
            args['specific_windows'] = specific_windows
            print(args['specific_windows'])

        # specific_days_off
        if args['specific_days_off']:
            specific_days_off = args['specific_days_off'][0].split(' ')
            args['specific_days_off'] = specific_days_off
            print(args['specific_days_off'])

        if not args['lecturer']:
            args['lecturer'] = []

        ret = []
        solutions = run(args['courses'], args['cluster'], args['specific_windows'], args['specific_days_off'],
                        args['lecturer'], int(args['specific_windows_weight']),int(args['specific_days_off_weight']),
                        int(args['specific_lecturer_weight']))
        for sol in solutions:
            classes = []
            for clas in sol.lectures:
                lectures = []
                for lecture in clas.lectures:
                    lect = {
                        "Semester": lecture.semester,
                        "Day": lecture.day_in_week,
                        "Start_time": lecture.start_time.hour,
                        "End_time": lecture.end_time.hour,
                        "Lecturer_name": lecture.lecturer,
                        "Class_location": lecture.location
                    }
                    lectures.append(lect)
                kita = {
                    "Class_type": clas.type,
                    "group_number": clas.g_number,
                    "Related_groups": clas.related_groups,
                    "lectures": lectures,
                    "c_ID": clas.c_id,
                    "lecturer": clas.lecturer
                }
                classes.append(kita)
            solution = {
                "classes": classes,
                "Score": sol.objective.string_fitness_paramenters()

            }
            ret.append(solution)

        json_res = {
            "results": ret
        }
        return jsonify(json_res)

api.add_resource(Start_GA, '/start_ga')