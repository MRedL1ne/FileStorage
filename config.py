import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__)).lower()
filedir = os.path.join(basedir,"Files").lower()
if not os.path.isdir(filedir):
    os.mkdir(filedir)

class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
        user=os.environ.get('POSTGRES_USER'),
        pw=os.environ.get('POSTGRES_PW'),
        url=os.environ.get('POSTGRES_URL'),
        port=os.environ.get('POSTGRES_PORT'),
        db=os.environ.get('POSTGRES_DB')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
