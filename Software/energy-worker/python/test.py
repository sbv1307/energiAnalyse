import sys
import os

from os.path import exists


#file_exists = exists("/usr/src/app/postgres.ini")

if (not exists("/usr/src/app/postgres.ini")):
    print('Inifile does not exist - creating one')
    content = """[postgresql]
host=%s
database=%s
user=%s
password=%s
""" % (os.environ['POSTGRES_HOST'], os.environ['POSTGRES_DB'], os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'])
    print(content)
    f = open("postgres.ini", "w")
    f.write(content)
