import os
import sys
import re
from flask import flash, request, redirect, render_template
from google.cloud import storage
from settings import UPLOAD_FOLDER, ROOT_DIR, CLOUD_STORAGE_BUCKET


def copy_bucket_json_to_local_folders(gcs, folder_name):
    '''Copy Cloud Storage Json to Linux for report generation'''
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    prefix = folder_name + '/json/'
    blob_iter = bucket.list_blobs(prefix=prefix, delimiter='/')
    blobs = []
    for blob in blob_iter:
        blobs.append(blob)
    sys.stdout.write('Copying %i bucket files to server' % len(blobs))
    if len(blobs) == 0:
        flash('Json Results Folder doesn\'t exists in GCS')
        return redirect(request.url)
    else:
        for blob in blobs:
            new_file_path = os.path.join(UPLOAD_FOLDER, blob.name)
            sys.stderr.write('Writing file to %s\n' % str(new_file_path))
            blob.download_to_filename(new_file_path)


def copy_history_json_to_local_folders(gcs, folder_name):
    '''Copy Cloud Storage History Files to Linux for report generation'''
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    prefix = folder_name + '/report/history/'
    blob_iter = bucket.list_blobs(prefix=prefix, delimiter='/')
    blobs = []
    for blob in blob_iter:
        blobs.append(blob)
    sys.stdout.write('Found %i History Files' % len(blobs))
    if len(blobs) == 0:
        flash('History Folder doesn\'t exists in GCS')
        return redirect(request.url)
    else:
        for blob in blobs:
            new_file_path = os.path.join(UPLOAD_FOLDER, blob.name)
            history_path = re.search(
                r".+?(?=\/).+?(?=\/).+?(?=\/).+?(?=\/).+?(?=\/)",
                new_file_path
            ).group()
            if os.path.isdir(history_path) is False:
                print('Creating History Folder at %s' % history_path,
                      file=sys.stdout
                      )
                os.makedirs(history_path)
            sys.stderr.write('Writing file to %s\n' % str(new_file_path))
            blob.download_to_filename(new_file_path)


def copy_history_to_storage(gcs, folder_name):
    '''Copy the History Folders for a report to Cloud Console'''
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    history_folder_path = os.path.join(
        UPLOAD_FOLDER,
        folder_name,
        'report',
        'history'
    )
    local_history_files = os.listdir(history_folder_path)
    if local_history_files == 0:
        print('No History Found', file=sys.stdout)
        flash('No History Found')
    else:
        for file in local_history_files:
            cloud_storage_path = os.path.join(
                folder_name,
                'report',
                'history',
                file
            )
            print('Uploading History File %s to bucket: %s\n' % (
                os.path.join(file, cloud_storage_path),
                cloud_storage_path),
                file=sys.stdout)
            local_file = open(os.path.join(history_folder_path, file), 'rb')
            blob = bucket.blob(cloud_storage_path)
            blob.upload_from_file(local_file)
            print(blob.public_url, file=sys.stdout)
            flash(blob.public_url)


def app_engine_file_uploader(gcs, project_name, filename, file):
    '''Store Allure Results Files in Cloud Storage'''
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    file_path = os.path.join(project_name, 'json', filename)
    blob = bucket.blob(file_path)
    print('Uploading %s to bucket: %s' % (
        str(filename),
        str(project_name)
        ), file=sys.stdout)
    blob.upload_from_file(file)
    print(blob.public_url, file=sys.stdout)
    flash(blob.public_url)


def delete_app_engine_bucket(gcs, folder_name):
    '''Delete a bucket so we can get rid of old projects'''
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    prefix = folder_name + '/'
    blob_iter = bucket.list_blobs(prefix=prefix)
    blobs = []
    for blob in blob_iter:
        blobs.append(blob)
    sys.stdout.write('Deleting %i bucket files.' % len(blobs))
    if len(blobs) == 0:
        flash('Folder doesn\'t exists')
        return redirect(request.url)
    else:
        for blob in blobs:
            sys.stderr.write('Deleting blob: %s' % (blob.name))
            blob.delete()
