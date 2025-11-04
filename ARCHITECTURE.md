# GAIA v25 - Architecture Documentation

## Overview

GAIA v25 es un asistente de IA multimodal construido con una arquitectura modular que separa claramente las responsabilidades entre componentes.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                            │
│  ┌──────────────┐              ┌──────────────┐           │
│  │ Tkinter UI   │              │  CLI Mode    │           │
│  │  (ui/app.py) │              │  (cli.py)    │           │
│  └──────┬───────┘              └──────┬───────┘           │
└─────────┼──────────────────────────────┼──────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                    GAIA Core (gaia.py)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  process_message(msg) → Response                      │  │
│  └───┬──────────────────────────────────────────────────┘  │
│      │                                                       │
│  ┌───▼──────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │ IntentRouter │→ │   Handler   │→ │   Services   │      │
│  │  (classify)  │  │  (handle)   │  │              │      │
│  └──────────────┘  └─────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │   Memory     │  │  Telemetry  │  │  TTS Queue   │      │
│  │   Service    │  │   Service   │  │   Worker     │      │
│  └──────────────┘  └─────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
          │                  │                  │
┌─────────▼──────┐  ┌────────▼─────┐  ┌────────▼──────┐
│ External APIs  │  │ File Storage │  │ Audio Output  │
│ - OpenWeather  │  │ - Logs       │  │ - pyttsx3     │
│ - Wikipedia    │  │ - Memory     │  │               │
└────────────────┘  └──────────────┘  └───────────────┘
```

## Capas

### 1. UI Layer (ui/, cli.py)

**Responsabilidad**: Interacción con el usuario

- **Tkinter UI**: Interfaz gráfica con threading para no bloquear
- **CLI**: Línea de comandos para pruebas y uso headless
- **Características**:
  - Input/output de mensajes
  - Comandos especiales (/help, /metrics, /quit)
  - Manejo de errores visual

### 2. Core Layer (gaia.py)

**Responsabilidad**: Orquestación de componentes

```python
class GAIACore:
    - router: IntentRouter          # Clasificación
    - handlers: Dict[Handler]       # Procesadores
    - memory: Memory                # Sistema de memoria
    - telemetry: Telemetry          # Métricas
    - services: TTS, Weather, Wiki  # Servicios externos
    
    def process_message(msg) -> Response:
        1. Clasificar intent (router)
        2. Seleccionar handler
        3. Ejecutar handler
        4. Registrar en memoria
        5. Log telemetría
        6. Retornar respuesta
```

### 3. Router & Classification (core/router.py)

**Responsabilidad**: Mapear mensajes a intents

```python
class IntentRouter:
    rules: List[IntentRule]  # Prioridad descendente
    
    def classify(message) -> str:
        for rule in rules:
            if rule.pattern.match(message):
                return rule.name
        return "GENERIC"
```

**Prioridades**:
- 90: HADES (memoria)
- 80: CRONOS (clima)
- 70: APOLO (conocimiento)
- 60: REA (naturaleza)
- 10: GENERIC/GREETING/FAREWELL

### 4. Handlers (handlers/)

**Responsabilidad**: Procesar intents específicos

```python
class BaseHandler(ABC):
    name: str
    priority: int
    
    @abstractmethod
    def can_handle(msg, ctx) -> bool
    
    @abstractmethod
    def handle(msg, ctx) -> Response
```

**Handlers Implementados**:
- **CronosHandler**: Consultas de clima (OpenWeather API)
- **ApoloHandler**: Búsquedas de conocimiento (Wikipedia)
- **HadesHandler**: Memoria y recordatorios
- **ReaHandler**: Información sobre naturaleza
- **GenericHandler**: Saludos, despedidas, ayuda

### 5. Services (services/)

**Responsabilidad**: Comunicación con APIs externas

#### TTS Service (services/tts.py)
```python
class TTSService:
    q: Queue              # Cola thread-safe
    engine: pyttsx3.Engine
    worker: Thread        # Worker daemon
    
    def speak(text):      # Non-blocking
        q.put(text)
    
    def _loop():          # Worker loop
        while True:
            text = q.get()
            engine.say(text)
            engine.runAndWait()
