# Install Stackdriver logging agent
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh

# Install or update needed software
apt-get update
apt-get install -yq git supervisor python3-pip apt-transport-https software-properties-common
#pip install --upgrade pip virtualenv
pip3 --version
pip3 install virtualenv
sudo tee /etc/google-fluentd/config.d/test-unstructured-log.conf <<EOF
<source>
    @type tail
    # Format 'none' indicates the log is unstructured (text).
    format none
    # The path of the log file.
    path /tmp/test-unstructured-log.log
    # The path of the position file that records where in the log file
    # we have processed already. This is useful when the agent
    # restarts.
    pos_file /var/lib/google-fluentd/pos/test-unstructured-log.pos
    read_from_head true
    # The log tag for this log input.
    tag unstructured-log
</source>
EOF
sudo service google-fluentd reload

# Account to own server process
useradd -m -d /home/pythonapp pythonapp

# Fetch source code
export HOME=/root
#git clone https://github.com/GoogleCloudPlatform/getting-started-python.git /opt/app
git clone https://github.com/Jiff21/gce-allure.git /opt/app
git checkout -b feature/log-path origin/feature/log-path

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
