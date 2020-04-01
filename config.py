import os

class BaseConfig:
    PROJECT = 'static_site_generator'
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    AX_CONTENT_LENGTH = 16 * 1024 * 1024
    GITHUB_CLIENTID =  os.getenv('GITHUB_CLIENTID')
    GITHUB_CLIENTSECRET =  os.getenv('GITHUB_CLIENTSECRET')
    GITHUB_PAGES = None
    GITHUB_DRAFT_PAGES = None
    GITHUB_ACCESSTOKEN = None

    GITHUB_REPO = None
    POSTS_FOLDER = None
    DRAFT_FOLDER = None
    

class Development(BaseConfig):
     DEBUG = True

class Production(BaseConfig):
     pass
