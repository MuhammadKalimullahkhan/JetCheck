from flask import Blueprint, jsonify
from jetcheck.secrets import KEY
import jwt

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("verify/user/token/<string:token>")
def verify_token(token):
    try:
        decoded = jwt.decode(token, KEY, algorithms=['HS256'])
        return jsonify(error=0, message="decoded successfully",decode=decoded)
    except Exception as e:
        return jsonify(error=1, message="Token is Invalid or Expired")