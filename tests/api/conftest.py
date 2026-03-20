import pytest
import requests
import uuid

# URL base de la API
BASE_URL = "http://localhost:8080/api"

# Prueba de conexión a la API antes de ejecutar cualquier test
@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

# Sesión de requests reutilizable para todos los tests
@pytest.fixture(scope="session")
def client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

# Creación de datos de prueba para usuarios, proyectos y tareas
@pytest.fixture
def created_user(client, base_url):
    unique = uuid.uuid4().hex[:8]
    payload = {
        "username": f"testuser_{unique}",
        "full_name": "Test User Fixture",
        "email": f"fixture_{unique}@test.com",
        "role": "member"
    }
    response = client.post(f"{base_url}/users", json=payload)
    user = response.json()
    yield user
    if "id" in user:
        client.delete(f"{base_url}/users/{user['id']}") # Teardown: eliminar el usuario creado después del test

# Creación de un proyecto de prueba y eliminación al finalizar el test
@pytest.fixture
def created_project(client, base_url, created_user):
    payload = {
        "name": "Proyecto Fixture",
        "description": "Proyecto creado para pruebas automatizadas",
        "owner_id": created_user["id"]
    }
    response = client.post(f"{base_url}/projects", json=payload)
    project = response.json()
    yield project
    if "id" in project:
        client.delete(f"{base_url}/projects/{project['id']}") # Teardown: eliminar el proyecto creado después del test

# Creación de una tarea de prueba y eliminación al finalizar el test
@pytest.fixture
def created_task(client, base_url, created_project, created_user):
    payload = {
        "title": "Tarea Fixture",
        "description": "Tarea creada para pruebas automatizadas",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
        "priority": "medium"
    }
    response = client.post(f"{base_url}/tasks", json=payload)
    task = response.json()
    yield task
    if "id" in task:
        client.delete(f"{base_url}/tasks/{task['id']}") # Teardown: eliminar la tarea creada después del test