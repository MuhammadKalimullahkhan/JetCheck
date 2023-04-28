import json
from requests import Session
from wtapi.api import API_GET_ASSIGNMENTS_URL

def newSession():
    return Session()


def getAssignments(sid, class_index):
    s = newSession()
    res = s.post(
        API_GET_ASSIGNMENTS_URL,
        json={
        "sid":sid,
        "cid": class_index
        }
    ).content
    return json.loads(res)
