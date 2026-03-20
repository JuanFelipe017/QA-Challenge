import pytest

# Tests para el módulo de comentarios
class TestComments:

    # ─────────────────────────────────────────
    # Crear comentario
    # ─────────────────────────────────────────

    # Crear comentario válido
    def test_create_comment_successfully(self, client, base_url, created_task, created_user):
        payload = {
            "task_id": created_task["id"],
            "content": "Comentario de prueba",
            "author_id": created_user["id"]
        }
        response = client.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["content"] == "Comentario de prueba"

    # Crear comentario en tarea inexistente
    def test_create_comment_on_invalid_task_returns_404(self, client, base_url, created_user):
        payload = {
            "task_id": "00000000-0000-0000-0000-000000000000",
            "content": "Comentario en tarea inválida",
            "author_id": created_user["id"]
        }
        response = client.post(
            f"{base_url}/tasks/00000000-0000-0000-0000-000000000000/comments",
            json=payload
        )
        assert response.status_code == 404

    # Crear comentario con contenido vacío
    def test_create_comment_empty_content_returns_422(self, client, base_url, created_task, created_user):
        payload = {
            "content": "",
            "author_id": created_user["id"]
        }
        response = client.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)
        assert response.status_code == 422

    # Crear comentario sin author_id
    def test_create_comment_missing_author_returns_422(self, client, base_url, created_task):
        payload = {"content": "Comentario sin autor"}
        response = client.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)
        assert response.status_code == 422

    # ─────────────────────────────────────────
    # Listar comentarios
    # ─────────────────────────────────────────

    # Listar comentarios de tarea existente
    def test_list_comments_returns_200(self, client, base_url, created_task):
        response = client.get(f"{base_url}/tasks/{created_task['id']}/comments")
        assert response.status_code == 200

    # Listar comentaios debe retornar una lista
    def test_list_comments_returns_list(self, client, base_url, created_task):
        response = client.get(f"{base_url}/tasks/{created_task['id']}/comments")
        data = response.json()
        assert "comments" in data  
        assert isinstance(data["comments"], list)

    # Listar comentarios de tarea inexistente
    def test_list_comments_invalid_task_returns_404(self, client, base_url):
        response = client.get(
            f"{base_url}/tasks/00000000-0000-0000-0000-000000000000/comments"
        )
        assert response.status_code == 404

    # El comentario creado debe aparecer en la lista de la tarea correcta
    def test_comment_belongs_to_correct_task(self, client, base_url, created_task, created_user):
        payload = {
            "task_id": created_task["id"],
            "content": "Comentario de verificación",
            "author_id": created_user["id"]
        }
        client.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)
        response = client.get(f"{base_url}/tasks/{created_task['id']}/comments")
        data = response.json()
        contents = [c["content"] for c in data["comments"]]
        assert "Comentario de verificación" in contents