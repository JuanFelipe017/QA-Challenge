# 📋 Plan de Pruebas — TaskFlow

> **Aplicación:** TaskFlow v1.2.0  
> **Fecha:** 2026-03-19  
> **Tester:** Juan Felipe Vanegas Silva
> **Entorno:** Local — Docker (http://localhost:8080)  

---

## 1. Alcance

### ✅ Qué se prueba

- API REST completa (todos los endpoints documentados en Swagger)
- Frontend web (flujos principales de usuario)
- Validaciones de datos de entrada
- Integridad referencial entre entidades
- Flujo de estados de tareas
- Exportación de datos (JSON y CSV)
- Estadísticas y métricas
- Seguridad básica (inyección, CORS, rate limiting, exposición de datos)

### ❌ Qué NO se prueba

- Rendimiento bajo carga masiva (fuera del alcance de esta iteración)
- Compatibilidad con navegadores distintos a Chrome
- Accesibilidad (WCAG)
- Internacionalización / localización
- Autenticación y autorización (la app no implementa auth)

---

## 2. Estrategia de Pruebas

| Tipo | Descripción | Herramienta |
|---|---|---|
| Pruebas funcionales API | Validar cada endpoint con casos felices y edge cases | pytest + requests |
| Pruebas de UI / E2E | Flujos principales desde el navegador | Playwright |
| Pruebas de seguridad | Inyección, exposición de datos, CORS | Manual + pytest |
| Pruebas de exploración | Bug hunting manual sobre API y frontend | Manual (Swagger + browser) |

---

## 3. Matriz de Riesgos

| Área | Riesgo | Probabilidad | Impacto | Prioridad |
|---|---|---|---|---|
| Validación de datos | Datos corruptos en BD por falta de validación | Alta | Alto | P1 |
| Integridad referencial | Tareas con usuarios/proyectos inexistentes | Alta | Alto | P1 |
| Seguridad | Exposición de errores internos de BD | Media | Alto | P1 |
| Flujo de estados | Transiciones de estado inválidas | Media | Alto | P1 |
| Email | Formato de email no validado | Alta | Medio | P2 |
| Exportación | Datos incorrectos o incompletos en CSV/JSON | Media | Medio | P2 |
| Estadísticas | Métricas incorrectas por datos corruptos | Media | Medio | P2 |
| Documentación | Schema de Swagger desactualizado | Alta | Bajo | P3 |
| Paginación | Comportamiento incorrecto con filtros combinados | Baja | Medio | P3 |

---

## 4. Casos de Prueba

### Módulo: Health

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-001 | Health check retorna 200 | App levantada | GET /api/health | N/A | 200 OK con `{"status": "healthy"}` | P1 |

---

### Módulo: Users

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-002 | Crear usuario válido | Ninguna | POST /api/users con datos válidos | `{"username":"juan","full_name":"Juan Test","email":"juan@test.com","role":"admin"}` | 201 Created con objeto usuario | P1 |
| TC-003 | Crear usuario con email duplicado | Usuario con ese email existe | POST /api/users con mismo email | Email ya registrado | 400/409 con mensaje de error | P1 |
| TC-004 | Crear usuario con email inválido | Ninguna | POST /api/users con email sin formato | `email: "estonoesuncorreo"` | 422 con error de validación de email | P1 |
| TC-005 | Crear usuario con campos vacíos | Ninguna | POST /api/users con strings vacíos | `username: "", full_name: "", email: ""` | 422 con errores de validación | P1 |
| TC-006 | Crear usuario con rol inválido | Ninguna | POST /api/users con rol inexistente | `role: "superadmin"` | 422 con mensaje amigable de error | P2 |
| TC-007 | Listar todos los usuarios | Al menos 1 usuario existe | GET /api/users | N/A | 200 con lista de usuarios | P1 |
| TC-008 | Obtener usuario por ID válido | Usuario existe | GET /api/users/{id} | ID existente | 200 con objeto usuario | P1 |
| TC-009 | Obtener usuario por ID inexistente | Ninguna | GET /api/users/{id} | ID no existente | 404 Not Found | P1 |
| TC-010 | Desactivar usuario existente | Usuario activo existe | DELETE /api/users/{id} | ID existente | 200 con confirmación | P1 |
| TC-011 | Desactivar usuario inexistente | Ninguna | DELETE /api/users/{id} | ID no existente | 404 Not Found | P2 |

---

### Módulo: Projects

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-012 | Crear proyecto válido | Usuario existe como owner | POST /api/projects con datos válidos | `{"name":"Proyecto Test","owner_id":"<uuid-valido>"}` | 201 Created con objeto proyecto | P1 |
| TC-013 | Crear proyecto sin owner_id | Ninguna | POST /api/projects sin owner_id | `{"name":"Proyecto Test"}` | 422 campo requerido | P1 |
| TC-014 | Crear proyecto con owner_id inexistente | Ninguna | POST /api/projects con owner_id falso | `owner_id: "00000000-0000-0000-0000-000000000000"` | 404 Owner not found | P1 |
| TC-015 | Listar proyectos | Al menos 1 proyecto existe | GET /api/projects | N/A | 200 con lista de proyectos | P1 |
| TC-016 | Filtrar proyectos por estado | Proyectos con distintos estados | GET /api/projects?status=active | `status=active` | 200 solo con proyectos activos | P2 |
| TC-017 | Actualizar proyecto existente | Proyecto existe | PUT /api/projects/{id} | Datos válidos de actualización | 200 con proyecto actualizado | P1 |
| TC-018 | Eliminar proyecto existente | Proyecto existe | DELETE /api/projects/{id} | ID existente | 200 con confirmación | P1 |
| TC-019 | Obtener proyecto inexistente | Ninguna | GET /api/projects/{id} | ID no existente | 404 Not Found | P2 |

---

### Módulo: Tasks

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-020 | Crear tarea válida | Proyecto y usuario existen | POST /api/tasks con datos válidos | `{"title":"Tarea","project_id":"<uuid>","reporter_id":"<uuid>","priority":"high"}` | 201 Created con objeto tarea | P1 |
| TC-021 | Crear tarea con project_id inexistente | Ninguna | POST /api/tasks con project_id falso | `project_id: "00000000-..."` | 404 Project not found | P1 |
| TC-022 | Crear tarea con reporter_id inexistente | Proyecto existe | POST /api/tasks con reporter_id falso | `reporter_id: "00000000-..."` | 404 User not found | P1 |
| TC-023 | Crear tarea con assignee_id inexistente | Proyecto existe | POST /api/tasks con assignee_id falso | `assignee_id: "00000000-..."` | 404 User not found | P1 |
| TC-024 | Listar tareas con paginación | Al menos 10 tareas existen | GET /api/tasks?page=1&limit=5 | `page=1, limit=5` | 200 con máximo 5 tareas | P2 |
| TC-025 | Filtrar tareas por estado | Tareas con distintos estados | GET /api/tasks?status=todo | `status=todo` | 200 solo con tareas en estado todo | P2 |
| TC-026 | Buscar tareas por título | Tareas existentes | GET /api/tasks?search=texto | `search=implementar` | 200 con tareas que contengan el texto | P2 |
| TC-027 | Actualizar estado de tarea | Tarea existe | PUT /api/tasks/{id} con nuevo status | `status: "in_progress"` | 200 con tarea actualizada | P1 |
| TC-028 | Eliminar tarea existente | Tarea existe | DELETE /api/tasks/{id} | ID existente | 200 con confirmación | P1 |
| TC-029 | Obtener tarea inexistente | Ninguna | GET /api/tasks/{id} | ID no existente | 404 Not Found | P2 |

---

### Módulo: Comments

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-030 | Agregar comentario a tarea existente | Tarea y usuario existen | POST /api/tasks/{id}/comments | `{"content":"Comentario de prueba","author_id":"<uuid>"}` | 201 Created con objeto comentario | P1 |
| TC-031 | Listar comentarios de tarea | Tarea con comentarios existe | GET /api/tasks/{id}/comments | ID tarea existente | 200 con lista de comentarios | P1 |
| TC-032 | Agregar comentario a tarea inexistente | Ninguna | POST /api/tasks/{id}/comments | ID tarea no existente | 404 Task not found | P2 |
| TC-033 | Agregar comentario vacío | Tarea existe | POST /api/tasks/{id}/comments | `content: ""` | 422 campo requerido | P2 |

---

### Módulo: Stats

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-034 | Obtener estadísticas globales | Al menos 1 tarea existe | GET /api/stats | N/A | 200 con métricas correctas (total, por estado, por prioridad, vencidas) | P1 |
| TC-035 | Verificar coherencia de total con lista | Tareas existentes | GET /api/stats y GET /api/tasks | N/A | El total en stats debe coincidir con el total de tareas | P1 |

---

### Módulo: Export

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-036 | Exportar tareas en formato JSON | Al menos 1 tarea existe | GET /api/export/tasks?format=json | `format=json` | 200 con lista de tareas en JSON | P1 |
| TC-037 | Exportar tareas en formato CSV | Al menos 1 tarea existe | GET /api/export/tasks?format=csv | `format=csv` | 200 con contenido CSV válido | P1 |
| TC-038 | Exportar con formato inválido | Ninguna | GET /api/export/tasks?format=xml | `format=xml` | 400/422 con mensaje de error | P2 |

---

### Módulo: Bulk Update

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|---|---|---|---|---|---|---|
| TC-039 | Actualización masiva con IDs válidos | Al menos 2 tareas existen | POST /api/tasks/bulk-update con IDs válidos | Lista de IDs existentes + nuevo status | 200 con confirmación de actualización | P2 |
| TC-040 | Actualización masiva con IDs inválidos | Ninguna | POST /api/tasks/bulk-update con IDs falsos | Lista de IDs inexistentes | 404 o respuesta parcial indicando cuáles fallaron | P2 |

---

## 5. Priorización

| Prioridad | Descripción | Casos |
|---|---|---|
| **P1** | Crítico — debe pasar antes de ir a producción | TC-001 a TC-010, TC-012 a TC-015, TC-017, TC-018, TC-020 a TC-023, TC-027, TC-028, TC-030, TC-031, TC-034, TC-035, TC-036, TC-037 |
| **P2** | Alto — importante pero no bloqueante | TC-011, TC-016, TC-019, TC-024 a TC-026, TC-029, TC-032, TC-033, TC-038 a TC-040 |
| **P3** | Medio — mejora de calidad | Casos relacionados a documentación y mensajes de error |
| **P4** | Bajo — nice to have | Casos de UI y accesibilidad |