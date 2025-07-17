import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configuración de la base de datos
DB_PATH = os.getenv('DB_PATH', 'dungeon_and_scrum.db')

# API Key de Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCJZfIVlX_5JQrLCGH-Sw_ADBCBvNXOURQ')

# Configuración de las clases del juego
CLASES = {
    'Desarrollador': {
        'sp': 4, 
        'energia': 10, 
        'niveles': ['Junior', 'SemiSenior', 'Senior', 'Arquitecto', 'Terry']
    },
    'Tester': {
        'sp': 2, 
        'energia': 15, 
        'niveles': ['Junior', 'SemiSenior', 'Senior', 'Líder']
    },
    'Diseñador': {
        'sp': 2, 
        'energia': 30, 
        'niveles': ['Junior', 'SemiSenior', 'Senior']
    }
}

# Configuración del servidor Flask
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000 