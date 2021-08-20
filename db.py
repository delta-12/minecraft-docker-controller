from os import uname
from mongoengine import connect, Document
from mongoengine.errors import ValidationError
from mongoengine.fields import BooleanField, DateTimeField, IntField, StringField
from docker_handler import launch_container, delete_container
from config import host, mongo_host

connect(host=mongo_host)

# define users schema
class users(Document):
  username = StringField(required=True, unique=True, trim=True)
  email = StringField(required=True)
  password = StringField(required=True, min_length=8)
  date = DateTimeField()
  v = IntField(db_field="__v")

# define minecraft_servers schema
# class minecraft_servers(Document):
class minecraft_servers(Document):
  name = StringField(required=True, min_lenth=1, unique=True)
  status = StringField()
  address = StringField()
  port = StringField()
  onlinePlayers = StringField()
  maxPlayers = StringField()
  gamemode = StringField()
  difficulty = StringField()
  seed = StringField()
  software = StringField()
  version = StringField()
  container_id = StringField(required=True)
  public = BooleanField()
  owner = StringField(required=True)

# verify if user with user_id exists
def find_id(user_id):
  for user in users.objects:
    if user_id == str(user.id):
      return(True)
  return(False)

# return number of server documents in minecraft_servers collection
def count_servers():
  return(minecraft_servers.objects.count())

# assign next available port
def assign_port():
  port = 25565
  for server in minecraft_servers.objects:
    if int(server.port) > port:  # check for availibity before highest number port, may skip ports otherwise
      port = int(server.port)
  return(str(port+1))

# server.validate fails to check name uniqueness
# used to check for unique name before launching container
def check_name(name):
  for server in minecraft_servers.objects:
    if name == server.name:
      return(False)
  return(True)

# insert a new server document to minecraft_servers collection
def insert_server(fields):
  owner = fields["user_id"]
  fields.pop("user_id")
  fields.add("owner", owner),
  fields.add("address", host)
  fields.add("port", assign_port())
  fields.add("container_id", "0")  # temporarily set container so server validates
  try:
    server = minecraft_servers(**fields)  # create instance of minecraft_servers class from fields key values
    try:
      server.validate()
      if check_name(server.name):
        container_id = launch_container(fields)
        server.container_id = container_id  # update container_id with actual value
        server.save()
        return(True, str(server.id))
      else:
        return("duplicate name")
    except ValidationError as e:
      return(str(e).split("(")[2].split(")")[0])
    except Exception as e:
      return(str(e))
  except Exception as e:
    return(str(e))

# delete existing server document when server is deleted
def remove_server(server_id):
  try:
    server = minecraft_servers.objects(id=server_id).first()
    container_id = server.container_id
    name = server.name
    if minecraft_servers.objects(id=server_id).delete() == 1:
      return(delete_container(container_id, name))  # check expected response in controller
    else:
      return("failed to delete container")
  except AttributeError:
    return(0)
  except Exception as e:
    return(str(e))