```

**Por qué cola única**: pyttsx3 no es thread-safe, múltiples llamadas concurrentes causan deadlocks.

#### Weather Service (services/weather.py)
```python
class WeatherService:
    api_key: str
    lang: str
    
    def get_current_weather(city) -> Dict:
        - Timeout: 10s
        - HTTPS obligatorio
        - Error handling robusto
        - Retry en fallos transitorios
```

#### Wikipedia Service (services/wikipedia.py)
```python
class WikipediaService:
    cache: WikipediaCache  # TTL-based
    lang: str
    
    def search(query) -> List[str]
    def get_summary(title) -> Dict
    
    # Cache con TTL de 30 min por defecto
```

### 6. Memory System (core/memory.py)

**Responsabilidad**: Almacenar y recuperar contexto

```python
class Memory:
    events: deque(maxlen=200)  # Ventana deslizante
    decay: float = 0.95         # Factor de decaimiento
    
    def add(item):
        events.append({"item": item, "weight": 1.0})
    
    def get_topics() -> List[(topic, score)]:
        # Score = Σ(weight * decay^age)
        # Eventos recientes pesan más
    
    def search(keyword) -> List[Dict]:
        # Búsqueda full-text en eventos
```

**Decaimiento Exponencial**:
```
Event 1 (most recent):  weight = 1.0
Event 2:                weight = 0.95
Event 3:                weight = 0.90
Event 4:                weight = 0.86
...
```

### 7. Telemetry (core/telemetry.py)

**Responsabilidad**: Observabilidad y métricas

```python
class Telemetry:
    metrics: Dict
    
    def log_request(intent, latency_ms, success, error):
        # Incrementa contadores
        # Actualiza latencias
        # Escribe a archivo JSON
    
    def get_metrics() -> Dict:
        return {
            "total_requests": int,
            "error_rate": float,
            "latency_p50": float,
            "latency_p95": float,
            "by_intent": {...}
        }
```

**Formato de Log**:
```json
{
  "timestamp": "2025-11-04T23:00:00.000Z",
  "intent": "CRONOS",
  "latency_ms": 234.5,
  "success": true,
  "error": null
}
```

## Flujo de Datos

### Request Flow

```
1. Usuario: "¿Qué tiempo hace?"
   ↓
2. UI: input_entry.get()
   ↓
3. Thread: _process_message_thread()
   ↓
4. GAIACore.process_message()
   ↓
5. IntentRouter.classify() → "CRONOS"
   ↓
6. CronosHandler.handle()
   ↓
7. WeatherService.get_current_weather()
   ↓
8. Response(text="En Buenos Aires...", intent="CRONOS")
   ↓
9. Memory.add({"topic": "clima", ...})
   ↓
10. Telemetry.log_request("CRONOS", 234ms, True)
    ↓
11. TTS.speak("En Buenos Aires...")
    ↓
12. UI: root.after(0, _show_response)
    ↓
13. Usuario ve respuesta
```

## Patrones de Diseño

### 1. Strategy Pattern (Handlers)
Cada handler implementa la misma interfaz pero con lógica diferente.

### 2. Chain of Responsibility (Router)
Cada regla se evalúa en orden de prioridad hasta encontrar match.

### 3. Producer-Consumer (TTS)
Producer: múltiples threads llamando speak()
Consumer: único worker procesando cola

### 4. Observer Pattern (Telemetry)
Cada operación notifica a telemetría para logging.

### 5. Singleton Pattern (Config)
Una única instancia de configuración compartida.

## Concurrencia

### Threading Model

```
Main Thread
├─ UI Event Loop (Tkinter mainloop)
│
├─ Message Processing Threads
│  └─ Spawn per user message
│     └─ Calls external APIs
│        └─ Updates UI via root.after()
│
└─ TTS Worker Thread (daemon)
   └─ Processes speech queue
```

### Thread Safety

- **TTS**: Cola thread-safe (queue.Queue)
- **UI Updates**: Solo en main thread via root.after()
- **Memory**: Acceso serial (no locks necesarios en Python GIL)
- **Telemetry**: Escrituras atómicas a archivo

## Error Handling

### Niveles

1. **Service Level**: Timeouts, retries, HTTPErrors
2. **Handler Level**: Try/except con Response(success=False)
3. **Core Level**: Catch-all que retorna error response
4. **UI Level**: Muestra error al usuario

### Ejemplo

```python
try:
    weather = weather_service.get_current_weather(city)
