import os
import jinja2
import logging
import sys
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import send_from_directory, session, send_file
from base.app_engine_functions import app_engine_file_uploader
from base.app_engine_functions import delete_app_engine_bucket
from base.app_engine_functions import copy_bucket_json_to_local_folders
from base.app_engine_functions import copy_history_to_storage
from base.linux_file_functions import create_local_folder, delete_local_folder
from base.linux_file_functions import delete_json_folder_content
from base.linux_file_functions import create_report, local_file_uploader
from base.first_run import get_existing_buckets
from google.cloud import error_reporting
from google.cloud import storage
import google.cloud.logging
from settings import  CLOUD_STORAGE_BUCKET, FLASK_SECRET
from settings import UPLOAD_FOLDER, ROOT_DIR
from settings import log
from werkzeug.utils import secure_filename

# False writes to local storage.
IS_APPENGINE = os.environ.get('IS_APPENGINE', False)
ALLOWED_EXTENSIONS = set(['json', 'properties'])


# Create a projects folder
# REplace with UPLOAD_FOLDER?
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
app.jinja_loader = jinja2.FileSystemLoader(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'html'
))


app.secret_key = FLASK_SECRET

# app.testing = True
# # Configure logging
# if app.testing:
#     log_format = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
#     logging.basicConfig(
#         format=log_format,
#         filename='/tmp/test-unstructured-log.log',
#         level=os.environ.get('LOG_LEVEL', 'INFO')
#     )
#     client = google.cloud.logging.Client()
#     client.get_default_handler()
#     client.setup_logging()
#     log = logging.getLogger('Allure-Hub')
#     log.info('Logging setup in SEARCHFORTHIS1')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_first_request
def before_first_request():
    if IS_APPENGINE == 'True':
        gcs = storage.Client()
        get_existing_buckets(gcs)


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
    log.info('Getting index SEARCHFORTHIS2')
    return render_template(
        'index.html',
        current_projects=get_projects(
            app.config['UPLOAD_FOLDER']
        )
    )


@app.route('/qa_admin', methods=['GET'])
def qa_admin():
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
            if IS_APPENGINE == 'True':
                gcs = storage.Client()
                app_engine_file_uploader(gcs, project_name, filename, file)
            else:
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
            # No need to create folder on App Engine
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
            # Make sure folder doesn't already exist
            if IS_APPENGINE == 'True':
                gcs = storage.Client()
                delete_app_engine_bucket(gcs, folder_name)
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
                # Need to add app engine Logic
                if IS_APPENGINE == 'True':
                    # Delete pre-existing folder content
                    log.info('Deleting old files at %s' %
                          str(os.path.join(folder_path, 'json'))
                          )
                    delete_json_folder_content(
                        os.path.join(folder_path, 'json')
                    )
                    # Then Copy the JSON IN Bucket:
                    gcs = storage.Client()
                    copy_bucket_json_to_local_folders(gcs, folder_name)
                create_report(folder_name)
                if IS_APPENGINE == 'True':
                    copy_history_to_storage(gcs, folder_name)
            return render_template('build_report.html')
    return render_template('build_report.html')


@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')


# Add an error handler that reports exceptions to Stackdriver Error
# Reporting. Note that this error handler is only used when debug
# is False
@app.errorhandler(500)
def server_error(e):
    client = error_reporting.Client()
    client.report_exception(
        http_context=error_reporting.build_flask_context(request))
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

# @app.errorhandler(500)
# def server_error(e):
#     logging.exception('An error occurred during a request.')
#     return """
#     An internal error occurred: <pre>{}</pre>
#     See logs for full stacktrace.
#     """.format(e), 500


if __name__ == '__main__':
    app.run()
    # Suggested for logging from
    # https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
    # only keep if I need that logging.
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
