import re
import os
import base64
import string
import random

from urllib.parse import urlencode, parse_qs
from functools import wraps
from datetime import datetime

import markdown2 as md2
from  github import InputGitTreeElement
from flask import (
                    current_app,
                    Blueprint,
                    render_template,
                    request,
                    Response,
                    jsonify,
                    send_from_directory,
                    redirect,
                    url_for)

from werkzeug.utils import secure_filename


from core.forms import CreateForm, FolderForm
from core.script import initialize, create_blobs, create_git_tree, \
                        create_git_commit, update_commit, upload_blob, get_contents, \
                        get_content_from_folder, decode_content, update_file, create_element_tree,\
                        create_git_blob, create_input_git_tree
from core.utils import allowed_file, create_static_page, move_images, clear_temp_static \
                        ,get_file_contents, get_article_data, read_blogs, read_file, UPLOAD_FOLDER\
                        ,pages, make_dir, post_call, get_session_token, get_app_config, get_post_folder\
                        ,get_draft_folder, get_content_type,github_remove_images

blueprint= Blueprint('core', '__name__')

#constant start
github_identity_url =  'https://github.com/login/oauth/authorize'
github_access_token_url = 'https://github.com/login/oauth/access_token'
root_url = 'http://localhost:5000'
authorize_url = 'http://localhost:5000/authorize'
#constant end

def github_upload_images(new_images, UPLOAD_FOLDER, path):
    """
     new_images(list): new images list to upload
     UPLOAD_FOLDER(string): image path
     path(string): github path to upload
     repo(object): github repo object
    """
    # create new element list and update the folder with added image
    if new_images:
       auth = initialize()
       if not auth[0]:
           return

       init = auth[1]
       branch = init.get('branch')
       master_ref = init.get('master_ref')
       repo = init.get('repo')
       tree = init.get('tree')
       parent = repo.get_git_commit(branch.commit.sha)

       #create blob for each image

       blobs = create_blobs(UPLOAD_FOLDER, repo, upload_list=new_images)
       #create element tree
       element_tree = create_element_tree(blobs, path)
       #create git tree
       git_tree= create_git_tree(repo, element_tree, tree)
       #update the head commit

       git_commit = create_git_commit(repo, 'new image added to {}'.format(path), git_tree, parent)
       update_commit(master_ref, git_commit.sha)

    return

def login_required(function=None, redirect_url=''):
    def actual_decorator(func):
        @wraps(func)
        def _wrapped_view(*args, **kwargs):

            github_auth = get_session_token()
            if github_auth:
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    return func(*args, **kwargs)
            else:
                return redirect(url_for('core.login', redirect=redirect_url))
        return _wrapped_view

    if function:
        return actual_decorator(function)
    return actual_decorator

@blueprint.context_processor
def autheticate_check():
    autheticated = get_session_token()
    return dict(is_autheticated= True if autheticated else False)

@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    client_id = os.getenv('GITHUB_CLIENTID')
    params = {'client_id':client_id, 'scope':"user,repo"}
    url = github_identity_url +'?' + urlencode(params)
    return redirect(url)

@blueprint.route('/logout')
def logout():
    config = get_app_config()
    config['GITHUB_ACCESSTOKEN'] = ''
    return redirect(root_url)

@blueprint.route('/authorize', methods=['GET', 'POST'])
def github_authorize():

    config = get_app_config()
    code = request.args.get('code')
    client_id = os.getenv('GITHUB_CLIENTID')
    client_secret = os.getenv('GITHUB_CLIENTSECRET')
    data = {'client_id':client_id, 'client_secret':client_secret, 'code':code}

    github_auth = get_session_token()

    response = post_call(github_access_token_url, data=data)
    reponse_data = parse_qs(response.content)

    for k, v in reponse_data.items():
        if len(v) == 1:
            data[k] = v[0]
        token = reponse_data.get(b'access_token', None)
        if token is not None:
            token = token[0].decode('ascii')
            config['GITHUB_ACCESSTOKEN'] = token
            return redirect(root_url)
        else:
            return redirect('/configure')

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    auth = initialize()
    if auth and auth[0]:
        init = auth[1]
        repo = init.get('repo')

        # get the posts location in github
        posts_folder = get_post_folder()
        if posts_folder:
            folders = get_contents(repo, posts_folder)
        else:
            return redirect('/configure')

        contents = get_content_from_folder(repo, folders)
        display_pages = {}

        for key, value in contents.items():
            files = value['files']
            for file in files:
                temp = {}
                if not allowed_file(file.path):
                    text =  decode_content(file.content, True)
                    display_content = get_file_contents(text)[0]
                    temp = get_article_data(display_content)

                    if temp.get('title'):
                        temp['path'] = value['path']
                        display_pages[temp['title']] = temp
                    else:
                        print (key, value)

        return render_template('index.html', pages= display_pages)
    elif not auth:

        return render_template('index.html')
    else:
        return redirect(url_for('core.'+auth[1]))

