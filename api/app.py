import os
import sys
import json
from datetime import timedelta
import mariadb
from flask import Flask, jsonify, session, request, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies


def create_connection_pool():
    """Creates and returns a Connection Pool"""

    pool = mariadb.ConnectionPool(
    host="mariadb",
    port=3306,
    user="root",
    password=os.getenv("DB_PASS"),
    database="scoreboard",
    pool_name="web-app",
    pool_size=50)

    # Return Connection Pool
    return pool


# Connect to MariaDB Platform
try:
    pool = create_connection_pool()
    # pconn = pool.get_connection()
except Exception as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
# Get Cursor


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)
jwt = JWTManager(app)
current_flag = os.getenv("FLAG")
sub_disabled = os.getenv("DISABLED")

@app.route('/check', methods=['POST'])
def check():
    if sub_disabled == 1:
        return jsonify({'message': 'Submissions are disabled right now :P'}), 200
    try:
        req = request.form.get('flag').strip()
        if req == current_flag:
            resp = jsonify({'message': 'Correct'})
            access_token = create_access_token(identity="user_solve")
            set_access_cookies(resp, access_token, domain=os.getenv("DOMAIN"))
            return resp
        else:
            return jsonify({'message': 'Incorrect'}), 200
    except Exception as e:
        print(f"Encountered error: {e}\n")
        return jsonify({'message': 'Bad request'}), 400


@app.route('/submit-solve', methods=['POST'])
@jwt_required()
def submit_solve():
    try:
        user_id = get_jwt_identity()

        if user_id != "user_solve":
            return jsonify({'message': 'Unauthorized'}), 403

        username = request.form.get('username').strip()

        if username == "" or username == " " or username == None:
            return jsonify({'message': 'Invalid username'}), 400
        pconn = pool.get_connection()
        cur = pconn.cursor()
        cur.execute("SELECT * FROM global WHERE username=(?) FOR UPDATE",(username,))
        #pconn.commit()
        if cur.rowcount == 0:
            cur.execute("INSERT INTO global values (?, ?, CURRENT_TIMESTAMP())",(username, 0,))
            pconn.commit()
        else:
            cur.execute("SELECT username FROM current WHERE username=(?)",(username,))
            #pconn.commit()
            if cur.rowcount == 1:
                pconn.close()
                return jsonify({'message': 'Username has already submitted'}), 200

        cur.execute("UPDATE global SET points = points + 1, time = CURRENT_TIMESTAMP() WHERE username=(?)",(username,))
        pconn.commit()
        cur.execute("INSERT into current values (?, CURRENT_TIMESTAMP())", (username,))
        pconn.commit()
        pconn.close()
        resp = jsonify({'message': 'Submitted'})
        unset_jwt_cookies(resp)
        return resp, 200
    except Exception as e:
        print(f"Error when submitting points: {e}")
        return jsonify({'message': 'Bad request'}), 400

@app.route('/current', methods=['GET'])
def current_lb():
        pconn = pool.get_connection()
        cur = pconn.cursor()
        cur.execute("SELECT username, cast(time as char) from current order by time")
        res = cur.fetchall()
        pconn.close()
        return jsonify({'message': res}), 200

@app.route('/global', methods=['GET'])
def global_lb():
        pconn = pool.get_connection()
        cur = pconn.cursor()
        cur.execute("SELECT username, points from global order by points DESC, time")
        res = cur.fetchall()
        pconn.close()
        return jsonify({'message': res}), 200

if __name__ == "__main__":
    with app.app_context():
        app.run(host="0.0.0.0", port=9000, debug=False)
