

```
cp secrets/example.env.example secrets/dev.env
```

Edit variables

```
cd gce
bash deploy.sh
```






TODO
Fix https
Fix Main.py
Test app.yaml disk options
Update project to use env name instead of a project folder



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
