sudo tee /etc/google-fluentd/config.d/test-unstructured-log.conf <<EOF
<source>
    @type tail
    # Format 'none' indicates the log is unstructured (text).
    format none
    # The path of the log file.
    path /tmp/gunicorn.error.log, /tmp/test-unstructured-log.log
    # The path of the position file that records where in the log file
    # we have processed already. This is useful when the agent
    # restarts.
    pos_file /var/lib/google-fluentd/pos/test-unstructured-log.pos
    read_from_head true
    # The log tag for this log input.
    tag unstructured-log
</source>
EOF
# Install Stackdriver logging agent
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh

# Install or update needed software
apt-get update
apt-get install -yq git supervisor python3-pip apt-transport-https software-properties-common
pip3 --version
pip3 install virtualenv

# Install Java & Allure
sudo apt-add-repository ppa:qameta/allure -y
sudo add-apt-repository ppa:linuxuprising/java -y
echo debconf shared/accepted-oracle-license-v1-2 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-2 seen true | sudo debconf-set-selections
sudo apt update -y
sudo apt install oracle-java14-installer -y
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
sudo apt-get update -y && sudo apt-get install allure  -y
echo "Allure version is $(allure --version)"


# Maybe default shell will help Python
sudo useradd -D -s /bin/bash
# Account to own server process
useradd -m -d /home/pythonapp -s /bin/bash  pythonapp
# Set any extra path here.
export PATH="$PATH:/usr/bin/env"  >> /home/pythonapp/.bashrc
export PYTHONPATH="$PATH"  >> /home/pythonapp/.bashrc
source  /home/pythonapp/.bashrc
echo "$PYTHONPATH"
# Check shell
# sudo useradd -D | grep -i shell

# Fetch source code
export HOME=/home/pythonapp
cd /home/pythonapp

git clone https://github.com/Jiff21/gce-allure.git /home/pythonapp/app
cd /home/pythonapp/app
git checkout -b feature/log-path origin/feature/log-path

# Set ownership to newly created account
chown -R pythonapp:pythonapp /home/pythonapp/app/
#Debugging
# sudo chown -R jeff:jeff /home/pythonapp/app

# Python environment setup
virtualenv -p python3 /home/pythonapp/app/gce/env
source /home/pythonapp/app/gce/env/bin/activate
pip3 install -r /home/pythonapp/app/gce/requirements.txt
# Sym Link Idea not working but maybe a pathing issue
# ln -s /usr/bin/allure /home/pythonapp/app/gce/env/bin/allure

echo "Allure version $(allure --version)"
# export PYTHONPATH="/home/pythonapp/app/gce:$PYTHONPATH"
# echo "export PATH='/usr/bin:/env/bin:/home/pythonapp/app/gce:$PATH'" >> /etc/profile

# Put supervisor configuration in proper place
cp /home/pythonapp/app/gce/python-app.conf /etc/supervisor/conf.d/python-app.conf

# Start service via supervisorctl
supervisorctl reread
supervisorctl update