@blueprint.route('/drafts', methods=['GET', 'POST'])
def draft():
    auth = initialize()
    if auth and auth[0]:
        init = auth[1]
        repo = init.get('repo')

        # get the posts location in github
        posts_folder = get_post_folder(draft=True)
        if posts_folder:
            folders = get_contents(repo, posts_folder)
        else:
            return redirect('/configure')

        contents = get_content_from_folder(repo, folders)
        display_pages = {}

        for key, value in contents.items():
            files = value['files']
            for file in files:
                temp = {}
                if not allowed_file(file.path):
                    text =  decode_content(file.content, True)
                    display_content = get_file_contents(text)[0]
                    temp = get_article_data(display_content)

                    if temp.get('title'):
                        temp['path'] = value['path']
                        display_pages[temp['title']] = temp
                    else:
                        print (key, value)

        return render_template('index.html', pages= display_pages)
    elif not auth:
        return render_template('index.html')
    else:
        return redirect(url_for('core.'+auth[1]))

@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateForm()
    # before starting remove the previous stuffs
    clear_temp_static()
    if form.validate_on_submit():
        dir_1 = datetime.now().strftime("%m/%d/%Y")
        dir_2 = form.data['title']
        dir_name = dir_1.replace('/', '-')+'--'+dir_2.replace(' ', '-')[:20]
        dir_path = pages+'/'+dir_name
        make_dir(dir_path)
        file_path = dir_path+'/'+'index.md'
        description = form.data['description']
        draft = form.data['draft']
        images_path = re.findall('/temp/.*?\.[jpg|jpeg|png|gif]+', description)

        # TODO: remove the ne static path creation

        #move images to particular folder
        updated_description = re.sub('\(/temp/', '(./', description)
        create_static_page(file_path, dir_2, form.data['category'], updated_description)
        images_status = move_images(images_path, dir_path)

        if not images_status[0]:
            return render_template('create.html', form=form, error=True, status=images_status[1])

        #Push to git rep
        get_repo = initialize()

        if get_repo[0]:
            init = get_repo[1]
            repo = init.get('repo')
            branch = init.get('branch')
            tree = init.get('tree')
            master_ref =init.get('master_ref')

            #created blob
            blobs = create_blobs(dir_path, repo)

            #create element list
            git_dir = dir_path.split('/')[-1]

            posts_folder = get_post_folder(draft)
            if posts_folder:
                git_path = '{}{}'.format(posts_folder, git_dir)
            else:
                return redirect('/configure')

            #create Element Tree
            element_tree = create_element_tree(blobs, git_path)

            #create gittree
            if element_tree:
                git_tree= create_git_tree(repo, element_tree, tree)
                #create git commit
                parent = repo.get_git_commit(branch.commit.sha)
                git_commit = create_git_commit(repo, 'new post added in {}'.format(git_dir), git_tree, parent)
                #update the head commit
                update_commit(master_ref, git_commit.sha)

            #After the github upload remove the temp
            clear_temp_static(True)
            return redirect(root_url)
        else:
            return redirect(url_for('core.'+get_repo[1]))
    return render_template('create.html', form=form)

