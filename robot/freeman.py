import requests
import subprocess
import time

SERVER_URL = "http://localhost:8000/api/bot" #https://api.visiportal.com/bot
SERVER_TOKEN = "auth_token_here"
RASPBERRY_ID = "raspberry_id_here"

def check_commands():
    try:
        headers = {"Accept":"application/json", "Authorization": "Token %s" % SERVER_TOKEN}
        response = requests.get(f"{SERVER_URL}/raspberries/{RASPBERRY_ID}/get-command/", headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            command_data = response.json()
            if command_data:
                execute_command(command_data)
    except Exception as e:
        print(f"Error: {e}")

def execute_command(command_data):
    command_id = command_data['id']
    command = command_data['command']
    
    try:
        # Ejecutar comando en el Raspberry
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        success = True
    except subprocess.CalledProcessError as e:
        result = e.output
        success = False
    
    # Enviar resultado al servidor
    headers = {"Accept":"application/json", "Authorization": "Token %s" % SERVER_TOKEN}
    response = requests.post(f"{SERVER_URL}/raspberries/{RASPBERRY_ID}/ack-command/", headers=headers, json={
        "command_id": command_id,
        "result": result
    })
    print(f"Command ID {command_id} executed. Success: {success}. Server response: {response.status_code}")

if __name__ == "__main__":
    while True:
        check_commands()
        time.sleep(10)  # Consultar cada 10 segundos