import json
from requests import Session
from jetcheck.models import Tokens
from wtapi.blueprints import *
from wtapi.assignments import *
from wtapi.api import *


def createCookies(session_id: str) -> dict:
    cookies = {
        "legacy-session-id": session_id,
        "session-id": session_id,
        "t": session_id,
        "test_cookie": "1",
        "xhfaculty": "0"
    }
    return cookies


def new_session():
    return Session()


def update_cookies(s: Session, cookies):
    s.cookies.update(cookies)


def login(creds: dict):
    s = new_session()
    auth = s.post(
        API_LOGIN_URL,
        json=creds,
        headers={
            "Content-Type": "application/json"
        }, 
        params= {"token": creds['token']}
    ).content
    auth = json.loads(auth)
    return auth['auth']


def fresh_login(creds: dict):
    s = new_session()
    auth = s.post(
        API_FRESH_LOGIN_URL,
        json=creds,
        headers={
            "Content-Type": "application/json"
        },
        params= {"token": creds['token']}
    ).content
    auth = json.loads(auth)
    return auth['auth']


def logout(session_id):
    s = new_session()
    return s.post(API_LOGOUT_URL, json={"sid":session_id}, headers={"Content-Type": "application/json"}).json()

def submit_file(file_info: dict, files:dict, token):
    s = new_session()
    # update_cookies(s, createCookies(file_info.session_id))
    return s.post(
        API_SUBMIT_FILE_URL,
        data=file_info,
        files=files,
        # headers={"Content-Type": "application/json"}
        params= {"token": token}
    )


def download_file(save_path: str, file: DownloadFileInfo, token):
    s = new_session()
    update_cookies(s, createCookies(file.session_id))
    res = s.post(
        API_DOWNLOAD_FILE_URL,
        json=file.dict(),
        headers={"Content-Type": "application/json"},
        params= {"token": token}
    )
    res = json.loads(res.content)

    # Saving file
    file_content = s.get(res['url']).content
    save_file(save_path, file_content)
    return res


def get_user_info(session_id, token):
    s = new_session()
    update_cookies(s, createCookies(session_id))
    res = s.get(API_GET_USER_INFO_URL + token)
    return res.json()


def save_file(path, file_content):
    with open(path, "wb") as f:
        f.write(file_content)


def run():

    file = SubmitFileInfo(
        file_stream=open(".myFile", "rb").read(),
        file_name="req.txt",
        file_title="JetCheck_TEST",
        auther_fname="Muhammad",
        auther_lname="Kalimullah",
        sid="ed7729522bd84ad1b5e4ecf63a487348",
        assignment_id=114235268
    )
    file.file_stream = None
    file.file_title = "JetCheck_TEST - 87077611491625032023"

    cookies = login({
        "email": "khankalimkalim121@gmail.com",
        "password": "!@Swatswat12"
    })

    file.session_id = cookies['session-id']
    data = download_file("file.pdf", file)
    print(data)


if __name__ == "__main__":
    run()
