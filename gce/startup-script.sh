# Install Stackdriver logging agent
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh


# Install or update needed software
apt-get update
apt-get install -yq git supervisor python3-pip apt-transport-https software-properties-common google-fluentd=1.6.35-1 google-fluentd-catch-all-config
#pip install --upgrade pip virtualenv
sudo service google-fluentd start
pip3 --version
pip3 install virtualenv

echo $'export http_proxy="http://0.0.0.0:8080"\nexport https_proxy="http://0.0.0.0:8080"\nexport no_proxy=169.254.169.254  # Skip proxy for the local Metadata Server.' >  /etc/default/google-fluentd

# Account to own server process
useradd -m -d /home/pythonapp pythonapp

# Fetch source code
export HOME=/root
#git clone https://github.com/GoogleCloudPlatform/getting-started-python.git /opt/app
git clone https://github.com/Jiff21/gce-allure.git /opt/app
git checkout -b scratch origin/scratch

# Python environment setup
virtualenv -p python3 /opt/app/gce/env
source /opt/app/gce/env/bin/activate
/opt/app/gce/env/bin/pip install -r /opt/app/gce/requirements.txt

# Set ownership to newly created account
chown -R pythonapp:pythonapp /opt/app

# Put supervisor configuration in proper place
cp /opt/app/gce/python-app.conf /etc/supervisor/conf.d/python-app.conf

# Start service via supervisorctl
supervisorctl reread
supervisorctl update
