import re
import os
import sys
from settings import UPLOAD_FOLDER, ROOT_DIR, CLOUD_STORAGE_BUCKET
from base.linux_file_functions import create_local_folder
from base.linux_file_functions import create_report
from base.app_engine_functions import copy_bucket_json_to_local_folders
from base.app_engine_functions import copy_history_json_to_local_folders


def get_existing_buckets(gcs):
    '''Delete a bucket so we can get rid of old projects'''
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob_iter = bucket.list_blobs()
    blobs = []
    project_names = []
    for blob in blob_iter:
        blobs.append(blob)
    sys.stderr.write('Found %i files.' % len(blobs))
    if len(blobs) == 0:
        print('No existing projects', file=sys.stderr)
        sys.stderr.write('No exitsing projects')
    else:
        for blob in blobs:
            files_first_folder = re.match(r".+?(?=\/)", blob.name).group(0)
            if str(files_first_folder) not in project_names:
                project_names.append(str(files_first_folder))
        for project in project_names:
            sys.stderr.write('Projects that exists: %s' % (project))
            folder_path = os.path.join(UPLOAD_FOLDER, project)
            create_local_folder(project, folder_path)
            copy_bucket_json_to_local_folders(gcs, project)
            copy_history_json_to_local_folders(gcs, project)
            create_report(project)
