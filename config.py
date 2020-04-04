import os

def get_environment_values(value):
    if 'DYNO' in os.environ:
        return os.environ.get(value)
    else:
        return os.getenv(value)

class BaseConfig:
    PROJECT = 'static_site_generator'
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DEBUG = False
    TESTING = False
    SECRET_KEY = get_environment_values('SECRET_KEY')
    AX_CONTENT_LENGTH = 16 * 1024 * 1024
    GITHUB_CLIENTID =  get_environment_values('GITHUB_CLIENTID')
    GITHUB_CLIENTSECRET =  get_environment_values('GITHUB_CLIENTSECRET')
    GITHUB_PAGES = None
    GITHUB_DRAFT_PAGES = None
    GITHUB_ACCESSTOKEN = None

    GITHUB_REPO = None
    POSTS_FOLDER = None
    DRAFT_FOLDER = None


class Development(BaseConfig):
     DEBUG = True

class Production(BaseConfig):
     DEBUG = False
