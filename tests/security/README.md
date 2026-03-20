# 🔒 Hallazgos de Seguridad — TaskFlow

Análisis de seguridad básica realizado sobre la API REST de TaskFlow v1.2.0.

**Fecha:** 2026-03-19  
**Tester:** Juan Felipe Vanegas Silva
**Entorno:** Local — Docker (http://localhost:8080)

---

## Resumen

| # | Hallazgo | Severidad | Estado |
|---|---|---|---|
| SEC-001 | Exposición de errores internos de base de datos | Media | Abierto |
| SEC-002 | Sin validación de formato de email | Alta | Abierto |
| SEC-003 | CORS configurado con wildcard (*) | Media | Abierto |
| SEC-004 | Sin rate limiting en ningún endpoint | Alta | Abierto |

---

## SEC-001: Exposición de errores internos de base de datos

**Severidad:** Media

**Descripción:** Cuando se envía un valor inválido para el campo `role`, la API retorna el mensaje de error interno de SQLite directamente al cliente, exponiendo detalles de la implementación interna.

**Evidencia:**
```
POST /api/users con role: "superadmin"

Response:
{ "detail": "CHECK constraint failed: role IN ('admin', 'member', 'viewer')" }
```

**Riesgo:** Un atacante puede usar esta información para mapear la estructura interna de la base de datos, conocer el tipo de BD utilizada (SQLite), y los valores permitidos de cada campo. Esta información puede usarse para diseñar ataques más precisos.

**Recomendación:** Capturar las excepciones de base de datos a nivel de aplicación y retornar mensajes de error genéricos y controlados al cliente.

---

## SEC-002: Sin validación de formato de email

**Severidad:** Alta

**Descripción:** El endpoint `POST /api/users` acepta cualquier string como email sin validar que tenga formato válido. Esto permite insertar datos maliciosos o malformados en la base de datos.

**Evidencia:**
```
POST /api/users con email: "estonoesuncorreo"
Response: 201 Created — usuario creado con email inválido
```

**Riesgo:** Además del problema de integridad de datos, un campo de email sin validación puede ser vulnerable a inyección si el valor se usa en queries o en el envío de correos. También permite crear cuentas con datos falsos que evaden validaciones de negocio.

**Recomendación:** Usar validación de tipo `EmailStr` de Pydantic para forzar el formato correcto del email antes de procesarlo.

---

## SEC-003: CORS configurado con wildcard (*)

**Severidad:** Media

**Descripción:** Los response headers de la API incluyen `access-control-allow-origin: *`, lo que significa que cualquier dominio puede hacer peticiones a la API desde el navegador.

**Evidencia:**
```
Response headers de cualquier endpoint:
access-control-allow-origin: *
access-control-allow-credentials: true
```

**Riesgo:** Con CORS abierto a todos los dominios, cualquier sitio web malicioso puede hacer peticiones a la API desde el navegador de un usuario. La combinación de `allow-origin: *` con `allow-credentials: true` es especialmente peligrosa y está explícitamente prohibida por la especificación CORS.

**Recomendación:** Restringir `Access-Control-Allow-Origin` a los dominios específicos que necesiten acceder a la API. Nunca combinar `*` con `allow-credentials: true`.

---

## SEC-004: Sin rate limiting en ningún endpoint

**Severidad:** Alta

**Descripción:** La API no implementa ningún mecanismo de rate limiting. Es posible hacer un número ilimitado de peticiones sin ser bloqueado o throttled.

**Evidencia:**
```bash
# Se pueden hacer cientos de peticiones sin restricción
for i in {1..100}; do curl http://localhost:8080/api/health; done
# Todas retornan 200 sin ningún error de límite
```

**Riesgo:** Sin rate limiting la API es vulnerable a ataques de fuerza bruta (intentos masivos de credenciales), ataques de denegación de servicio (DoS), y scraping masivo de datos. Un atacante podría intentar credenciales de forma automatizada sin ningún impedimento.

**Recomendación:** Implementar rate limiting a nivel de aplicación usando librerías como `slowapi` para FastAPI, o a nivel de infraestructura con un reverse proxy como nginx o un API Gateway.