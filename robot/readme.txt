#CHANGE VARS

nano robot.py
    SERVER_URL = "http://localhost:8000/api/bot"
    SERVER_TOKEN = "auth_token_here"
    RASPBERRY_ID = "raspberry_id_here"
    
#AUTO RUN WITH SUPERVISOR

sudo cp robot.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update