@blueprint.route('/editpage', methods=['GET', 'POST'])
@login_required
def edit_page():
    if request.method == 'GET':
        clear_temp_static(True)
        path = request.args.get('path', None)
        folder_path =  path.split('/')[-1]
        if path:
            get_repo = initialize()
            if get_repo[0]:
                init = get_repo[1]
                repo = init.get('repo')
                file_contents = get_contents(repo, path)
                for file in file_contents:
                    if not allowed_file(file.path):
                        text =  decode_content(file.content, True)
                        display_content = get_file_contents(text)
                        file_meta = get_article_data(display_content[0])
                        add_image_desc = re.sub('!\[\]\(.', '![](temp/{}'.format(folder_path), display_content[1])
                        markdown = md2.markdown(add_image_desc,  extras=['fenced-code-blocks'])
                        fix_front_quotes = re.sub('<blockquote>\n', '<blockquote>', markdown)
                        fixed_quotes = re.sub('\n</blockquote>\n','</blockquote>', fix_front_quotes)
                        description = re.sub('\n', '<br/>', fixed_quotes)
                    else:
                        file_path = os.path.join(UPLOAD_FOLDER+'/{}'.format(folder_path), file.name)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        # file_path = os.path.join(UPLOAD_FOLDER, file.name)
                        with open(file_path, 'wb') as f:
                            f.write(decode_content(file.content))
                form = CreateForm(data=file_meta)
                return render_template('edit.html', form=form, description=description, path=path)
            else:
                return redirect(url_for('core.'+get_repo[1]))
        else:
            return render_template('edit.html', content=None)
    if request.method == 'POST':
        get_repo = initialize()
        if get_repo[0]:
            init=get_repo[1]
            repo = init.get('repo')
            tree = init.get('tree')
            branch = init.get('branch')
            master_ref =init.get('master_ref')

            form = request.form
            path = form.get('path')
            title_text = form.get('title')
            category_text = form.get('category')
            folder_text = form.get('folder')
            file_path = path.split('/')[-1]
            #get file content
            description = form.get('description')
            is_draft = form.get('draft')


            #find image
            current_image = re.findall('temp/.*?\.[jpg|jpeg|png|gif]+', description)

            previous_image = new_images = remove_images = []
            if current_image:
                try:
                    previous_image = os.listdir(UPLOAD_FOLDER+'/'+file_path)
                except:
                    previous_image = []
                # go thorugh all the image take the list of added and removed images
                new_images = [ image.split('/')[-1] for image in current_image if image.split('/')[-1] not in previous_image]
                remove_images = [image for image in previous_image if 'temp/'+file_path+'/'+image not in current_image]

            #get content current folder
            content_folder = get_content_type(path)

            updated_image = re.sub('\(/temp|temp/[a-z0-9\-]+', '(.', description)

            # recheck the image added to temp folder
            updated_desc = re.sub('\(\(./', '(./', updated_image)

            title = 'title: ' + title_text + '\n'
            category = 'category: '+ category_text + '\n'
            cover  = 'cover: ' + ' ' +'\n'
            author = 'author: ' + 'arunkumar'+'\n'
            folder = 'folder: ' + folder_text + '\n'

            file_meta = '---\n' + title + category + cover + author + folder + '---\n'

            content = file_meta + updated_desc

            #update the file
            current_time = datetime.now().strftime("%d-%b-%Y-%H:%M:%S")
            commit_message = 'Updated {} at {}'.format(file_path, current_time)

            file = repo.get_contents('{}/index.md'.format(path))

            """
             find the content folder location and check for
             saving type(draft or post)

             if draft
               i)  content_folder is draft leave to the flow
               ii) contet_folder is post:
                     update the folder meta_data for content
                     and create new draft content
             if post
               i) content_folder is post leave the flow
               ii) content_folder is draft:
                   check file_meta_data folder
                   folder is empty --> create new content
                   folder is not empty --> update the path leave the flow
            """
            if is_draft and content_folder == 'drafts' or not is_draft and content_folder == 'posts':
                #leave the flow
                if current_image:
                    github_remove_images(remove_images, path, repo)
                    github_upload_images(new_images, UPLOAD_FOLDER, path, repo, tree, branch, master_ref)

            elif is_draft and content_folder == 'posts':
                #Update the folder path and create new draft content
                content = re.sub('folder:', 'folder:{}'.format(path), content )
                # create element tree
                blob = create_git_blob(repo, content, 'utf-8|base64')

                draft_folder = get_post_folder(draft)

                git_dir = file_path

                git_path = draft_folder+ git_dir

                index_element = create_input_git_tree(git_path+'/index.md','100644', 'blob', blob.sha)

                element_tree = [index_element]

                # create git tree
                git_tree= create_git_tree(repo, element_tree, tree)
                #create git commit

                parent = repo.get_git_commit(branch.commit.sha)

                git_commit = create_git_commit(repo, 'new draft post added in {}'.format(git_dir), git_tree, parent)
                #update the head commit
                update_commit(master_ref, git_commit.sha)

                github_upload_images(new_images, UPLOAD_FOLDER, git_path)

                # upload current image
                github_upload_images(previous_image, UPLOAD_FOLDER+'/'+file_path, git_path)
                return redirect('/drafts')

            elif not is_draft and not folder_text:
                #create new post content
                blob = create_git_blob(repo, content, 'utf-8|base64')
                posts_folder = get_post_folder(is_draft)
                git_dir = file_path
                git_path = posts_folder+ git_dir

                index_element = create_input_git_tree(git_path+'/index.md','100644', 'blob', blob.sha)

                element_tree = [index_element]

                # create git tree
                git_tree= create_git_tree(repo, element_tree, tree)
                #create git commit
                parent = repo.get_git_commit(branch.commit.sha)
                git_commit = create_git_commit(repo, 'new draft post added in {}'.format(git_dir), git_tree, parent)
                #update the head commit
                update_commit(master_ref, git_commit.sha)

                github_upload_images(new_images, UPLOAD_FOLDER, path)
                github_upload_images(previous_image, UPLOAD_FOLDER+'/'+file_path, git_path)

                return redirect(root_url)

            elif not is_draft and folder_text:
                #leave the flow and update the path
                import pdb; pdb.set_trace()
                path = folder_text
                file = repo.get_contents('{}/index.md'.format(path))
                # update the folder text to empty
                content = re.sub('folder: [a-z]+/[a-z]+/[a-zA-z0-9\-]+', 'folder:', content)
                github_remove_images(remove_images, path, repo)
                github_upload_images(new_images, UPLOAD_FOLDER, path)

            update_file(repo, path+'/index.md', commit_message, content, file.sha)
            clear_temp_static(True)
            # TODO exception handling and send the form again with data
            return redirect(root_url)
        else:
            return redirect(url_for('core.'+get_repo[1]))

