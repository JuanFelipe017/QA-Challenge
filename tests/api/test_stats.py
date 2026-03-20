import pytest

# Tests para el módulo de estadísticas
class TestStats:

    # Obtenemos estadísticas para verificar su estructura y contenido
    def test_get_stats_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/stats")
        assert response.status_code == 200

    # Las estadísticas deben incluir el total de tareas
    def test_get_stats_returns_total_tasks(self, client, base_url):
        response = client.get(f"{base_url}/stats")
        data = response.json()
        assert "total_tasks" in data
        assert isinstance(data["total_tasks"], int)

    # Las estadísticas deben incluir conteo por estado
    def test_get_stats_returns_by_status(self, client, base_url):
        response = client.get(f"{base_url}/stats")
        data = response.json()
        assert "by_status" in data
        assert isinstance(data["by_status"], dict)

    # Las estadísticas deben incluir conteo por prioridad
    def test_get_stats_returns_by_priority(self, client, base_url):
        response = client.get(f"{base_url}/stats")
        data = response.json()
        assert "by_priority" in data
        assert isinstance(data["by_priority"], dict)

    # Las estadísticas deben incluir tareas vencidas
    def test_get_stats_returns_overdue(self, client, base_url):
        response = client.get(f"{base_url}/stats")
        data = response.json()
        assert "overdue" in data
        assert isinstance(data["overdue"], int)

    # El total en stats debe coincidir con el total de tareas.
    def test_stats_total_matches_tasks(self, client, base_url):
        stats_response = client.get(f"{base_url}/stats")
        tasks_response = client.get(f"{base_url}/tasks")
        stats_total = stats_response.json()["total_tasks"]
        tasks_total = tasks_response.json()["total"]
        assert stats_total == tasks_total