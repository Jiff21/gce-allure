import os
import jinja2
import logging
import sys
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import send_from_directory, session, send_file
from base.linux_file_functions import create_local_folder, delete_local_folder
from base.linux_file_functions import delete_json_folder_content
from base.linux_file_functions import create_report, local_file_uploader
from google.cloud import error_reporting
from google.cloud import storage
from settings import FLASK_SECRET
from settings import UPLOAD_FOLDER, ROOT_DIR, _ENV
from werkzeug.utils import secure_filename


# False writes to local storage.
ALLOWED_EXTENSIONS = set(['json', 'properties'])


log = logging.getLogger('Allure-Hub')
log.info('Logging setup in SEARCHFORTHIS1')


# Create a projects folder
# Replace with UPLOAD_FOLDER?
if os.path.isdir(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'projects'
)) is False:
    log.info(
        'Creating Projects Folder at %s' % UPLOAD_FOLDER
    )
    os.makedirs(os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'projects'
    ))


def get_projects(path):
    current_projects = []
    files = os.listdir(os.path.join(os.path.abspath(
        os.path.dirname(__file__)),
        'projects/'))
    for file in files:
        if os.path.isdir(os.path.join(os.path.abspath(
                os.path.dirname(__file__)),
                'projects',
                file
        )):
            if os.path.isdir(os.path.join(os.path.abspath(
                    os.path.dirname(__file__)),
                    'projects',
                    file,
                    'reports'
            )):
                flash("The project %s has been created but has no reports")
            else:
                current_projects.append(file)
    return current_projects


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PROPAGATE_EXCEPTIONS'] = True
app.jinja_loader = jinja2.FileSystemLoader(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'html'
))


app.secret_key = FLASK_SECRET

if 'prod' not in _ENV:
    app.testing = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(
            ROOT_DIR,
            'static'
        ),
        'favicon.ico', mimetype='image/gif'
    )


@app.route('/', methods=['GET'])
def index():
    log.info('Running app.route for index')
    return render_template(
        'index.html',
        current_projects=get_projects(
            app.config['UPLOAD_FOLDER']
        )
    )


@app.route('/qa_admin', methods=['GET'])
def qa_admin():
    log.info('Running app.route for qa_admin')
    return render_template(
        'qa_admin.html',
        current_projects=get_projects(
            app.config['UPLOAD_FOLDER']
        )
    )


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    # Add this to save path, and add return directory as well.
    log.info('Upload File')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file in request')
            return render_template('upload_file.html')
        file = request.files['file']
        sys.stderr.write(str(type(file)))
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template('upload_file.html')
        # Project name is mandatory
        if request.form['project'] == '':
            flash('You did not provide a project name')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # create json file and message where it can be found
            project_name = request.form['project'].lower()
            filename = secure_filename(file.filename)
            local_file_uploader(project_name, filename, file)
            return render_template('upload_file.html')
    return render_template('upload_file.html')


@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    '''data must include project_name'''
    if request.method == 'POST':
        # 2 checks to see if folder name was sent
        if '' not in request.form['project']:
            flash('No project_name part')
            return render_template('create_project.html')
        if request.form['project'] == '':
            flash('Project name must be null')
            return render_template('create_project.html')
        else:
            folder_name = secure_filename(request.form['project']).lower()
            folder_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                folder_name
            )
            create_local_folder(folder_name, folder_path)
            return render_template('create_project.html')
    return render_template('create_project.html')


@app.route('/delete_project', methods=['GET', 'POST'])
def delete_project():
    '''data must include project_name'''
    if request.method == 'POST':
        # 2 checks to see if folder name was sent
        if '' not in request.form['project']:
            flash('No project_name part')
            return render_template('delete_project.html')
        if request.form['project'] == '':
            flash('Project name must be null')
            return render_template('delete_project.html')
        else:
            folder_name = secure_filename(request.form['project']).lower()
            folder_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                folder_name
            )
            delete_local_folder(folder_name, folder_path)
            return render_template('delete_project.html')
    return render_template('delete_project.html')


# Serves all files for the allure report
@app.route('/<path:req_path>')
def dir_listing(req_path):
    # Joining the base and the requested path
    abs_path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)),
        req_path
    )
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        flash('404, redirected to the homepage')
        return render_template(
            'index.html',
            current_projects=get_projects(app.config['UPLOAD_FOLDER'])
        )
    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)
    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('file_list.html', files=files)


@app.route('/build_report', methods=['GET', 'POST'])
def build_report():
    if request.method == 'POST':
        # 2 checks to see if folder name was sent
        if '' not in request.form['project']:
            flash('No project_name part')
            return render_template('build_report.html')
        if request.form['project'] == '':
            flash('Project name must be null')
            return render_template('build_report.html')
        else:
            folder_name = secure_filename(request.form['project']).lower()
            folder_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                folder_name
            )
            # Make sure folder doesn't already exist
            if os.path.isdir(folder_path) is False:
                flash('Local Folder does not exist')
                return render_template('build_report.html')
            else:
                create_report(folder_name)
            return render_template('build_report.html')
    return render_template('build_report.html')


@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')


@app.errorhandler(500)
def server_error(e):
    client = error_reporting.Client()
    client.report_exception(
        http_context=error_reporting.build_flask_context(request))
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
