import pytest
import uuid

# Tests para el endpoint de usuarios
class TestUsers:

    # ─────────────────────────────────────────
    # Crear usuario
    # ─────────────────────────────────────────

    # Verificar que se puede crear un usuario con datos válidos
    def test_create_user_successfully(self, client, base_url):
        unique = uuid.uuid4().hex[:8]
        payload = {
            "username": f"newuser_{unique}",
            "full_name": "New User",
            "email": f"newuser_{unique}@test.com",
            "role": "member"
        }
        response = client.post(f"{base_url}/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == f"newuser_{unique}@test.com" 
        assert data["username"] == f"newuser_{unique}"      
        assert "id" in data
        client.delete(f"{base_url}/users/{data['id']}") # Cleanup: eliminar el usuario creado después del test

    # Verificar que no se puede crear un usuario con email duplicado
    def test_create_user_duplicate_email_returns_error(self, client, base_url, created_user):
        payload = {
            "username": "otheruser",
            "full_name": "Other User",
            "email": created_user["email"],
            "role": "member"
        }
        response = client.post(f"{base_url}/users", json=payload)
        assert response.status_code in [400, 409, 422]

    # Crear usuario con email inválido debe retornar 422 — este test documenta el bug identificado como BUG-003
    def test_create_user_invalid_email_format(self, client, base_url):
        """Crear usuario con email inválido debe retornar 422 — BUG-003."""
        payload = {
            "username": "buguser",
            "full_name": "Bug User",
            "email": "estonoesuncorreo",
            "role": "member"
        }
        response = client.post(f"{base_url}/users", json=payload)
        # BUG-003: La API acepta emails inválidos — este test documenta el bug
        # Resultado esperado: 422, Resultado actual: 201
        assert response.status_code != 201, (
            "BUG-003: La API debería rechazar emails con formato inválido"
        )

    # Verificar que no se puede crear un usuario con campos vacíos
    def test_create_user_empty_fields_returns_422(self, client, base_url):
        payload = {
            "username": "",
            "full_name": "",
            "email": "",
            "role": "admin"
        }
        response = client.post(f"{base_url}/users", json=payload)
        assert response.status_code == 422

    # Verificar que no se puede crear un usuario con rol inválido
    def test_create_user_invalid_role_returns_error(self, client, base_url):
        payload = {
            "username": "roleuser",
            "full_name": "Role User",
            "email": "roleuser@test.com",
            "role": "superadmin"
        }
        response = client.post(f"{base_url}/users", json=payload)
        assert response.status_code in [400, 422, 500]

    # Verificar que no se puede crear un usuario sin campos requeridos
    def test_create_user_missing_required_fields(self, client, base_url):
        payload = {"role": "member"}
        response = client.post(f"{base_url}/users", json=payload)
        assert response.status_code == 422

    # ─────────────────────────────────────────
    # Listar usuarios
    # ─────────────────────────────────────────

    # Listar usuarios debe retornar 200 OK
    def test_list_users_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/users")
        assert response.status_code == 200

    # Listar usuarios debe retornar una lista
    def test_list_users_returns_list(self, client, base_url):
        response = client.get(f"{base_url}/users")
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)

    # ─────────────────────────────────────────
    # Obtener usuario por ID
    # ─────────────────────────────────────────

    # Obtener usuario por ID válido debe retornar 200 OK
    def test_get_user_by_valid_id(self, client, base_url, created_user):
        response = client.get(f"{base_url}/users/{created_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]

    # Obtener usuario con ID inexistente debe retornar 404
    def test_get_user_by_invalid_id_returns_404(self, client, base_url):
        response = client.get(f"{base_url}/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    # ─────────────────────────────────────────
    # Desactivar usuario
    # ─────────────────────────────────────────

    # Desactivar un usuario existente debe retornar 200
    def test_delete_user_successfully(self, client, base_url):
        unique = uuid.uuid4().hex[:8]
        payload = {
            "username": f"todelete_{unique}",
            "full_name": "To Delete",
            "email": f"todelete_{unique}@test.com",
            "role": "member"
        }
        create_response = client.post(f"{base_url}/users", json=payload)
        user_id = create_response.json()["id"]

        response = client.delete(f"{base_url}/users/{user_id}")
        assert response.status_code == 200

    # Desactivar usuario con ID inexistente debe retornar 404
    def test_delete_user_invalid_id_returns_404(self, client, base_url):
        response = client.delete(f"{base_url}/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404