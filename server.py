import falcon
import json
import time
from db import DB


students_list = [{"student": "John Doe",
                  "email": "john.doe@mail.polimi.it",
                  "registered": True}]


class StudentsList:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        with DB() as db:
            content["list"] = db.get_students()
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


class Status:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        with DB() as db:
            content["list"] = db.get_status(params["labid"])
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


class Register:
    def on_post(self, req, resp):
        students = []
        req_json = json.loads(req.stream.read().decode('utf-8'))
        with DB() as db:
            db.register(req_json["id"], req_json["labid"])
            students = db.get_students(student_id=req_json["id"])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'registered': students,
                                'timestamp': int(time.time())})


api = falcon.API()
api.add_route('/list', StudentsList())
api.add_route('/status', Status())
api.add_route('/register', Register())
