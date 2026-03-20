# 🐛 Bug Reports — TaskFlow

> **Aplicación:** TaskFlow v1.2.0  
> **Fecha de pruebas:** 2026-03-19  
> **Tester:** Juan Felipe Vanegas Silva
> **Entorno:** Local — Docker (http://localhost:8080)  

---

## Resumen

| ID | Título | Severidad | Componente | Estado |
|---|---|---|---|---|
| BUG-001 | Schema de Swagger incorrecto en múltiples endpoints | Baja | API / Documentación | Abierto |
| BUG-002 | Campos redundantes de nombre de usuario sin claridad | Media | API | Abierto |
| BUG-003 | No se valida el formato del email al crear usuario | Alta | API | Abierto |
| BUG-004 | Validaciones de longitud inconsistentes entre campos | Media | API | Abierto |
| BUG-005 | Error expone constraint interno de base de datos | Media | API / Seguridad | Abierto |
| BUG-006 | No se valida existencia de reporter_id ni assignee_id | Alta | API | Abierto |

---

### BUG-001: Schema de Swagger incorrecto en múltiples endpoints

- **Severidad:** Baja
- **Componente:** API / Documentación
- **Endpoint/Pantalla:** Todos los endpoints — Example Value en sección Responses
- **Precondiciones:** Aplicación levantada y Swagger accesible en http://localhost:8080/docs

**Pasos para reproducir:**
1. Abrir Swagger en http://localhost:8080/docs
2. Expandir cualquier endpoint (ej: `POST /api/users`, `GET /api/health`)
3. Revisar la sección "Responses" → "Example Value"

**Resultado actual:** El Example Value muestra `"string"` como respuesta esperada en endpoints que retornan objetos JSON complejos. Por ejemplo, `GET /api/health` retorna `{ "status": "healthy", "version": "1.2.0", "environment": "development" }` pero el schema documenta `"string"`.

**Resultado esperado:** El schema debería reflejar la estructura real del objeto retornado por cada endpoint.

**Evidencia:**
```json
// Swagger muestra:
"string"

// API retorna realmente:
{
  "status": "healthy",
  "version": "1.2.0",
  "environment": "development"
}
```

**Impacto:** Los desarrolladores que consuman la API basándose en la documentación de Swagger recibirán información incorrecta sobre la estructura de las respuestas, dificultando la integración.

**Sugerencia de fix:** Definir correctamente los modelos de respuesta (`response_model`) en cada endpoint de FastAPI para que Swagger los refleje automáticamente.

---

### BUG-002: Campos redundantes de nombre de usuario sin claridad

- **Severidad:** Media
- **Componente:** API
- **Endpoint/Pantalla:** `POST /api/users`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `POST /api/users` con solo el campo `name` vacío y un email válido
2. Observar el error de validación retornado

**Resultado actual:** El error de validación menciona dos campos distintos para el nombre: `username` (mínimo 3 caracteres) y `full_name` (mínimo 1 carácter). Ambos son requeridos y representan conceptos similares sin documentación clara de su diferencia. La respuesta exitosa también retorna ambos campos.

**Resultado esperado:** Debería existir un único campo para el nombre del usuario, o al menos documentación clara que explique la diferencia entre `username` y `full_name`.

**Evidencia:**
```json
// Error al enviar name vacío:
{
  "detail": [
    { "loc": ["body", "username"], "msg": "String should have at least 3 characters" },
    { "loc": ["body", "full_name"], "msg": "String should have at least 1 character" }
  ]
}

// Respuesta exitosa incluye ambos campos:
{
  "id": "f1f53918-...",
  "username": "juantest",
  "full_name": "Juan Test",
  ...
}
```

**Impacto:** Genera confusión en los consumidores de la API sobre qué campo usar. Puede ocasionar inconsistencias en la forma en que distintos clientes almacenan o muestran el nombre del usuario.

**Sugerencia de fix:** Unificar en un solo campo `full_name` o documentar claramente la diferencia y el propósito de cada uno.

---

### BUG-003: No se valida el formato del email al crear usuario

- **Severidad:** Alta
- **Componente:** API
- **Endpoint/Pantalla:** `POST /api/users`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `POST /api/users` con el siguiente body:
```json
{
  "username": "test2",
  "full_name": "Test Dos",
  "email": "estonoesuncorreo",
  "role": "admin"
}
```
2. Observar la respuesta

**Resultado actual:** La API acepta y guarda el usuario con el email `"estonoesuncorreo"` sin ningún error de validación. Retorna `201 Created` con el dato corrupto almacenado.

**Resultado esperado:** La API debería retornar un error `422 Unprocessable Entity` indicando que el formato del email es inválido.

**Evidencia:**
```json
// Request:
{ "username": "test2", "full_name": "Test Dos", "email": "estonoesuncorreo", "role": "admin" }

// Response 201:
{
  "id": "3dd13cda-48cd-4ad1-9b51-fbde83a8409c",
  "username": "test2",
  "email": "estonoesuncorreo",
  ...
}
```

**Impacto:** Permite almacenar datos corruptos en la base de datos. Los correos de recuperación de contraseña, notificaciones, y cualquier comunicación por email fallarán para estos usuarios. Afecta la integridad de los datos.

**Sugerencia de fix:** Usar validación de tipo `EmailStr` de Pydantic en el modelo de entrada para forzar el formato correcto del email.

---

### BUG-004: Validaciones de longitud inconsistentes entre campos

- **Severidad:** Media
- **Componente:** API
- **Endpoint/Pantalla:** `POST /api/users`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `POST /api/users` con campos vacíos:
```json
{
  "username": "",
  "full_name": "",
  "email": "",
  "role": "admin"
}
```
2. Observar el mensaje de validación

**Resultado actual:** Las validaciones son inconsistentes:
- `username`: mínimo **3 caracteres**
- `full_name`: mínimo **1 carácter**

Un nombre completo de 1 carácter no representa un nombre real de persona.

**Resultado esperado:** Ambos campos deberían tener validaciones coherentes con su propósito. `full_name` debería requerir al menos 2-3 caracteres.

**Evidencia:**
```json
{
  "detail": [
    { "loc": ["body", "username"], "msg": "String should have at least 3 characters", "ctx": { "min_length": 3 } },
    { "loc": ["body", "full_name"], "msg": "String should have at least 1 character", "ctx": { "min_length": 1 } }
  ]
}
```

**Impacto:** Permite registrar usuarios con nombres de una sola letra como `"A"`, lo que genera datos de baja calidad y puede afectar funcionalidades que dependan del nombre completo.

**Sugerencia de fix:** Establecer `min_length=2` o `min_length=3` para `full_name`, consistente con `username`.

---

### BUG-005: Error expone constraint interno de base de datos

- **Severidad:** Media
- **Componente:** API / Seguridad
- **Endpoint/Pantalla:** `POST /api/users`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `POST /api/users` con un rol inválido:
```json
{
  "username": "testuser",
  "full_name": "Test User",
  "email": "test@test.com",
  "role": "superadmin"
}
```
2. Observar el mensaje de error

**Resultado actual:** La API retorna el mensaje de error interno de SQLite:
```json
{ "detail": "CHECK constraint failed: role IN ('admin', 'member', 'viewer')" }
```

**Resultado esperado:** Un mensaje de error amigable y sin información interna:
```json
{ "detail": "Rol inválido. Los valores permitidos son: admin, member, viewer." }
```

**Evidencia:**
```
Response 500:
{ "detail": "CHECK constraint failed: role IN ('admin', 'member', 'viewer')" }
```

**Impacto:** Expone detalles de la implementación interna de la base de datos (tipo de BD, nombre de constraints, valores permitidos). Un atacante puede usar esta información para mapear la estructura de la base de datos. Clasificado también como hallazgo de seguridad.

**Sugerencia de fix:** Validar el campo `role` a nivel de Pydantic antes de llegar a la base de datos, retornando un mensaje de error controlado.

---

### BUG-006: No se valida existencia de reporter_id ni assignee_id al crear tareas

- **Severidad:** Alta
- **Componente:** API
- **Endpoint/Pantalla:** `POST /api/tasks`
- **Precondiciones:** Al menos un proyecto existente en la base de datos

**Pasos para reproducir:**
1. Obtener un `project_id` válido con `GET /api/projects`
2. Hacer `POST /api/tasks` con `reporter_id` y `assignee_id` inexistentes:
```json
{
  "title": "Tarea de prueba",
  "project_id": "4e8f9df8-d7c4-4906-91c1-5efb0bb1f447",
  "reporter_id": "00000000-0000-0000-0000-000000000000",
  "assignee_id": "00000000-0000-0000-0000-000000000000",
  "priority": "high"
}
```
3. Observar la respuesta

**Resultado actual:** La tarea se crea exitosamente con `201 Created` aunque `reporter_id` y `assignee_id` no correspondan a usuarios existentes. La tarea queda con referencias a usuarios fantasma en la base de datos.

**Resultado esperado:** La API debería retornar `404 Not Found` indicando que el usuario referenciado no existe, igual que lo hace con `project_id` inválido.

**Evidencia:**
```json
// Con project_id inválido → Error correcto:
{ "detail": "Project not found" }

// Con reporter_id inválido → Se crea igual:
{
  "id": "6e2aaf24-...",
  "reporter_id": "00000000-0000-0000-0000-000000000000",
  ...
}
```

**Impacto:** Genera inconsistencia de datos en la base de datos — tareas asignadas a usuarios que no existen. Puede causar errores en funcionalidades que intenten resolver el nombre del reporter o assignee, estadísticas incorrectas, y problemas en la exportación de datos.

**Sugerencia de fix:** Agregar validación de existencia para `reporter_id` y `assignee_id` antes de crear la tarea, similar a la validación que ya existe para `project_id`.

---

### BUG-007: Estadísticas incluyen tareas con datos corruptos sin advertencia

- **Severidad:** Media
- **Componente:** API
- **Endpoint/Pantalla:** `GET /api/stats`
- **Precondiciones:** Existir tareas con reporter_id o assignee_id inexistentes

**Pasos para reproducir:**
1. Crear una tarea con `reporter_id` inexistente (ver BUG-006)
2. Hacer `GET /api/stats`
3. Observar el total de tareas

**Resultado actual:** Las estadísticas incluyen en el conteo total las tareas con referencias a usuarios inexistentes, sin ningún tipo de advertencia o distinción. El campo `total_tasks` refleja todas las tareas incluyendo las corruptas.

**Resultado esperado:** Las estadísticas deberían excluir tareas con datos de integridad comprometida, o al menos incluir un campo adicional que indique cuántas tareas tienen datos inconsistentes.

**Evidencia:**
```json
{
  "total_tasks": 20,
  "by_status": { "todo": 10, ... }
}
// Incluye 2 tareas creadas con reporter_id "00000000-..." inexistente
```

**Impacto:** Las métricas del dashboard pueden ser incorrectas o engañosas para el equipo. Decisiones de negocio basadas en estas estadísticas podrían ser erróneas.

**Sugerencia de fix:** Agregar validación al calcular estadísticas para excluir tareas con referencias inválidas, o agregar un endpoint de diagnóstico de integridad de datos.

---

### BUG-008: No se valida existencia de owner_id al crear proyectos

- **Severidad:** Alta
- **Componente:** API
- **Endpoint/Pantalla:** `POST /api/projects`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `POST /api/projects` con un `owner_id` inexistente:
```json
{
  "name": "Proyecto owner inválido",
  "owner_id": "00000000-0000-0000-0000-000000000000"
}
```
2. Observar la respuesta

**Resultado actual:** El proyecto se crea exitosamente con `201 Created` aunque el `owner_id` no corresponda a ningún usuario existente en la base de datos.

**Resultado esperado:** La API debería retornar `404 Not Found` indicando que el usuario referenciado como owner no existe, igual que lo hace con `project_id` inválido en tareas.

**Evidencia:**
```json
// Request con owner_id inexistente:
{ "name": "Proyecto owner inválido", "owner_id": "00000000-0000-0000-0000-000000000000" }

// Response 201 — debería ser 404:
{ "id": "...", "name": "Proyecto owner inválido", "owner_id": "00000000-...", ... }
```

**Impacto:** Genera proyectos huérfanos sin dueño válido. Puede causar errores en funcionalidades que intenten resolver el nombre del owner, y afecta la integridad referencial de la base de datos. Relacionado con BUG-006.

**Sugerencia de fix:** Agregar validación de existencia para `owner_id` antes de crear el proyecto, similar a la validación que ya existe para `project_id` en tareas.

---

### BUG-009: El parámetro limit es ignorado en la paginación de tareas

- **Severidad:** Media
- **Componente:** API
- **Endpoint/Pantalla:** `GET /api/tasks`
- **Precondiciones:** Al menos 6 tareas existentes

**Pasos para reproducir:**
1. Hacer `GET /api/tasks?limit=5`
2. Contar las tareas retornadas

**Resultado actual:** La API retorna todas las tareas ignorando el parámetro `limit`.

**Resultado esperado:** La API debería retornar máximo 5 tareas.

**Evidencia:**
```
GET /api/tasks?limit=5 → retorna 20 tareas
```

**Impacto:** La paginación no funciona, lo que puede causar problemas de rendimiento al retornar grandes volúmenes de datos innecesariamente.

**Sugerencia de fix:** Implementar correctamente el parámetro `limit` en el query de la base de datos.

---

### BUG-010: El endpoint de comentarios requiere task_id en el body y en la URL simultáneamente

- **Severidad:** Baja
- **Componente:** API
- **Endpoint/Pantalla:** `POST /api/tasks/{task_id}/comments`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `POST /api/tasks/{id}/comments` sin incluir `task_id` en el body
2. Observar el error

**Resultado actual:** El endpoint retorna 422 si no se incluye `task_id` en el body, aunque ya está en la URL.

**Resultado esperado:** El `task_id` debería tomarse de la URL automáticamente, sin requerirlo también en el body.

**Impacto:** Genera confusión y trabajo innecesario para los consumidores de la API.

**Sugerencia de fix:** Eliminar `task_id` del body del request y tomarlo directamente del path parameter.

---

### BUG-011: La exportación acepta formatos inválidos sin retornar error

- **Severidad:** Baja
- **Componente:** API
- **Endpoint/Pantalla:** `GET /api/export/tasks`
- **Precondiciones:** Ninguna

**Pasos para reproducir:**
1. Hacer `GET /api/export/tasks?format=xml`
2. Observar la respuesta

**Resultado actual:** La API retorna 200 con datos en vez de rechazar el formato inválido.

**Resultado esperado:** Debería retornar 400 o 422 indicando que el formato no es soportado.

**Evidencia:**
```
GET /api/export/tasks?format=xml → 200 OK
```

**Impacto:** El cliente no recibe feedback sobre formatos no soportados, lo que puede generar confusión.

**Sugerencia de fix:** Validar el parámetro `format` y retornar error si no es `json` o `csv`.