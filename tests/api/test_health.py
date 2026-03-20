import pytest

# Tests para el endpoint de health check
class TestHealth:

    # Verificar que el endpoint de health check responde con 200 OK
    def test_health_check_returns_200(self, client, base_url):
        response = client.get(f"{base_url}/health")
        assert response.status_code == 200

    # Verificar que el health check retorna un status "healthy"
    def test_health_check_returns_healthy_status(self, client, base_url):
        response = client.get(f"{base_url}/health")
        data = response.json()
        assert data["status"] == "healthy"

    # Verificar que el health check retorna la versión de la aplicación
    def test_health_check_returns_version(self, client, base_url):
        response = client.get(f"{base_url}/health")
        data = response.json()
        assert "version" in data

    # Verificar que el health check retorna el entorno de ejecución
    def test_health_check_returns_environment(self, client, base_url):
        response = client.get(f"{base_url}/health")
        data = response.json()
        assert "environment" in data