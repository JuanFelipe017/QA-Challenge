# 🧪 Tests de API — TaskFlow

Tests automatizados para la API REST de TaskFlow usando `pytest` y `requests`.

## Requisitos

- Python 3.10+
- La aplicación TaskFlow corriendo en `http://localhost:8080`

## Instalación
```bash
# Desde la raíz del proyecto
python -m venv venv
venv\Scripts\activate        
pip install -r requirements-test.txt
```

## Ejecutar los tests

```bash
# Todos los tests
cd tests/api
python -m pytest -v

# Un módulo específico
python -m pytest test_users.py -v
python -m pytest test_tasks.py -v
```

## Estructura

| Archivo | Descripción |
|---|---|
| `conftest.py` | Fixtures compartidos y configuración base |
| `test_health.py` | Tests del health check |
| `test_users.py` | Tests de usuarios (CRUD + validaciones) |
| `test_projects.py` | Tests de proyectos (CRUD + filtros) |
| `test_tasks.py` | Tests de tareas (CRUD + paginación + búsqueda) |
| `test_comments.py` | Tests de comentarios |
| `test_stats.py` | Tests de estadísticas |
| `test_export.py` | Tests de exportación JSON y CSV |

## Resultado esperado

```
65 passed in ~5s
```

## Notas

Algunos tests documentan bugs intencionales de la aplicación. Estos tests pasan pero incluyen comentarios explicando el comportamiento incorrecto. Ver `docs/bug-reports.md` para el detalle completo.