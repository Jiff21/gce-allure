import os
import shutil
import subprocess
import sys
from flask import flash, request, redirect, render_template
from settings import UPLOAD_FOLDER, ROOT_DIR
from settings import log

def create_local_folder(folder_name, folder_path):
    '''Create project folders and message where it can be found.
    os.makedirs(folder_path)'''
    if os.path.isdir(folder_path):
        flash('Folder already exists on linux host.')
        return redirect(request.url)
    else:
        # Create project folders and message where it can be found.
        # os.makedirs(folder_path)
        os.makedirs(os.path.join(folder_path, 'json'))
        os.makedirs(os.path.join(folder_path, 'report'))
        flash('Project created at ' + os.path.join(
            request.host,
            'projects',
            folder_name
        ) + '/')


def delete_local_folder(folder_name, folder_path):
    '''Delete the folders for a project on the Docker Image'''
    if os.path.isdir(folder_path) is False:
        flash('Folder Doesn\'t exists on linux host')
        return redirect(request.url)
    else:
        # Create project folders and message where it can be found.
        shutil.rmtree(folder_path)
        flash('Project deleted at ' + os.path.join(
            request.host,
            'projects',
            folder_name
        ) + '/')


def delete_json_folder_content(path):
    '''Clear out a Results folde rto copy in newer json'''
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def local_file_uploader(project_name, filename, file):
    '''Create local json files on linux'''
    sub_path = os.path.join(project_name, 'json', filename)
    if os.path.isdir(os.path.join(
        UPLOAD_FOLDER,
        project_name
    )) is False:
        flash(
            '''Project does not exist locally. Please check project has been
             created and you have typed correct name.'''
        )
        return render_template('upload_file.html')
    log.debug('Adding files to %s' % os.path.join(
        UPLOAD_FOLDER,
        sub_path)
    )
    file.save(os.path.join(UPLOAD_FOLDER, sub_path))
    flash('File created at: ' + os.path.join(
        request.host,
        'projects',
        sub_path
    ))


def create_report(folder_name):
    '''Generate report by copying history folder from previous report
    and json on local linux host'''
    report_history_path = os.path.join(
        UPLOAD_FOLDER,
        folder_name,
        'report',
        'history'
    )
    results_history = os.path.join(
        UPLOAD_FOLDER,
        folder_name,
        'json',
        'history'
    )
    if os.path.isdir(report_history_path):
        log.info('Copying History to Results File.', file=sys.stdout)
        print('Copying History to Results File.', file=sys.stdout)
        # cp - R report_history_path results_history
        generated_command = 'cp -R %s %s' % (
            report_history_path,
            results_history
            )
        log.info('Copying History to Results File. With Command:\n%s'
              % generated_command
        )
        process = subprocess.Popen(
            generated_command,
            stderr=subprocess.STDOUT,
            shell=True
            )
        process.wait()
    else:
        log.info('No history to copy')
    # Create Report from current json and history
    results_path = os.path.join(
        UPLOAD_FOLDER,
        folder_name,
        'json'
    )
    report_path = os.path.join(
        UPLOAD_FOLDER,
        folder_name,
        'report'
    )
    generated_command = 'allure generate %s -o %s --clean' % (
                results_path,
                report_path
    )
    log.info('Time to create a report with command:\n%s'
          % generated_command
    )
    try:
        process = subprocess.Popen(
            generated_command,
            stderr=subprocess.STDOUT,
            shell=True
        )
        process.wait()
    except Exception:
        log.error("Fatal error in main loop", exc_info=True)
    flash('Report Created at ' + os.path.join(
        request.host,
        'projects',
        folder_name
    ) + '/report/index.html')


def write_files_locally(project_name, filename, file):
    sub_path = os.path.join(project_name, 'json', filename)
    if os.path.isdir(os.path.join(
        UPLOAD_FOLDER,
        project_name
    )) is False:
        flash(
            '''Project does not exist locally. Please check project has been
             created and you have typed correct name.'''
        )
        return render_template('upload_file.html')
    log.info('Adding files to %s' %
          os.path.join(UPLOAD_FOLDER, sub_path)
    )
    file.save(os.path.join(UPLOAD_FOLDER, sub_path))
    flash('File created at: ' + os.path.join(
        request.host,
        'projects',
        sub_path
    ))
