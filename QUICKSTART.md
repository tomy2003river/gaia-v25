# GAIA v25 - Quick Start Guide

## Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/tomy2003river/gaia-v25.git
cd gaia-v25

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu API key de OpenWeather
# Obtén una gratis en: https://openweathermap.org/api
```

Ejemplo de `.env`:
```bash
OPENWEATHER_API_KEY=tu_clave_api_aqui
GAIA_CITY=Buenos Aires
GAIA_LANG=es
```

### 3. Ejecutar

**Modo UI (Interfaz Gráfica)**
```bash
python ui/app.py
```

**Modo CLI (Línea de Comandos)**
```bash
python cli.py
```

### 4. Probar

Intenta estas consultas:

```
👤 Tú: ¿Qué tiempo hace?
🤖 GAIA: En Buenos Aires, la temperatura actual es de...

👤 Tú: ¿Qué sabes de Einstein?
🤖 GAIA: Según mis fuentes, sobre Albert Einstein...

👤 Tú: Háblame de la naturaleza
🤖 GAIA: La naturaleza nos enseña sobre...

👤 Tú: ¿De qué hablamos?
🤖 GAIA: En nuestras conversaciones recientes hemos hablado sobre...
```

## Comandos CLI

- `/help` - Mostrar ayuda
- `/metrics` - Ver métricas de uso
- `/quit` - Salir

## Solución de Problemas

### Error: "OPENWEATHER_API_KEY no está configurada"

Asegúrate de que tu archivo `.env` existe y contiene una clave API válida.

### Warning: "pyttsx3 not available"

Instala pyttsx3:
```bash
pip install pyttsx3
```

En macOS puede requerir:
```bash
pip install pyobjc
```

### Tests

Para ejecutar los tests:
```bash
python -m unittest discover tests/
```

Deberías ver:
```
Ran 21 tests in 0.002s
OK
```

## Siguientes Pasos

1. Personaliza tu ciudad por defecto en `.env`
2. Explora diferentes consultas
3. Revisa las métricas con `/metrics` en CLI
4. Lee el [README completo](README.md) para características avanzadas
5. Contribuye al proyecto siguiendo [CONTRIBUTING.md](CONTRIBUTING.md)

## Estructura del Proyecto

```
gaia-v25/
├── config/           # Configuración
├── core/             # Router, memoria, telemetría
├── services/         # TTS, weather, wikipedia
├── handlers/         # Intent handlers
├── ui/               # Interfaz Tkinter
├── tests/            # Tests unitarios
├── cli.py            # CLI mode
├── gaia.py           # Core application
└── README.md         # Documentación completa
```

## Recursos

- [Documentación Completa](README.md)
- [Guía de Contribución](CONTRIBUTING.md)
- [Issues](https://github.com/tomy2003river/gaia-v25/issues)

¡Disfruta usando GAIA! 🚀
