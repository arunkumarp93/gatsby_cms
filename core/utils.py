import shutil
import os
import requests
from datetime import datetime

from core import settings

# constant start
PAGES = os.getcwd() + '/static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.getcwd() + '/temp'
# constant end


def github_remove_images(remove_images, path, repo):
    """
       delete the image from the path.
       remove_images (list): list of images to be removed
       path (string): github path
    """
    if remove_images:
        for image in remove_images:
            try:
                file = repo.get_contents('{}/{}'.format(path, image))
                message = 'removed {}'.format(image)
                repo.delete_file(path + '/' + image, message, file.sha)
            except:
                pass
    return


def get_content_type(path):
    return path.split('/')[1]


def get_app_config():
    return settings.app.config


def get_post_folder(draft=False):
    config = get_app_config()
    if draft:
        return config.get('DRAFT_FOLDER')
    return config.get('POSTS_FOLDER')


def get_draft_folder():
    config = get_app_config()
    return config.get('DRAFT_FOLDER')


def get_session_token():
    config = get_app_config()
    return config.get('GITHUB_ACCESSTOKEN')


def post_call(url, data):
    session = requests.session()
    return session.post(url, data)


def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception as e:
        raise e


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_static_page(file_path, title, category, description, folder=''):
    """
    """
    f = open(file_path, 'w+')
    f.write('---\n')
    f.write('title: ' + title + '\n')
    f.write('category: ' + category + '\n')
    f.write('date: ' + '{}'.format(datetime.now().strftime("%m/%d/%Y")) + '\n')
    f.write('author: ' + 'arunkumar' + '\n')
    f.write('updated: ' + ' ' + '\n')
    f.write('folder:' + folder + '\n')
    f.write('---\n')
    f.write(description)


def move_images(images, destination):
    """
    """
    for image in images:
        source = os.getcwd() + image
        try:
            shutil.move(source, destination)
        except FileNotFoundError:
            return (None, image)
    return (True, None)


def clear_temp_static(temp=False):
    """
     Remove the images from temp folder from end of the request
    """

    if temp:
        try:
            for file in os.listdir(UPLOAD_FOLDER):
                file_path = os.getcwd() + '/temp/' + file
                if os.path.isdir(file_path):
                    try:
                        shutil.rmtree(file_path)
                    except:
                        pass
                else:
                    os.unlink(file_path)
        except Exception as e:
            print("*" * 150, e)
            pass
    try:
        for file in os.listdir(PAGES):
            file_path = os.getcwd() + '/static/' + file
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
        else:
            try:
                os.remove(file_path)
            except:
                pass
    except Exception as e:
        print("*" * 150, e)
        pass


def get_file_contents(file):
    if not isinstance(file, str):
        file = file.decode('utf-8')
    contents = list(filter(None, file.split('---')))
    return contents


def get_article_data(article):
    contents = article.split('\n')
    temp = {}
    for content in contents:
        values = content.split(":")
        if content and len(values) == 2:
            temp[values[0]] = values[1].strip()
    return temp


def read_blogs(path=""):
    # read from file
    directory = os.listdir(PAGES)

    display_pages = {}
    for file in directory:
        current_folder = PAGES + '/' + file
        if os.path.isdir(current_folder):
            with open(current_folder + '/' + 'index.md', 'r+') as file:
                file_content = file.read()
                display_content = get_file_contents(file_content)[0]
                temp = get_article_data(display_content)
                temp['path'] = current_folder
                display_pages[temp['title']] = temp
    return display_pages


def read_file(path):
    if path:
        try:
            with open(path + '/index.md') as file:
                file_content = file.read()
                contents = get_file_contents(file_content)
                description = contents[1]
                data = get_article_data(contents[0])
                return data, description
        except Exception as e:
            return None
