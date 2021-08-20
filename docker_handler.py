import docker
import os
from shutil import copy2, rmtree
from time import sleep
from config import mongo_host, db, collection

client = docker.from_env()

dockerfile_dir = os.getcwd()

class server:
  def __init__(self, fields):
    for field in fields:
      setattr(self, field, fields[field])

def bootstrap_dockerfile(name, seed):
  with open(dockerfile_dir+"/Dockerfile", "r") as f:
    lines = f.readlines()
  f.close()
  lines.insert(12, f"\nRUN echo 'server-name: {name}' >> plugins/MinecraftMongoDB/config.yml\n")
  lines.insert(12, f"\nRUN echo 'collection-name: {collection}' >> plugins/MinecraftMongoDB/config.yml")
  lines.insert(12, f"\nRUN echo 'database-name: {db}' >> plugins/MinecraftMongoDB/config.yml")
  lines.insert(12, f"\nRUN echo 'mongo-client-uri: {mongo_host}' >> plugins/MinecraftMongoDB/config.yml")
  lines.insert(12, "\nRUN mkdir -p plugins/MinecraftMongoDB && touch plugins/MinecraftMongoDB/config.yml")
  lines.insert(12, f"\nRUN echo 'level-seed={seed}' >> server.properties")
  lines.insert(12, f"RUN sed -i 's/motd=A Minecraft Server/motd={name}/g' server.properties")
  # error handling if directory and Dockerfile already exist?
  dir = dockerfile_dir+f"/{name}"
  os.mkdir(dir)
  copy2("wrapper.js", dir)
  with open(dir+"/Dockerfile", "w") as f:
    lines = "".join(lines)
    f.write(lines)
  f.close()
  return(dir)

def launch_container(fields):
  name = fields["name"]
  port = int(fields["port"])
  path = bootstrap_dockerfile(name, fields["seed"])
  client.images.build(path=path, tag=f"dcs-minecraft:{name}")
  container = client.containers.run(
    f"dcs-minecraft:{name}", detach=True, auto_remove=True, name=name, tty=True, stdin_open=True, ports={"25565/tcp":port})
  return(container.short_id)

# delete container, associated volumes, return whether it was successful
def delete_container(container_id, name):
  container = client.containers.get(container_id)
  if stop_container(container_id):
    container.wait()
    sleep(5)
    client.images.remove(image=f"dcs-minecraft:{name}")
    rmtree(dockerfile_dir+f"/{name}")
    # prune system to remove untagged container?
    return(True)
  else:
    return(False)

def start_container(container_id):  # unused
  return(True)

def stop_container(container_id):
  # will return false if container is stopped?
  try:
    container = client.containers.get(container_id)
    container.exec_run("/bin/ash -c \"kill 1\"", stdin=True, tty=True, detach=True)
    return(True)
  except:
    return(False)
