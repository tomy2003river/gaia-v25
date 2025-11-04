# Contributing to GAIA v25

¡Gracias por tu interés en contribuir a GAIA! 🎉

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor abre un [issue](https://github.com/tomy2003river/gaia-v25/issues) con:

- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs. actual
- Versión de Python y SO
- Logs relevantes

### Sugerir Features

Para nuevas funcionalidades:

1. Revisa los [issues existentes](https://github.com/tomy2003river/gaia-v25/issues)
2. Abre un nuevo issue con etiqueta "enhancement"
3. Describe el caso de uso y beneficios
4. Propón una implementación si es posible

### Pull Requests

1. **Fork** el repositorio
2. **Crea una rama** para tu feature:
   ```bash
   git checkout -b feature/mi-feature
   ```
3. **Escribe código** siguiendo las guías de estilo
4. **Añade tests** para tu código
5. **Ejecuta tests** y asegúrate que pasan:
   ```bash
   python -m pytest tests/
   ```
6. **Commit** con mensajes descriptivos:
   ```bash
   git commit -m "Añade handler para X"
   ```
7. **Push** a tu fork:
   ```bash
   git push origin feature/mi-feature
   ```
8. **Abre un Pull Request** en GitHub

## Guías de Estilo

### Python

- Sigue [PEP 8](https://pep8.org/)
- Usa type hints cuando sea posible
- Docstrings en formato Google/NumPy
- Nombres descriptivos en español para conceptos de dominio

```python
def procesar_mensaje(mensaje: str, contexto: Optional[Dict] = None) -> Response:
    """
    Procesa un mensaje del usuario.
    
    Args:
        mensaje: Texto del usuario
        contexto: Contexto opcional
        
    Returns:
        Objeto Response con la respuesta
    """
    pass
```

### Commits

- Mensajes en español
- Formato: `<tipo>: <descripción>`
- Tipos: feat, fix, docs, style, refactor, test, chore

Ejemplos:
```
feat: añade handler para música
fix: corrige error en caché de Wikipedia
docs: actualiza README con ejemplos
test: añade tests para Cronos handler
```

### Tests

- Test por cada feature nueva
- Tests unitarios en `tests/test_*.py`
- Usa mocks para servicios externos
- Cobertura mínima del 80%

```python
class TestMiHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MiHandler()
    
    def test_can_handle(self):
        self.assertTrue(self.handler.can_handle("test"))
```

## Proceso de Revisión

1. Un maintainer revisará tu PR
2. Se pueden solicitar cambios
3. Una vez aprobado, se hará merge
4. Tu contribución aparecerá en el changelog

## Código de Conducta

- Sé respetuoso y constructivo
- Acepta feedback con mente abierta
- Ayuda a otros contributors
- Mantén discusiones profesionales

## Preguntas

¿Dudas? Abre un [discussion](https://github.com/tomy2003river/gaia-v25/discussions) o contacta al equipo.

¡Gracias por contribuir a GAIA! 🚀
