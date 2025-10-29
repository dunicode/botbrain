#!/usr/bin/env python3
import requests
import subprocess
import time
import logging
import os
from typing import Dict, Any

class Bot:
    def __init__(self, server_url: str, token: str, raspberry_id: str):
        self.SERVER_URL = server_url
        self.SERVER_TOKEN = token
        self.RASPBERRY_ID = raspberry_id
        self._setup_logging()
        
        # Diccionario que mapea nombres de comandos a métodos
        self.commands = {
            "limpiar_imagenes": self.limpiar_imagenes,
            "estado_sistema": self.estado_sistema,
            "reiniciar_servicios": self.reiniciar_servicios,
            "crear_respaldo": self.crear_respaldo,
            # Añade más comandos aquí
        }

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json", 
            "Authorization": f"Token {self.SERVER_TOKEN}"
        }

    def check_commands(self) -> None:
        """Consulta el servidor por comandos pendientes"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.SERVER_URL}/raspberries/{self.RASPBERRY_ID}/get-command/", 
                headers=headers
            )
            
            self.logger.info(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                command_data = response.json()
                if command_data:
                    self.execute_command(command_data)
            elif response.status_code != 200:
                self.logger.warning(f"Respuesta inesperada: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error checking commands: {e}")

    def execute_command(self, command_data: Dict[str, Any]) -> None:
        """Ejecuta un comando recibido del servidor"""
        command_id = command_data['id']
        command_name = command_data['command']
        
        self.logger.info(f"Ejecutando comando ID {command_id}: {command_name}")
        
        if command_name in self.commands:
            try:
                result = self.commands[command_name]()
                success = True
                self.logger.info(f"Comando {command_id} ejecutado exitosamente")
            except Exception as e:
                result = f"Error ejecutando comando: {str(e)}"
                success = False
                self.logger.error(f"Error ejecutando comando {command_id}: {str(e)}")
        else:
            result = f"Comando no reconocido: {command_name}"
            success = False
            self.logger.warning(f"Comando no reconocido: {command_name}")
        
        self._send_command_result(command_id, result, success)

    def _send_command_result(self, command_id: str, result: str, success: bool) -> None:
        """Envía el resultado del comando al servidor"""
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.SERVER_URL}/raspberries/{self.RASPBERRY_ID}/ack-command/", 
                headers=headers, 
                json={
                    "command_id": command_id,
                    "result": result
                }
            )
            
            log_message = f"Command ID {command_id} executed. Success: {success}. Server response: {response.status_code}"
            
            if response.status_code == 200:
                self.logger.info(log_message)
            else:
                self.logger.warning(log_message)
                
        except Exception as e:
            self.logger.error(f"Error enviando resultado del comando {command_id}: {e}")

    def run(self) -> None:
        """Bucle principal del bot"""
        self.logger.info(f"Iniciando bot para Raspberry ID: {self.RASPBERRY_ID}")
        self.logger.info(f"Conectando a servidor: {self.SERVER_URL}")
        self.logger.info(f"Comandos disponibles: {', '.join(self.commands.keys())}")
        
        while True:
            self.check_commands()
            time.sleep(10)  # Consultar cada 10 segundos

    # =============================================================================
    # MÉTODOS DE COMANDOS - AÑADE TUS PROPIOS COMANDOS AQUÍ
    # =============================================================================
    
    def limpiar_imagenes(self) -> str:
        """Limpia las imágenes en una carpeta específica"""
        try:
            # Define la carpeta que quieres limpiar
            carpeta_imagenes = "/tmp/imagenes"  # Cambia por tu ruta
            
            if not os.path.exists(carpeta_imagenes):
                return f"La carpeta {carpeta_imagenes} no existe"
            
            # Contar archivos antes de borrar
            archivos = [f for f in os.listdir(carpeta_imagenes) 
                       if os.path.isfile(os.path.join(carpeta_imagenes, f))]
            count = len(archivos)
            
            # Borrar todos los archivos
            for archivo in archivos:
                os.remove(os.path.join(carpeta_imagenes, archivo))
            
            return f"Se eliminaron {count} archivos de {carpeta_imagenes}"
            
        except Exception as e:
            return f"Error limpiando imágenes: {str(e)}"

    def estado_sistema(self) -> str:
        """Obtiene el estado del sistema"""
        try:
            # Información de memoria
            memoria = subprocess.check_output("free -h", shell=True, text=True).strip()
            
            # Espacio en disco
            disco = subprocess.check_output("df -h /", shell=True, text=True).strip()
            
            # Uptime
            uptime = subprocess.check_output("uptime", shell=True, text=True).strip()
            
            # Temperatura (solo Raspberry Pi)
            try:
                temperatura = subprocess.check_output("vcgencmd measure_temp", shell=True, text=True).strip()
            except:
                temperatura = "Temperatura no disponible"
            
            return f"""Estado del sistema:
            
                Memoria:
                {memoria}

                Disco:
                {disco}

                Uptime:
                {uptime}

                Temperatura:
                {temperatura}"""
            
        except Exception as e:
            return f"Error obteniendo estado del sistema: {str(e)}"

    def reiniciar_servicios(self) -> str:
        """Reinicia servicios específicos"""
        try:
            servicios = ["nginx", "ssh"]  # Cambia por los servicios que necesites
            
            resultados = []
            for servicio in servicios:
                try:
                    resultado = subprocess.check_output(
                        f"sudo systemctl restart {servicio}", 
                        shell=True, 
                        text=True,
                        stderr=subprocess.STDOUT
                    )
                    resultados.append(f"Servicio {servicio}: reiniciado correctamente")
                except subprocess.CalledProcessError as e:
                    resultados.append(f"Servicio {servicio}: error - {e.output}")
            
            return "\n".join(resultados)
            
        except Exception as e:
            return f"Error reiniciando servicios: {str(e)}"

    def crear_respaldo(self) -> str:
        """Crea un respaldo de una carpeta específica"""
        try:
            carpeta_origen = "/home/pi/datos"  # Cambia por tu carpeta
            carpeta_respaldo = "/home/pi/backups"
            
            if not os.path.exists(carpeta_respaldo):
                os.makedirs(carpeta_respaldo)
            
            # Crear nombre de archivo con fecha
            from datetime import datetime
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_respaldo = f"{carpeta_respaldo}/respaldo_{fecha}.tar.gz"
            
            # Crear respaldo comprimido
            subprocess.check_output(
                f"tar -czf {archivo_respaldo} {carpeta_origen}", 
                shell=True,
                stderr=subprocess.STDOUT
            )
            
            return f"Respaldo creado: {archivo_respaldo}"
            
        except Exception as e:
            return f"Error creando respaldo: {str(e)}"


# =============================================================================
# INICIALIZACION
# =============================================================================
SERVER_URL = "http://localhost:8000/api/bot"
SERVER_TOKEN = "auth_token_here"
RASPBERRY_ID = "raspberry_id_here"
# =============================================================================

if __name__ == "__main__":
    # Crear instancia del bot con la configuración
    bot = Bot(
        server_url=SERVER_URL,
        token=SERVER_TOKEN,
        raspberry_id=RASPBERRY_ID
    )
    
    # Ejecutar el bot
    bot.run()