# 🏰 Dungeon and Scrum

Un juego de rol basado en metodologías ágiles donde los jugadores asumen roles de desarrollo de software y exploran aventuras guiadas por una IA que actúa como Dungeon Master.

## 🎮 Características

- **Juego de rol ágil**: Los jugadores son Desarrolladores, Testers y Diseñadores
- **IA Dungeon Master**: Integración con Google Gemini para narrativa dinámica
- **Chat en tiempo real**: Comunicación grupal con respuestas de IA
- **Sistema de niveles**: Progresión de Junior a niveles superiores
- **Estadísticas de personaje**: Energía, SP (Story Points), experiencia
- **Interfaz moderna**: Diseño responsive y atractivo

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- API Key de Google Gemini

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd dungeonsagile
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Obtener API Key de Gemini**
   - Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Crea una nueva API key
   - Guárdala para la configuración

4. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

5. **Acceder a la aplicación**
   - Abre tu navegador en `http://localhost:5000`
   - Completa el wizard de configuración inicial

## ⚙️ Configuración

### Configuración inicial

Al acceder por primera vez, la aplicación mostrará un wizard que te permitirá:

1. **Configurar la base de datos**: Ruta del archivo SQLite (por defecto: `dungeon_and_scrum.db`)
2. **Ingresar API Key**: Tu clave de API de Google Gemini

### Archivo de configuración

La configuración se guarda en `config.py` y puede ser modificada manualmente:

```python
# Configuración de la base de datos
DB_PATH = 'dungeon_and_scrum.db'

# API Key de Gemini
GEMINI_API_KEY = 'TU_API_KEY_DE_GEMINI'

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
```

## 🎯 Cómo jugar

### 1. Crear o unirse a una partida

- **Crear nueva partida**: Deja vacío el campo "Partida" y haz clic en "Ingresar"
- **Unirse a partida**: Ingresa el token de la partida existente

### 2. Seleccionar personaje

- **Nombre**: Elige un nombre único para tu personaje
- **Clase**: Selecciona entre Desarrollador, Tester o Diseñador

### 3. Explorar y jugar

- **Chat grupal**: Escribe acciones en el chat central
- **Respuestas de IA**: El Dungeon Master responderá a tus acciones
- **Estado del equipo**: Observa las estadísticas de todos los jugadores

## 👥 Clases de personajes

### Desarrollador
- **SP inicial**: 4 (+4 por nivel)
- **Energía**: 10
- **Niveles**: Junior → SemiSenior → Senior → Arquitecto → Terry
- **Especialidad**: Desarrollo y arquitectura

### Tester
- **SP inicial**: 2 (+4 por nivel)
- **Energía**: 15
- **Niveles**: Junior → SemiSenior → Senior → Líder
- **Especialidad**: Testing y calidad

### Diseñador
- **SP inicial**: 2 (+4 por nivel)
- **Energía**: 30
- **Niveles**: Junior → SemiSenior → Senior
- **Especialidad**: Diseño y UX

## 🔧 API Endpoints

### POST /crear
Crea una nueva partida.

**Entrada:**
```json
{
    "nombre": "Juan",
    "clase": "Desarrollador"
}
```

**Respuesta:**
```json
{
    "token": "abc123",
    "mensaje": "Partida creada con éxito",
    "jugador": {
        "nombre": "Juan",
        "clase": "Desarrollador"
    }
}
```

### POST /unirse
Únete a una partida existente.

**Entrada:**
```json
{
    "nombre": "Ana",
    "clase": "Tester",
    "partida": "abc123"
}
```

### POST /estado
Obtiene el estado de los jugadores.

**Entrada:**
```json
{
    "token": "abc123"
}
```

### POST /chat
Obtiene el historial del chat.

**Entrada:**
```json
{
    "token": "abc123"
}
```

### POST /hablar
Envía un mensaje al chat.

**Entrada:**
```json
{
    "token": "abc123",
    "autor": "Juan",
    "texto": "Exploro la sala"
}
```

## 🛠️ Desarrollo

### Estructura del proyecto

```
dungeonsagile/
├── app.py              # Aplicación Flask principal
├── config.py           # Configuración
├── requirements.txt    # Dependencias Python
├── templates/
│   └── index.html     # Página principal
├── static/
│   ├── css/
│   │   └── style.css  # Estilos CSS
│   └── js/
│       └── app.js     # Lógica JavaScript
└── README.md
```

### Base de datos

La aplicación utiliza SQLite con las siguientes tablas:

- **partidas**: Información de las partidas
- **jugadores**: Datos de los personajes
- **mensajes**: Historial del chat

### Personalización

Puedes modificar:

- **Atributos de clases**: En `config.py`
- **Estilos**: En `static/css/style.css`
- **Lógica del frontend**: En `static/js/app.js`
- **Comportamiento del backend**: En `app.py`

## 🐛 Solución de problemas

### Error de configuración
- Verifica que la API key de Gemini sea válida
- Asegúrate de que la ruta de la base de datos sea accesible

### Error de conexión
- Verifica que el servidor esté ejecutándose
- Revisa la consola del navegador para errores detallados

### Problemas con la IA
- Verifica que la API key tenga permisos para Gemini
- Revisa los logs del servidor para errores de API

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

¡Disfruta explorando el mundo de Dungeon and Scrum! 🎮✨ 