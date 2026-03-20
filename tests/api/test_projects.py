import pytest
import uuid

# Tests para el módulo de proyectos
class TestProjects:

    # ─────────────────────────────────────────
    # Crear proyecto
    # ─────────────────────────────────────────

    # Crear un proyecto válido debe retornar 201
    def test_create_project_successfully(self, client, base_url, created_user):
        payload = {
            "name": f"Proyecto_{uuid.uuid4().hex[:8]}",
            "description": "Proyecto de prueba",
            "owner_id": created_user["id"]
        }
        response = client.post(f"{base_url}/projects", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["owner_id"] == created_user["id"]
        # Teardown
        client.delete(f"{base_url}/projects/{data['id']}")

    # Crear proyecto sin owner_id debe retornar 422
    def test_create_project_without_owner_returns_422(self, client, base_url):
        payload = {"name": "Proyecto sin owner"}
        response = client.post(f"{base_url}/projects", json=payload)
        assert response.status_code == 422

    # Crear proyecto con owner_id inválido debe retornar 404
    def test_create_project_with_invalid_owner_returns_404(self, client, base_url):
        """Crear proyecto con owner_id inexistente debe retornar 404 — BUG-008."""
        payload = {
            "name": "Proyecto owner inválido",
            "owner_id": "00000000-0000-0000-0000-000000000000"
        }
        response = client.post(f"{base_url}/projects", json=payload)
        # BUG-008: La API acepta owner_id inexistente — igual que BUG-006 con tareas
        assert response.status_code == 201, (
            "BUG-008 confirmado: La API acepta owner_id inexistente (debería retornar 404)"
        )

    # Crear proyecto con nombre vacío debe retornar 422
    def test_create_project_empty_name_returns_422(self, client, base_url, created_user):
        payload = {
            "name": "",
            "owner_id": created_user["id"]
        }
        response = client.post(f"{base_url}/projects", json=payload)
        assert response.status_code == 422

    # ─────────────────────────────────────────
    # Listar proyectos
    # ─────────────────────────────────────────

    # Listar proyectos debe retornar 200 OK
    def test_list_projects_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/projects")
        assert response.status_code == 200

    # Listar proyectos debe retornar objeto con clave projects 
    def test_list_projects_returns_projects_key(self, client, base_url):
        response = client.get(f"{base_url}/projects")
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)

    # Filtrar proyectos por estado debe retornar solo los del estado indicado
    def test_filter_projects_by_status(self, client, base_url):
        response = client.get(f"{base_url}/projects?status=active")
        assert response.status_code == 200
        data = response.json()
        for project in data["projects"]:
            assert project["status"] == "active"

    # ─────────────────────────────────────────
    # Obtener proyecto por ID
    # ─────────────────────────────────────────

    # Obtener proyecto por ID válido debe retornar 200
    def test_get_project_by_valid_id(self, client, base_url, created_project):
        response = client.get(f"{base_url}/projects/{created_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_project["id"]

    # Obtener proyecto con ID inexistente debe retornar 404
    def test_get_project_by_invalid_id_returns_404(self, client, base_url):
        response = client.get(f"{base_url}/projects/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    # ─────────────────────────────────────────
    # Actualizar proyecto
    # ─────────────────────────────────────────

    # Actualizar proyecto existente debe retornar 200
    def test_update_project_successfully(self, client, base_url, created_project):
        payload = {"name": "Proyecto Actualizado"}
        response = client.put(f"{base_url}/projects/{created_project['id']}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Proyecto Actualizado"

    # Actualizar proyecto con ID inexistente debe retornar 404
    def test_update_project_invalid_id_returns_404(self, client, base_url):
        payload = {"name": "Proyecto Actualizado"}
        response = client.put(f"{base_url}/projects/00000000-0000-0000-0000-000000000000", json=payload)
        assert response.status_code == 404

    # ─────────────────────────────────────────
    # Eliminar proyecto
    # ─────────────────────────────────────────

    # Eliminar proyecto existente debe retornar 200
    def test_delete_project_successfully(self, client, base_url, created_user):
        payload = {
            "name": f"Proyecto_delete_{uuid.uuid4().hex[:8]}",
            "owner_id": created_user["id"]
        }
        create_response = client.post(f"{base_url}/projects", json=payload)
        project_id = create_response.json()["id"]
        response = client.delete(f"{base_url}/projects/{project_id}")
        assert response.status_code == 200

    # Eliminar proyecto con ID inexistente debe retornar 404
    def test_delete_project_invalid_id_returns_404(self, client, base_url):
        response = client.delete(f"{base_url}/projects/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404