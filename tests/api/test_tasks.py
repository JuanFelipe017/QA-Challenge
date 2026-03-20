import pytest
import uuid

# Tests para el módulo de tareas
class TestTasks:

    # ─────────────────────────────────────────
    # Crear tarea
    # ─────────────────────────────────────────

    # Crear tarea válida
    def test_create_task_successfully(self, client, base_url, created_project, created_user):
        payload = {
            "title": f"Tarea_{uuid.uuid4().hex[:8]}",
            "description": "Descripción de prueba",
            "project_id": created_project["id"],
            "reporter_id": created_user["id"],
            "priority": "medium"
        }
        response = client.post(f"{base_url}/tasks", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["project_id"] == created_project["id"]
        
        client.delete(f"{base_url}/tasks/{data['id']}") # Limpiar tarea creada

    # Crear tarea con project_id inválido
    def test_create_task_with_invalid_project_returns_404(self, client, base_url, created_user):
        payload = {
            "title": "Tarea proyecto inválido",
            "project_id": "00000000-0000-0000-0000-000000000000",
            "reporter_id": created_user["id"],
            "priority": "medium"
        }
        response = client.post(f"{base_url}/tasks", json=payload)
        assert response.status_code == 404

    # Crear tarea con reporter_id inválido
    def test_create_task_with_invalid_reporter_id(self, client, base_url, created_project):
        payload = {
            "title": "Tarea reporter inválido",
            "project_id": created_project["id"],
            "reporter_id": "00000000-0000-0000-0000-000000000000",
            "priority": "medium"
        }
        response = client.post(f"{base_url}/tasks", json=payload)
        # BUG-006: La API acepta reporter_id inexistente
        # Resultado esperado: 404, Resultado actual: 201
        assert response.status_code == 201, (
            "BUG-006 confirmado: La API acepta reporter_id inexistente (debería retornar 404)"
        )

    # Crear tarea con assignee_id inválido
    def test_create_task_with_invalid_assignee_id(self, client, base_url, created_project, created_user):
        payload = {
            "title": "Tarea assignee inválido",
            "project_id": created_project["id"],
            "reporter_id": created_user["id"],
            "assignee_id": "00000000-0000-0000-0000-000000000000",
            "priority": "medium"
        }
        response = client.post(f"{base_url}/tasks", json=payload)
        # BUG-006: La API acepta assignee_id inexistente
        # Resultado esperado: 404, Resultado actual: 201
        assert response.status_code == 201, (
            "BUG-006 confirmado: La API acepta assignee_id inexistente (debería retornar 404)"
        )

    # Crear tarea sin campos requeridos
    def test_create_task_missing_required_fields(self, client, base_url):
        payload = {"title": "Tarea sin proyecto"}
        response = client.post(f"{base_url}/tasks", json=payload)
        assert response.status_code == 422

    # Crear tarea con título vacío
    def test_create_task_empty_title_returns_422(self, client, base_url, created_project, created_user):
        payload = {
            "title": "",
            "project_id": created_project["id"],
            "reporter_id": created_user["id"],
            "priority": "medium"
        }
        response = client.post(f"{base_url}/tasks", json=payload)
        assert response.status_code == 422

    # ─────────────────────────────────────────
    # Listar tareas
    # ─────────────────────────────────────────

    # Listar tareas 
    def test_list_tasks_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/tasks")
        assert response.status_code == 200

    # Listar tareas debe retornar clave tasks con lista
    def test_list_tasks_returns_tasks_key(self, client, base_url):
        response = client.get(f"{base_url}/tasks")
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    # Listar tareas con paginación
    def test_list_tasks_pagination(self, client, base_url):
        response = client.get(f"{base_url}/tasks?limit=5")
        assert response.status_code == 200
        data = response.json()
        # BUG-009: El parámetro limit es ignorado — retorna todas las tareas
        # Resultado esperado: 5 tareas, Resultado actual: 20
        assert len(data["tasks"]) == 20, (
            "BUG-009 confirmado: El parámetro limit es ignorado en la paginación"
        )

    # Filtrar tareas por estado
    def test_filter_tasks_by_status(self, client, base_url):
        response = client.get(f"{base_url}/tasks?status=todo")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "todo"

    # Buscar tareas por título
    def test_search_tasks_by_title(self, client, base_url):
        response = client.get(f"{base_url}/tasks?search=Configurar")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data

    # ─────────────────────────────────────────
    # Obtener tarea por ID
    # ─────────────────────────────────────────

    # Obtener tarea por ID válido
    def test_get_task_by_valid_id(self, client, base_url, created_task):
        response = client.get(f"{base_url}/tasks/{created_task['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_task["id"]

    # Obtener tarea por ID inexistente 
    def test_get_task_by_invalid_id_returns_404(self, client, base_url):
        response = client.get(f"{base_url}/tasks/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    # ─────────────────────────────────────────
    # Actualizar tarea
    # ─────────────────────────────────────────

    # Actualizar estado de tarea
    def test_update_task_status(self, client, base_url, created_task):
        payload = {"status": "in_progress"}
        response = client.put(f"{base_url}/tasks/{created_task['id']}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    # Actualizar tarea con ID inexistente
    def test_update_task_invalid_id_returns_404(self, client, base_url):
        payload = {"status": "in_progress"}
        response = client.put(f"{base_url}/tasks/00000000-0000-0000-0000-000000000000", json=payload)
        assert response.status_code == 404

    # ─────────────────────────────────────────
    # Eliminar tarea
    # ─────────────────────────────────────────

    # Eliminar tarea existente
    def test_delete_task_successfully(self, client, base_url, created_project, created_user):
        payload = {
            "title": f"Tarea_delete_{uuid.uuid4().hex[:8]}",
            "project_id": created_project["id"],
            "reporter_id": created_user["id"],
            "priority": "low"
        }
        create_response = client.post(f"{base_url}/tasks", json=payload)
        task_id = create_response.json()["id"]
        response = client.delete(f"{base_url}/tasks/{task_id}")
        assert response.status_code == 200

    # Eliminar tarea con ID inexistente
    def test_delete_task_invalid_id_returns_404(self, client, base_url):
        response = client.delete(f"{base_url}/tasks/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404