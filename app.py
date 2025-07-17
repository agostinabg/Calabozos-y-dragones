from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import uuid
import json
import requests
from datetime import datetime
import config
import os

app = Flask(__name__)
CORS(app)

def init_db():
    """Inicializar la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de partidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidas (
            token TEXT PRIMARY KEY,
            creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de jugadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            clase TEXT NOT NULL,
            nivel TEXT DEFAULT 'Junior',
            energia INTEGER,
            sp INTEGER,
            experiencia INTEGER DEFAULT 0,
            partida_token TEXT,
            FOREIGN KEY (partida_token) REFERENCES partidas (token)
        )
    ''')
    
    # Tabla de mensajes del chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden INTEGER NOT NULL,
            autor TEXT NOT NULL,
            texto TEXT NOT NULL,
            partida_token TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partida_token) REFERENCES partidas (token)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def call_gemini_api(context, player_message):
    """Llamar a la API de Gemini para obtener respuesta del Dungeon Master"""
    if not config.GEMINI_API_KEY:
        return "Error: No se ha configurado la API key de Gemini"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Construir el prompt para el Dungeon Master
    prompt = f"""
    Eres el Dungeon Master de un juego de rol llamado "Dungeon and Scrum" donde los jugadores son roles de metodologías ágiles.
    
    Contexto del juego:
    {context}
    
    Último mensaje del jugador: {player_message}
    
    Responde como Dungeon Master, creando una narrativa creativa y contextual basada en la acción del jugador.
    Mantén un tono divertido y relacionado con el mundo del desarrollo de software y metodologías ágiles.
    Tu respuesta debe ser de 2-4 oraciones máximo.
    """
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        response = requests.post(
            f"{url}?key={config.GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "El Dungeon Master está pensando..."
        else:
            return f"Error en la API de Gemini: {response.status_code}"
            
    except Exception as e:
        return f"Error al comunicarse con Gemini: {str(e)}"

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/check-config')
def check_config():
    """Verificar si la configuración está completa"""
    db_exists = os.path.exists(config.DB_PATH)
    has_api_key = bool(config.GEMINI_API_KEY)
    
    return jsonify({
        'db_exists': db_exists,
        'has_api_key': has_api_key,
        'config_complete': db_exists and has_api_key
    })

@app.route('/setup-config', methods=['POST'])
def setup_config():
    """Configurar la aplicación inicialmente"""
    try:
        data = request.json
        db_path = data.get('db_path', 'dungeon_and_scrum.db')
        api_key = data.get('api_key', '')
        
        # Actualizar configuración
        config.DB_PATH = db_path
        config.GEMINI_API_KEY = api_key
        
        # Crear archivo .env
        with open('.env', 'w') as f:
            f.write(f'DB_PATH={db_path}\n')
            f.write(f'GEMINI_API_KEY={api_key}\n')
        
        # Inicializar base de datos
        init_db()
        
        return jsonify({'success': True, 'message': 'Configuración completada'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/crear', methods=['POST'])
def crear_partida():
    """Crear una nueva partida"""
    try:
        data = request.json
        nombre = data.get('nombre')
        clase = data.get('clase')
        
        if not nombre or not clase:
            return jsonify({'error': 'Nombre y clase son requeridos'}), 400
        
        if clase not in config.CLASES:
            return jsonify({'error': 'Clase no válida'}), 400
        
        # Generar token único
        token = str(uuid.uuid4())[:8]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear partida
        cursor.execute('INSERT INTO partidas (token) VALUES (?)', (token,))
        
        # Crear jugador
        clase_config = config.CLASES[clase]
        cursor.execute('''
            INSERT INTO jugadores (nombre, clase, nivel, energia, sp, experiencia, partida_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, clase, 'Junior', clase_config['energia'], clase_config['sp'], 0, token))
        
        # Agregar mensaje inicial del Dungeon Master
        cursor.execute('''
            INSERT INTO mensajes (orden, autor, texto, partida_token)
            VALUES (?, ?, ?, ?)
        ''', (1, 'IA', '¡Bienvenidos a Dungeon and Scrum! El equipo ágil se encuentra en la entrada de la oficina digital. ¿Qué harán primero?', token))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'token': token,
            'mensaje': 'Partida creada con éxito',
            'jugador': {
                'nombre': nombre,
                'clase': clase
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/unirse', methods=['POST'])
def unirse_partida():
    """Unirse a una partida existente"""
    try:
        data = request.json
        nombre = data.get('nombre')
        clase = data.get('clase')
        partida = data.get('partida')
        
        if not nombre or not clase or not partida:
            return jsonify({'error': 'Nombre, clase y partida son requeridos'}), 400
        
        if clase not in config.CLASES:
            return jsonify({'error': 'Clase no válida'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la partida existe
        cursor.execute('SELECT token FROM partidas WHERE token = ?', (partida,))
        if not cursor.fetchone():
            return jsonify({'error': 'Partida no encontrada'}), 404
        
        # Verificar que el nombre no esté duplicado
        cursor.execute('SELECT nombre FROM jugadores WHERE partida_token = ? AND nombre = ?', (partida, nombre))
        if cursor.fetchone():
            return jsonify({'error': 'Ya existe un jugador con ese nombre en la partida'}), 400
        
        # Agregar jugador
        clase_config = config.CLASES[clase]
        cursor.execute('''
            INSERT INTO jugadores (nombre, clase, nivel, energia, sp, experiencia, partida_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, clase, 'Junior', clase_config['energia'], clase_config['sp'], 0, partida))
        
        # Agregar mensaje de bienvenida
        cursor.execute('SELECT MAX(orden) FROM mensajes WHERE partida_token = ?', (partida,))
        max_orden = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            INSERT INTO mensajes (orden, autor, texto, partida_token)
            VALUES (?, ?, ?, ?)
        ''', (max_orden + 1, 'IA', f'¡{nombre} se ha unido a la aventura!', partida))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'token': partida,
            'mensaje': 'Unido con éxito',
            'jugador': {
                'nombre': nombre,
                'clase': clase
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/estado', methods=['POST'])
def obtener_estado():
    """Obtener estado de los jugadores en una partida"""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token es requerido'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nombre, clase, nivel, energia, sp, experiencia
            FROM jugadores
            WHERE partida_token = ?
        ''', (token,))
        
        jugadores = []
        for row in cursor.fetchall():
            jugadores.append({
                'nombre': row['nombre'],
                'clase': row['clase'],
                'nivel': row['nivel'],
                'energia': row['energia'],
                'sp': row['sp'],
                'experiencia': row['experiencia']
            })
        
        conn.close()
        
        return jsonify({'jugadores': jugadores})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def obtener_chat():
    """Obtener historial de mensajes del chat"""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token es requerido'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT orden, autor, texto
            FROM mensajes
            WHERE partida_token = ?
            ORDER BY orden
        ''', (token,))
        
        mensajes = []
        for row in cursor.fetchall():
            mensajes.append({
                'orden': row['orden'],
                'autor': row['autor'],
                'texto': row['texto']
            })
        
        conn.close()
        
        return jsonify({'mensajes': mensajes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hablar', methods=['POST'])
def enviar_mensaje():
    """Enviar mensaje al chat y obtener respuesta del Dungeon Master"""
    try:
        data = request.json
        token = data.get('token')
        autor = data.get('autor')
        texto = data.get('texto')
        
        if not token or not autor or not texto:
            return jsonify({'error': 'Token, autor y texto son requeridos'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener siguiente orden
        cursor.execute('SELECT MAX(orden) FROM mensajes WHERE partida_token = ?', (token,))
        max_orden = cursor.fetchone()[0] or 0
        nuevo_orden = max_orden + 1
        
        # Guardar mensaje del jugador
        cursor.execute('''
            INSERT INTO mensajes (orden, autor, texto, partida_token)
            VALUES (?, ?, ?, ?)
        ''', (nuevo_orden, autor, texto, token))
        
        # Obtener contexto para la IA
        cursor.execute('''
            SELECT j.nombre, j.clase, j.nivel, j.energia, j.sp, j.experiencia
            FROM jugadores j
            WHERE j.partida_token = ?
        ''', (token,))
        
        jugadores = []
        for row in cursor.fetchall():
            jugadores.append({
                'nombre': row['nombre'],
                'clase': row['clase'],
                'nivel': row['nivel'],
                'energia': row['energia'],
                'sp': row['sp'],
                'experiencia': row['experiencia']
            })
        
        # Obtener últimos mensajes para contexto
        cursor.execute('''
            SELECT autor, texto
            FROM mensajes
            WHERE partida_token = ?
            ORDER BY orden DESC
            LIMIT 5
        ''', (token,))
        
        ultimos_mensajes = []
        for row in cursor.fetchall():
            ultimos_mensajes.append({
                'autor': row['autor'],
                'texto': row['texto']
            })
        
        # Construir contexto
        context = f"""
        Jugadores en la partida: {json.dumps(jugadores, ensure_ascii=False)}
        Últimos mensajes: {json.dumps(ultimos_mensajes, ensure_ascii=False)}
        """
        
        # Obtener respuesta del Dungeon Master
        respuesta_ia = call_gemini_api(context, texto)
        
        # Guardar respuesta de la IA
        cursor.execute('''
            INSERT INTO mensajes (orden, autor, texto, partida_token)
            VALUES (?, ?, ?, ?)
        ''', (nuevo_orden + 1, 'IA', respuesta_ia, token))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'orden': nuevo_orden,
            'autor': autor,
            'texto': texto,
            'respuesta_ia': respuesta_ia
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicializar base de datos al arrancar
    init_db()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT) 