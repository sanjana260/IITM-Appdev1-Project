# creating exceptions for the various status codes for our api
from distutils.archive_util import make_archive
from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class RaiseError(HTTPException):
    def __init__(self, statuscode):
       self.response = make_response("",statuscode)

class BusinessValidationError(HTTPException):
    def __init__(self,statuscode, error,error_message):
        message = {"error_code":error, "error_message":error_message}
        self.response = make_response(json.dumps(message),statuscode)