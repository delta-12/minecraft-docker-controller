import flask
from flask import jsonify
from docker_handler import delete_container, start_container, stop_container
from db import find_id, count_servers, insert_server, remove_server

api = flask.Flask(__name__)

# Verify user id for each request
@api.before_request
def verify_user():
  if "user_id" in flask.request.form.keys():
    if not find_id(str(flask.request.form["user_id"])):
      return(jsonify(error="user validation failed"), 401)
  else:
    return(jsonify(error="no user id"), 401)

# Create a new minecraft server
@api.route("/create_server", methods=["POST"])
def create_server():
  if count_servers() < 10:  # max of 10 servers
    response = insert_server(flask.request.form.copy())  # prevent users from specifying certain data, e.g. port?
    if response[0] == True:
      return(jsonify(id=response[1], status="Successfully created."), 201)
    else:
      return(jsonify(error=response), 400)
  else:
    return(jsonify(error="server count cannot exceed 10"), 405)

# Delete an existing minecraft server
@api.route("/delete_server", methods=["POST"])
def delete_server():
  if "server_id" in flask.request.form.keys():
    server_id = str(flask.request.form["server_id"])
    response = remove_server(server_id)
    if response == 1:
      return(jsonify(id=server_id, status="deleted"), 200)
    elif response == 0:
      return(jsonify(error=f"server with id {server_id} not found"), 404)
    else:
      return(jsonify(error=response), 400)
  else:
    return(jsonify(error="no server id"), 400)

# Start a stopped minecraft server
@api.route("/start_server", methods=["POST"])
def start_server():
  if "server_id" in flask.request.form.keys():
    server_id = str(flask.request.form["server_id"])
    # lookup server in database and return container id
    # add container id to class + database schema?
    container_id = ""
    start_container(container_id)
    return(jsonify(id=server_id, status="started"), 200)
  else:
    return(jsonify(error="no server id"), 401)

# Stop running minecraft server
@api.route("/stop_server", methods=["POST"])
def stop_server():
  if "server_id" in flask.request.form.keys():
    server_id = str(flask.request.form["server_id"])
    # lookup server in database and return container id
    # add container id to class + database schema?
    container_id = ""
    stop_container(container_id)
    return(jsonify(id=server_id, status="stopped"), 200)
  else:
    return(jsonify(error="no server id"), 401)

if __name__ == "__main__":
  api.run(host="0.0.0.0")
