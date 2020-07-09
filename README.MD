# Allure Hub on gce

## Setup

```
cp secrets/example.env.example secrets/dev.env
```

Edit variables appropriately, then run deploy script to create compute engine
instance and necessary firewall rules

```
source dev.env
cd allure-report
bash deploy.sh
```


While Debugging should just be
```
source secrets/dev.env
INSTANCE_NAME=ce-test-[Increment]
gcloud compute --project=$PROJECT_ID instances create $INSTANCE_NAME \
    --image=ubuntu-1604-xenial-v20200429 \
    --image-project=ubuntu-os-cloud \
    --machine-type=f1-micro \
    --no-boot-disk-auto-delete \
    --scopes userinfo-email,cloud-platform \
    --metadata-from-file startup-script=startup-script.sh \
    --zone $ZONE \
    --tags http-server,https-server
```


TODO
Fix https
Fix Main.py
Test app.yaml disk options
Update project to use env name instead of a project folder

#### Scrath Notes

```
virtualenv -p python3 lib
source /lib/bin/activate
pip3 install -r scripts/requirements.txt
dev_appserver.py /Users/jeff/Documents/Code/allure_hub_gcp/app.yaml

```
https://cloud.google.com/appengine/docs/standard/python3/tools/local-devserver-command





```
gcloud compute firewall-rules create default-allow-https-8080     --allow tcp:8080     --source-ranges 0.0.0.0/0     --target-tags http-servers     --description "Allow port 8080 access to https-server"
```

 Then label server "allow-8080" &
https://35.222.53.13:8080
