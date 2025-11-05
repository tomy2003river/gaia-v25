# GAIA v25 — Vision & Technical Plan

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-25.0.0-orange.svg)

> **Elevator pitch**
> 
> GAIA es un asistente multimodal, modular y extensible que combina NLU robusto, herramientas conectables y memoria evolutiva para **entender**, **razonar** y **actuar** con estilo propio. v25 reestructura la arquitectura en intents/handlers, añade RAG ligero, cola de TTS, llamadas no bloqueantes y métricas de calidad.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Principios de Diseño](#-principios-de-diseño)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Módulos y Handlers](#-módulos-y-handlers)
- [Servicios](#-servicios)
- [Memoria y Aprendizaje](#-memoria-y-aprendizaje)
- [TTS y Concurrencia](#-tts-y-concurrencia)
- [Telemetría](#-telemetría)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contribuir](#-contribuir)

---

## ✨ Características

- **🎯 NLU por Reglas**: Clasificación de intents con patrones regex y prioridades
- **🌤️ Clima (Cronos)**: Consultas meteorológicas con OpenWeatherMap
- **📚 Conocimiento (Apolo)**: Búsquedas en Wikipedia con caché inteligente
- **🧠 Memoria (Hades)**: Sistema de memoria con ventana deslizante y decaimiento
- **🌿 Naturaleza (Rea)**: Base de conocimientos sobre naturaleza y ecosistemas
- **🔊 TTS Thread-Safe**: Cola única con worker dedicado para síntesis de voz
- **⚡ Non-Blocking**: Llamadas a red en threads, UI siempre responsiva
- **📊 Telemetría**: Logs JSON, métricas de latencia y trazas de respuesta
- **🔒 Seguridad**: Sin secretos en código, validación de configuración
- **🎨 UI Tkinter**: Interfaz gráfica demo, core desacoplado para CLI/Web

---

## 🎯 Principios de Diseño

1. **Modularidad**: Cada capacidad vive en un *módulo* (intent/handler) intercambiable
2. **Observabilidad**: Logs estructurados + métricas + trazas de cada respuesta
3. **Seguridad por defecto**: Sin secretos en código, límites de herramientas, sanitización
4. **UX fluida**: UI reactiva, cero bloqueos, TTS secuenciado
5. **Aprendizaje gradual**: Memoria con ventana + perfilado de usuario
6. **Portabilidad**: Funciona en Windows/macOS/Linux, sin dependencias exclusivas

---

## 🏗️ Arquitectura

```
App (UI) ─┬─> Core Router (NLU ↔ Intent Classifier) ──┬─> Handlers (Cronos/Rea/Apolo/Hades/...)
          │                                            │
          │                                            ├─> Tools (OpenWeather, Wikipedia, ...)
          │                                            │
          ├─> TTS Queue Worker <───────────────────────┘
          │
          ├─> Memory Service (deque+TTL/decay) ──> Storage (JSON/SQLite)
          │
          └─> Telemetry (logs JSON, métricas, trazas)
```

### Estructura de Carpetas

```
gaia-v25/
├── config/           # Configuración y variables de entorno
├── core/             # Router, memoria, errores, telemetría
├── services/         # TTS, weather, wikipedia
├── handlers/         # Intent handlers (Cronos, Apolo, Hades, Rea)
├── ui/               # Interfaz Tkinter
├── tests/            # Tests unitarios e integración
├── data/             # Datos persistentes (memoria)
├── logs/             # Logs de aplicación y telemetría
├── cache/            # Caché de Wikipedia
├── gaia.py           # Core application
├── .env.example      # Ejemplo de configuración
└── requirements.txt  # Dependencias Python
```

---

## 📦 Instalación

### Requisitos

- Python 3.8+
- pip

### Pasos

1. **Clonar el repositorio**

```bash
git clone https://github.com/tomy2003river/gaia-v25.git
cd gaia-v25
```

2. **Crear entorno virtual** (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tu API key de OpenWeather
```

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# API de OpenWeather (obligatorio)
OPENWEATHER_API_KEY=tu_api_key_aqui

# Ciudad por defecto
GAIA_CITY=Buenos Aires

# Idioma (es/en)
GAIA_LANG=es

# TTS
GAIA_TTS_RATE=160
GAIA_TTS_VOICE_ID=

# Memoria
GAIA_MEMORY_MAXLEN=200
GAIA_MEMORY_DECAY=0.95

# Caché
GAIA_CACHE_TTL=1800

# Logging
GAIA_LOG_LEVEL=INFO
GAIA_LOG_FILE=logs/gaia.log
```

### Obtener API Key de OpenWeather

1. Visita [OpenWeatherMap](https://openweathermap.org/api)
2. Crea una cuenta gratuita
3. Genera una API key
4. Cópiala en tu archivo `.env`

---

## 🚀 Uso

### Iniciar la UI

```bash
python ui/app.py
```

### Ejemplos de Consultas

**Clima (Cronos)**
```
- "¿Qué tiempo hace?"
- "¿Cómo está el clima en Madrid?"
- "Temperatura actual"
```

**Conocimiento (Apolo)**
```
- "¿Qué sabes de Albert Einstein?"
- "Cuéntame sobre la fotosíntesis"
- "¿Quién es Mozart?"
```

**Memoria (Hades)**
```
- "¿De qué hablamos ayer?"
- "¿Recuerdas nuestra conversación?"
- "Dame un resumen"
- "Olvida todo" (reset)
```

**Naturaleza (Rea)**
```
- "Háblame de los árboles"
- "¿Qué es un ecosistema?"
- "Información sobre pájaros"
```

**General**
```
- "Hola" (saludo)
- "Ayuda" (mostrar capacidades)
- "Adiós" (despedida)
```

---

## 🎭 Módulos y Handlers

### Sistema de Prioridades

Cada handler tiene una prioridad que determina el orden de evaluación:

1. **Hades (90)**: Memoria y eventos pasados
2. **Cronos (80)**: Clima y tiempo
3. **Apolo (70)**: Conocimiento general
4. **Rea (60)**: Naturaleza
5. **Generic (10)**: Fallback

### Cronos Handler (Clima)

- **Intent**: `CRONOS`
- **Servicio**: OpenWeatherMap API
- **Capacidades**:
  - Clima actual por ciudad
  - Temperatura, sensación térmica, humedad
  - Descripción del tiempo
  - Velocidad del viento

**Personalidad**: Habla con autoridad sobre el tiempo

### Apolo Handler (Conocimiento)

- **Intent**: `APOLO`
- **Servicio**: Wikipedia API
- **Capacidades**:
  - Búsqueda de artículos
  - Resúmenes con caché (TTL 30 min)
  - Sugerencias de temas relacionados

**Personalidad**: Guía sabio del conocimiento

### Hades Handler (Memoria)

- **Intent**: `HADES`
- **Servicio**: Sistema de memoria interno
- **Capacidades**:
  - Recordar conversaciones pasadas
  - Búsqueda por keywords
  - Resumen de temas principales
  - Reset de memoria

**Personalidad**: Guardián del pasado

### Rea Handler (Naturaleza)

- **Intent**: `REA`
- **Servicio**: Base de conocimientos interna
- **Capacidades**:
  - Información sobre flora y fauna
  - Ecosistemas
  - Hechos sobre naturaleza

**Personalidad**: Voz reverente de la naturaleza

### Generic Handler (Fallback)

- **Intent**: `GENERIC`, `GREETING`, `FAREWELL`
- **Capacidades**:
  - Saludos y despedidas
  - Ayuda
  - Respuestas genéricas

---

## 🛠️ Servicios

### TTS Service

Thread-safe text-to-speech con cola única:

```python
from services import TTSService

tts = TTSService(rate=160)
tts.speak("Hola, soy GAIA")  # Non-blocking
```

**Características**:
- Cola única con worker daemon
- Selección automática de voz española
- No bloquea el thread principal

### Weather Service

Cliente OpenWeatherMap con error handling:

```python
from services import WeatherService

weather = WeatherService(api_key="...")
data = weather.get_current_weather("Madrid")
# {'temp': 22.5, 'description': 'cielo claro', ...}
```

**Características**:
- HTTPS por defecto
- Timeout de 10 segundos
- Retry automático
- Manejo de errores robusto

### Wikipedia Service

Cliente Wikipedia con caché:

```python
from services import WikipediaService

wiki = WikipediaService(cache_dir="./cache")
titles = wiki.search("Einstein")  # Buscar
summary = wiki.get_summary(titles[0])  # Obtener resumen
```

**Características**:
- Caché local con TTL configurable
- Búsqueda y resúmenes
- Soporte multiidioma

---

## 🧠 Memoria y Aprendizaje

### Características

- **Estructura**: `deque(maxlen=200)` con decaimiento exponencial
- **Peso**: Eventos recientes > eventos antiguos (decay=0.95)
- **Búsqueda**: Por keywords en cualquier campo
- **Resumen**: Topics principales por frecuencia ponderada
- **Privacidad**: Session-only por defecto, opcional en disco
- **Reset**: Comando `/reset` o "olvida todo"

### Uso

```python
from core import Memory

memory = Memory(maxlen=200, decay=0.95)

# Añadir evento
memory.add({
    "type": "interaction",
    "topic": "clima",
    "content": "Preguntó por el clima en Madrid"
})

# Buscar
results = memory.search("Madrid")

# Topics principales
topics = memory.get_topics()  # [(topic, score), ...]

# Limpiar
memory.clear()
```

---

## 🔊 TTS y Concurrencia

### Problema

pyttsx3 no es thread-safe. Múltiples llamadas concurrentes a `runAndWait()` causan bloqueos.

### Solución

Cola única con worker dedicado:

```python
# services/tts.py
class TTSService:
    def __init__(self):
        self.q = queue.Queue()
        self.engine = pyttsx3.init()
        threading.Thread(target=self._loop, daemon=True).start()
    
    def _loop(self):
        while True:
            text = self.q.get()
            if text is None: break
            self.engine.say(text)
            self.engine.runAndWait()
    
    def speak(self, text: str):
        self.q.put(text)  # Non-blocking
```

### Networking Non-Blocking

Todas las llamadas a APIs externas se ejecutan en threads:

```python
def _process_message_thread(self, message: str):
    # En thread separado
    response = self.gaia.process_message(message)
    
    # Actualizar UI en main thread
    self.root.after(0, self._show_response, response)
```

---

## 📊 Telemetría

### Métricas Capturadas

- **Requests totales**: Contador global
- **Errores**: Rate de fallos
- **Latencia**: p50, p95, promedio
- **Por intent**: Stats individuales por handler
- **Timestamps**: ISO 8601 UTC

### Logs JSON

Cada request genera un log estructurado:

```json
{
  "timestamp": "2025-11-04T23:00:00.000Z",
  "intent": "CRONOS",
  "latency_ms": 234.5,
  "success": true,
  "error": null
}
```

### Uso

```python
from core import Telemetry

telemetry = Telemetry(log_file="logs/telemetry.jsonl")

# Log request
telemetry.log_request(
    intent="CRONOS",
    latency_ms=123.4,
    success=True
)

# Get metrics
metrics = telemetry.get_metrics()
# {
#   "total_requests": 42,
#   "error_rate": 0.05,
#   "latency_p50": 234.5,
#   "latency_p95": 1234.5,
#   ...
# }
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/

# Tests específicos
python -m pytest tests/test_core.py
python -m pytest tests/test_handlers.py

# Con cobertura
python -m pytest --cov=. --cov-report=html
```

### Estructura de Tests

```
tests/
├── test_core.py       # Router, memoria, errores
├── test_handlers.py   # Handlers individuales
└── test_services.py   # Servicios externos (mocked)
```

### Ejemplos

```python
# test_core.py
def test_cronos_weather(self):
    router = IntentRouter()
    intent = router.classify("¿Qué tiempo hace?")
    self.assertEqual(intent, "CRONOS")

# test_handlers.py
def test_greeting(self):
    handler = GenericHandler()
    response = handler.handle("Hola", {"intent": "GREETING"})
    self.assertTrue(response.success)
    self.assertIn("GAIA", response.text)
```

---

## 🗺️ Roadmap

### Sprint 1 (v25.0) ✅

- [x] Estructura de carpetas y módulos
- [x] Sistema de configuración con .env
- [x] Router con prioridades
- [x] TTS con cola única
- [x] Handlers: Cronos, Apolo, Hades, Rea, Generic
- [x] Servicios: Weather, Wikipedia, TTS
- [x] Memoria con ventana y decay
- [x] UI Tkinter con threads
- [x] Telemetría básica
- [x] Tests unitarios
- [x] Documentación completa

### Sprint 2 (v25.1)

- [ ] RAG ligero para Apolo (embeddings + reranking)
- [ ] Caché mejorado con FAISS opcional
- [ ] EntityRuler con spaCy para extracción
- [ ] Comando `/reset` en UI
- [ ] Panel de métricas (Streamlit)

### Sprint 3 (v25.2)

- [ ] Paquete pip `gaia-core`
- [ ] CLI alternativo
- [ ] Plugins system
- [ ] Tests E2E completos
- [ ] CI/CD con GitHub Actions

### Sprint 4 (v26)

- [ ] UI Web (FastAPI + HTMX/Tailwind)
- [ ] Internacionalización EN/ES completa
- [ ] Voice input (STT)
- [ ] Multimodal: Image understanding
- [ ] Docker compose

---

## 🤝 Contribuir

¡Cualquier contribucionn es bienvenida! Por favor:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Añade nueva feature'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

### Guidelines

- Sigue PEP 8 para código Python
- Añade tests para nuevas features
- Actualiza documentación
- Commits descriptivos en español

---

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles

---

## 👥 Autores

- **GAIA Team** - Desarrollo inicial

---

## 🙏 Agradecimientos

- OpenWeatherMap por la API de clima
- Wikipedia por el conocimiento libre
- La comunidad Python por las excelentes librerías

---

## 📞 Contacto y Soporte

- **Issues**: [GitHub Issues](https://github.com/tomy2003river/gaia-v25/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tomy2003river/gaia-v25/discussions)

---

## 📚 Documentación Adicional

### Métricas de Calidad

Para evolucionar GAIA, medimos:

- **Task success**: Etiquetado humano 0/1 por intent
- **Factualidad** (Apolo): 3 puntos (correcto, discutible, incorrecto)
- **Latencia**: p50 < 600ms (sin red), p95 < 2.5s (con red)
- **Estilo/voz**: Consistencia de "personas" por handler

### Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Bloqueos de UI | Threads + `root.after()` |
| TTS no thread-safe | Cola única con worker |
| Rate limits externos | Caché + retry + mensajes empáticos |
| Fuga de secretos | `.env`, `.gitignore`, validación |
| Deriva de reglas NLU | Tests + telemetría de fallback rate |

### Snippets Útiles

**Añadir nuevo handler**:

```python
from handlers.base import BaseHandler
from core.errors import Response

class MiHandler(BaseHandler):
    def __init__(self):
        super().__init__(name="MI_INTENT", priority=75)
    
    def can_handle(self, message: str, context=None) -> bool:
        return True
    
    def handle(self, message: str, context=None) -> Response:
        return Response(
            text="Mi respuesta",
            intent="MI_INTENT",
            success=True
        )
```

**Registrar en router**:

```python
# core/router.py
self.add_rule(
    priority=75,
    name="MI_INTENT",
    pattern=r"\b(mi|patron)\b",
    description="Mi nuevo intent"
)
```

**Registrar en GAIA**:

```python
# gaia.py
self.handlers["MI_INTENT"] = MiHandler()
```

---

**¡Disfruta usando GAIA v25!** 🚀