@blueprint.route('/configure', methods=['GET', 'POST'])
@login_required
def configure_github_folders():
    if request.method == 'GET':
        config = get_app_config()
        data = {}
        data['repo'] = config['GITHUB_REPO']
        data['posts_folder'] = config['POSTS_FOLDER']
        data['drafts_folder'] = config['DRAFT_FOLDER']
        form = FolderForm(data = data)
        return render_template('github_folder.html', form = form)
    if request.method == 'POST':
        data = request.form
        repo = data.get('repo')
        post = data.get('posts_folder')
        draft = data.get('drafts_folder')
        config = get_app_config()
        if repo and post and draft:
            config['GITHUB_REPO'] = repo
            config['POSTS_FOLDER'] = post
            config['DRAFT_FOLDER'] = draft
            return redirect('login')
        else:
            return render_template('github_folder.html', context)

@blueprint.route('/uploads', methods=['POST'])
@login_required
def save_image():
    if request.method == 'POST':
        file = request.files.get('image')
        if file and allowed_file(file.filename):
             filename = file.filename
             filename = secure_filename(filename)
             if not os.path.exists(UPLOAD_FOLDER):
                 os.makedirs(UPLOAD_FOLDER)

             file_path = os.path.join(UPLOAD_FOLDER, filename)
             file.save(file_path)
             return jsonify({'data':'/temp/'+filename})
        return jsonify({'data':None})

@blueprint.route('/uploads/<regex("[a-z0-9\-]+"):dir_path>', methods=['POST'])
@login_required
def edit_save_image(dir_path):
    if request.method == 'POST':
        file = request.files.get('image')
        if file and allowed_file(file.filename):
             filename = file.filename
             filename = secure_filename(filename)
             if not os.path.exists(UPLOAD_FOLDER):
                 os.makedirs(UPLOAD_FOLDER)

             file_path = os.path.join(UPLOAD_FOLDER+'/'+dir_path, filename)
             file.save(file_path)
             return jsonify({'data':'/temp/'+dir_path+'/'+filename})
        return jsonify({'data':None})

@blueprint.route('/temp/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@blueprint.route('/temp/<regex("[a-z0-9\-]+"):dir_path>/<filename>')
@login_required
def edit_file(filename, dir_path):
    return send_from_directory(UPLOAD_FOLDER+'/'+dir_path, filename)

@blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(os.getcwd() , 'core/static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
