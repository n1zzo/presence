from db import DB
import falcon
import json
import time


def get_error_json(string):
    return json.dumps({"status": "error",
                       "message": string,
                       "timestamp": int(time.time())})


class StudentsList:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        try:
            section = params["section"]
            with DB(section) as db:
                content["list"] = db.get_students()
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


class Registered:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        try:
            section = params["section"]
            with DB(section) as db:
                content["list"] = db.get_registered(params["labid"])
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


class NotYet:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        try:
            section = params["section"]
            with DB(section) as db:
                content["list"] = db.get_not_yet_registered(params["labid"])
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


class Register:
    def on_post(self, req, resp):
        students = []
        req_json = json.loads(req.stream.read().decode('utf-8'))
        try:
            section = req_json["section"]
            with DB(section) as db:
                db.register(req_json["id"], req_json["labid"])
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        with DB(section) as db:
            students = db.get_students(student_id=req_json["id"])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'registered': students,
                                'timestamp': int(time.time())})


class Timer:
    def on_post(self, req, resp):
        req_json = json.loads(req.stream.read().decode('utf-8'))
        try:
            section = req_json["section"]
            action = req_json["action"]
            if action not in {"start", "stop"}:
                resp.status = falcon.HTTP_500
                resp.body = get_error_json("Unknown action!")
                return
            with DB(section) as db:
                db.timer(action, req_json["id"], req_json["labid"])
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        with DB(section) as db:
            students = db.get_students(student_id=req_json["id"])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'registered': students,
                                'timestamp': int(time.time())})


class Groups:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        try:
            section = params["section"]
            with DB(section) as db:
                content["list"] = db.get_groups()
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


class GroupInfo:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        try:
            section = params["section"]
            groupid = params["groupid"]
            with DB(section) as db:
                content["list"] = db.get_group_info(groupid)
        except KeyError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Missing call parameter!")
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_500
            resp.body = get_error_json("Section does not exists!")
            return
        content["timestamp"] = int(time.time())
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(content)


api = falcon.API()
api.add_route('/list', StudentsList())
api.add_route('/registered', Registered())
api.add_route('/notyet', NotYet())
api.add_route('/register', Register())
api.add_route('/timer', Timer())
api.add_route('/groups', Groups())
api.add_route('/groupinfo', GroupInfo())
