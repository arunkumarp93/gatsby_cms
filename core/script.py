import base64
import os

from github import Github
from github import InputGitTreeElement

from core.utils import allowed_file

from core import settings


def read_local_storage():
    file_location = os.getcwd() + '/.local_store'


# create new commit start
def initialize():
    """
    Try to get the token, repo from the local storage.

    if it's there fetch from the github given username.

    Not there then return False

    """
    local_data = read_local_storage()
    config = settings.app.config
    token = config.get('GITHUB_ACCESSTOKEN')
    repo = config.get('GITHUB_REPO')
    git_username = ''
    if token and repo:
        g = Github(token)
        try:
            repo = g.get_repo('{}/{}'.format(repo, git_username))
        except Exception as e:
            return False, 'configure_github_folders'
        branch = repo.get_branch('master')
        tree = repo.get_git_tree(branch.commit.sha)
        master_ref = repo.get_git_ref('heads/master')

        return True, {'repo': repo, 'branch': branch, 'tree': tree, 'master_ref': master_ref}
    else:
        if not token and repo:
            return False
        elif not token:
            return False, 'login'
        else:
            return False, 'configure_github_folders'


def create_git_blob(repo, content, convert_type):
    return repo.create_git_blob(content, convert_type)


def upload_blob(repo, path, not_text=False):
    """
     repo : "pass the repo"
     path: (string)  blob file full path
     not_text: (bool) check the blob is just text file

     return : blob sha
    """
    if not_text:
        data = base64.b64encode(open(path, "rb").read())
        blob = create_git_blob(repo, data.decode("utf-8"), "base64")
        return blob

    blob = create_git_blob(repo, open(path, "r").read(), 'utf-8|base64')
    return blob


def upload_blobs(repo, file, path):
    """
     utils to check file type and upload blob

     return: git blob
    """
    if allowed_file(file):
        return upload_blob(repo, path + '/' + file, True)
    else:
        return upload_blob(repo, path + '/' + file)


def create_blobs(path, repo, upload_list=[]):
    """
      path: directory to upload
      repo: repo object

      upload_list: upload only specific files in the path

      return (dict) filenames and git blobs
    """
    result = {}
    if not upload_list:
        directories = os.listdir(path)
        for file in directories:
            result[file] = upload_blobs(repo, file, path)
    else:
        for file in upload_list:
            result[file] = upload_blobs(repo, file, path)

    return result


def create_input_git_tree(git_path, mode, file_type, sha):
    """
    git_path  : (string) Where git file need to be
    mode      : (string) It must be in three modes
                1. 100644 (blob)
                2. 100755 (executable)
                3. 040000 (subdirectory/tree)
                4. 160000 (submodule/commit)/120000 (blob specifying path of symlink)
    file_type : (string) Type of the tree can in these three
                1. "blob"
                2. "tree"
                3. "commit"
    sha       : (string) sha value of the blob uploaded before

    return : ( object ) InputGitTreeElement
    """

    return InputGitTreeElement(git_path, mode, file_type, sha=sha)


def create_git_tree(repo, element_tree, base_tree):
    """
    repo : "pass the repo object"
    element_tree : (list) list of InputGitTreeElement
    base_tree    : (GitTree object) get the base tree repo.get_git_tree
     """
    return repo.create_git_tree(tree=element_tree, base_tree=base_tree)


def create_git_commit(repo, message, tree, parent):
    """
    repo : "pass the repo object"
    message : (string) commit message
    tree    : (Gittree) Created Git Tree
    parent  : (list) parent list where the commit need to create
             repo.get_git_commit
    return : (object) commit object with sha value
    """
    return repo.create_git_commit(message, tree, [parent])


def update_commit(ref, new_head):
    """
    ref      : (branch refernce) E.g: repo.get_git_ref('heads/master')
    new_head : (string) new head sha value
            (commit sha value create in create_git_commit)
    """
    ref.edit(new_head, True)


# create new commit end

# manage contents start
def update_file(repo, path, message, content, sha):
    """
     repo: "pass the repo object"
     path: file path
     message: commit message
     content: file current content
     sha: fle sha value
    """
    return repo.update_file(path, message, content, sha)


def get_contents(repo, path):
    """
      repo : "pass the repo object"
      path :(string) path to get the cotnents
            E.g "" read all the comments

     return : list contents/None
    """
    try:
        return repo.get_contents(path)
    except:
        return None


def get_content_from_folder(repo, contents):
    result = {}
    for content in contents:
        temp = {}
        if content.type == 'dir':
            path = content.path
            files = get_contents(repo, content.path)
            temp['path'] = path
            temp['files'] = files
            result[content.name] = temp
    return result


def decode_content(content, text=False):
    """
    content:  string file content
    return : decoded string
    """
    if text:
        return base64.b64decode(content).decode('utf-8')
    return base64.b64decode(content)


# manage contents end

def create_element_tree(blobs, git_path, mode='100644', file_type='blob'):
    element_tree = []
    for file, blob in blobs.items():
        sha = blob.sha
        input_tree = create_input_git_tree(git_path + '/' + file, mode, file_type, sha)
        element_tree.append(input_tree)
    return element_tree
