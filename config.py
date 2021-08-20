import configparser

config = configparser.ConfigParser()
config.read("config.ini")

host = config["Local Machine"]["host"]

mongo_host = config["MongoDB"]["host"]
db = config["MongoDB"]["db"]
collection = config["MongoDB"]["collection"]