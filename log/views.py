from flask import Blueprint, jsonify, make_response, request
from admins.models import Admin
from libs.db import LogRecord
log_record_bp = Blueprint("log_record", import_name="log_record")

@log_record_bp.route('/log_record', methods=["POST"])
def create():
    print("create log")
    data = request.json
    # log_record = LogRecord(data)
    res = Admin(LogRecord, log_record_bp).upLoad(data)
    return res

@log_record_bp.route("/log_record", methods=['GET'])
def getAll():
    res = Admin(LogRecord, log_record_bp).getAll()
    response = make_response(jsonify(res['data']))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-24/' + str(len(res['data']))
    return response

@log_record_bp.route("/log_record/<int:id>", methods=['GET'])
def getOne(id):
    res = Admin(LogRecord, log_record_bp).getOne(id)
    response = make_response(jsonify(res))
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = 'posts 0-24/' + str(len(res['data']))
    return response
