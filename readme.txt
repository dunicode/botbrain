sudo apt install python3 python3-pip python3-virtualenv supervisor mariadb-server redis -y
sudo pip install virtualenv

sudo mkdir /var/log/celery
sudo cp botbrain.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart botbrain-gunicorn