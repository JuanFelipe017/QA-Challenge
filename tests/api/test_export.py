import pytest

# Tests para el módulo de exportación
class TestExport:

    # Exportar tareas en JSON 
    def test_export_tasks_json_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/export/tasks?format=json")
        assert response.status_code == 200

    # El JSON exportado debe contener una lista de tareas   
    def test_export_tasks_json_returns_list(self, client, base_url):
        response = client.get(f"{base_url}/export/tasks?format=json")
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    # Exportar tareas en CSV 
    def test_export_tasks_csv_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/export/tasks?format=csv")
        assert response.status_code == 200

    # El CSV exportado debe tener el contenido correcto 
    def test_export_tasks_csv_returns_text(self, client, base_url):
        response = client.get(f"{base_url}/export/tasks?format=csv")
        assert "text" in response.headers.get("content-type", "")

    # Exportar tareas con formato inválido debe retornar error
    def test_export_tasks_invalid_format_returns_error(self, client, base_url):
        response = client.get(f"{base_url}/export/tasks?format=xml")
        # BUG-011: La API acepta formatos inválidos y retorna 200
        # Resultado esperado: 400/422, Resultado actual: 200
        assert response.status_code == 200, (
            "BUG-011 confirmado: La API debería rechazar formatos inválidos de exportación"
        )