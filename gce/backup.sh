#!/bin/bash
screen -r mcs -X stuff '/save-all\n/save-off\n'
/usr/bin/gsutil cp -R ${BASH_SOURCE%/*}/world gs://${YOUR_BUCKET_NAME}-results-bu/$(date "+%Y%m%d-%H%M%S")-history
screen -r mcs -X stuff '/save-on\n'


## Needs cron job to execute