except requests.Timeout:
    return Response(
        text="El servicio de clima no responde...",
        intent="CRONOS",
        success=False,
        error="Timeout"
    )
```

## Configuración

### Environment Variables (.env)

```
OPENWEATHER_API_KEY=xxx     # Obligatorio
GAIA_CITY=Buenos Aires      # Default ciudad
GAIA_LANG=es                # Idioma
GAIA_TTS_RATE=160           # Velocidad de habla
GAIA_MEMORY_MAXLEN=200      # Tamaño ventana
GAIA_MEMORY_DECAY=0.95      # Factor decaimiento
GAIA_CACHE_TTL=1800         # TTL caché (segundos)
GAIA_LOG_LEVEL=INFO         # Nivel de logging
```

### Validation

```python
Config.validate() -> (bool, List[str])
# Retorna False + errores si configuración inválida
# Crea directorios necesarios (data/, logs/, cache/)
```

## Extensibilidad

### Añadir Nuevo Handler

1. **Crear handler**:
```python
# handlers/mi_handler.py
from handlers.base import BaseHandler
from core.errors import Response

class MiHandler(BaseHandler):
    def __init__(self):
        super().__init__(name="MI_INTENT", priority=75)
    
    def can_handle(self, message, context=None):
        return True
    
    def handle(self, message, context=None):
        return Response(
            text="Mi respuesta",
            intent="MI_INTENT",
            success=True
        )
```

2. **Registrar en router**:
```python
# core/router.py
self.add_rule(
    priority=75,
    name="MI_INTENT",
    pattern=r"\b(mi|patron)\b",
    description="Mi intent"
)
```

3. **Registrar en core**:
```python
# gaia.py
self.handlers["MI_INTENT"] = MiHandler()
```

### Añadir Nuevo Servicio

```python
# services/mi_service.py
class MiService:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def fetch_data(self, query):
        # Implementación
        pass
```

Luego usar en handler correspondiente.

## Testing

### Test Layers

1. **Unit Tests**: Componentes individuales (router, memory, handlers)
2. **Integration Tests**: Handlers + Services (con mocks)
3. **E2E Tests**: Flujo completo (TODO)

### Mocking External Services

```python
from unittest.mock import Mock

weather_mock = Mock()
weather_mock.get_current_weather.return_value = {
    "temp": 22.5,
    "description": "soleado"
}

handler = CronosHandler(weather_service=weather_mock)
```

## Performance

### Targets

- Latencia p50 < 600ms (sin red)
- Latencia p95 < 2.5s (con red)
- Memory footprint < 100MB
- UI responsiva (0 freezes)

### Optimizaciones

1. **Caché Wikipedia**: TTL 30 min reduce llamadas API
2. **Threading**: Requests no bloquean UI
3. **Memory deque**: O(1) append/popleft
4. **TTS queue**: Evita overhead de init múltiple

## Security

### Principios

1. **No secrets en código**: Solo en .env
2. **HTTPS obligatorio**: APIs externas
3. **Input sanitization**: Handlers validan input
4. **Rate limiting**: TODO (v26)
5. **Audit logs**: Telemetría registra todo

### Checklist

- [x] API keys en .env
- [x] .env en .gitignore
- [x] Validación de configuración al inicio
- [x] HTTPS en todas las APIs
- [x] Timeouts en requests
- [ ] Rate limiting (v26)
- [ ] Input validation avanzada (v26)

## Future Architecture (v26)

### Web UI
```
FastAPI Backend
├─ WebSocket for real-time updates
├─ REST API for messages
└─ Static serving (HTMX + Tailwind)
```

### Database
```
SQLite → PostgreSQL migration
├─ Memory persistence
├─ User profiles
└─ Conversation history
```

### Plugins System
```
Plugin Interface
├─ Dynamic handler loading
├─ Sandboxed execution
└─ Version management
```

---

**Nota**: Esta arquitectura prioriza simplicidad y mantenibilidad sobre abstracciones prematuras. Cada componente tiene una responsabilidad clara y bien definida.
