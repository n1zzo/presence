from db import DB
from falcon_cors import CORS
import base64
import falcon
import hashlib
import hmac
import json
import os
import time


def get_error_json(string):
    return json.dumps({"status": "error",
                       "message": string,
                       "timestamp": int(time.time())})


def handle_authentication(params):
    if "auth" not in params:
        return False
    authenticated_params = {x: params[x] for x in params if x != "auth"}
    # Sort them alphabetically
    message = ""
    for k, v in authenticated_params.items():
        message += str(k)
        message += "="
        message += str(v)
        message += "&"
    message = message[:-1]
    key = bytes(os.environ["PRE_SHARED_KEY"], 'UTF-8')
    message = bytes(message, 'UTF-8')
    print(message)
    digester = hmac.new(key, message, hashlib.sha256)
    raw_sig = digester.digest()
    b64_sig = base64.urlsafe_b64encode(raw_sig)
    signature = str(b64_sig, 'UTF-8') 
    print("Expected: ",signature)
    print("Received: ",params["auth"])
    return signature == params["auth"]


class StudentsList:
    def on_get(self, req, resp):
        """Handles GET requests"""
        content = {}
        params = req.params
        if not handle_authentication(params):
            #resp.status = falcon.HTTP_401
            #resp.body = get_error_json("Unauthorized access!")
            #return
            content["auth"] = "failed"
        else:
            content["auth"] = "success"
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
        if not handle_authentication(params):
            #resp.status = falcon.HTTP_401
            #resp.body = get_error_json("Unauthorized access!")
            #return
            content["auth"] = "failed"
        else:
            content["auth"] = "success"
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
        if not handle_authentication(params):
            #resp.status = falcon.HTTP_401
            #resp.body = get_error_json("Unauthorized access!")
            #return
            content["auth"] = "failed"
        else:
            content["auth"] = "success"
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
        if not handle_authentication(params):
            #resp.status = falcon.HTTP_401
            #resp.body = get_error_json("Unauthorized access!")
            #return
            content["auth"] = "failed"
        else:
            content["auth"] = "success"
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
        if not handle_authentication(params):
            #resp.status = falcon.HTTP_401
            #resp.body = get_error_json("Unauthorized access!")
            #return
            content["auth"] = "failed"
        else:
            content["auth"] = "success"
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


cors = CORS(allow_origins_list=['http://localhost:8000'],
            allow_all_headers=True,
            allow_all_methods=True)


api = falcon.API(middleware=[cors.middleware])
api.add_route('/list', StudentsList())
api.add_route('/registered', Registered())
api.add_route('/notyet', NotYet())
api.add_route('/register', Register())
api.add_route('/timer', Timer())
api.add_route('/groups', Groups())
api.add_route('/groupinfo', GroupInfo())
