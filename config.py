import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
filedir = f"{basedir}\\Files"
if not os.path.isdir(filedir):
    os.mkdir(filedir)

class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
        user=os.environ.get('POSTGRES_USER'),
        pw=os.environ.get('POSTGRES_PW'),
        url=os.environ.get('POSTGRES_URL'),
        db=os.environ.get('POSTGRES_DB')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
