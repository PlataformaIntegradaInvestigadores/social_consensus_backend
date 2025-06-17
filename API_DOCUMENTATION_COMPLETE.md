# 📚 Documentación Completa de API - Sistema de Consenso Social

## 🏗️ Arquitectura del Sistema

El sistema integra múltiples módulos:
- **Autenticación Dual**: Investigadores y Empresas
- **Sistema de Consenso**: Debates y votaciones académicas  
- **Sistema de Jobs**: Publicación y postulación de trabajos
- **Feed Social**: Posts, comentarios y likes
- **Recomendaciones con IA**: Vectores de embedding para personalización

### Tecnologías Clave
- **pgvector**: Para búsquedas de similitud vectorial
- **Django REST Framework**: API REST
- **JWT**: Autenticación
- **WebSockets**: Tiempo real
- **Redis**: Cache y mensajería
- **PostgreSQL**: Base de datos principal

---

## 🔐 Base URL y Autenticación

### Base URL
```
http://localhost:8000/api/v1/
```

### Autenticación
Todas las APIs protegidas requieren el header:
```
Authorization: Bearer {access_token}
```

---

## 👨‍🔬 SISTEMA DE USUARIOS

### 1. Registro de Investigador
```http
POST /api/register/
```

**Request Body:**
```json
{
    "first_name": "Juan",
    "last_name": "Pérez",
    "username": "juan.perez@universidad.edu",
    "scopus_id": "12345678901",
    "password": "miPasswordSeguro123",
    "investigation_camp": "Computer Science",
    "institution": "Universidad Nacional",
    "interests": "machine learning, artificial intelligence, data science"
}
```

**Response Success (201):**
```json
{
    "id": "abcd123456",
    "first_name": "Juan",
    "last_name": "Pérez", 
    "username": "juan.perez@universidad.edu",
    "scopus_id": "12345678901",
    "investigation_camp": "Computer Science",
    "institution": "Universidad Nacional",
    "job_recommendations_embedding": null,
    "feed_recommendations_embedding": null,
    "profile_vector_updated_at": null,
    "interaction_count": 0
}
```

### 2. Registro de Empresa
```http
POST /api/company/register/
```

**Request Body:**
```json
{
    "company_name": "TechCorp S.A.",
    "username": "contact@techcorp.com",
    "password": "companyPassword123",
    "industry": "Software Development",
    "company_size": "medium",
    "website": "https://techcorp.com",
    "description": "Empresa líder en desarrollo de software"
}
```

### 3. Login Unificado
```http
POST /api/token/
```

**Request Body:**
```json
{
    "username": "usuario@email.com",
    "password": "password123"
}
```

**Response Success (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": "abcd123456",
    "user_type": "user" // o "company"
}
```

---

## 💼 SISTEMA DE JOBS

### 1. Listar Jobs
```http
GET /api/v1/jobs/
```

**Query Parameters:**
- `q`: Búsqueda de texto (título, descripción, empresa)
- `location`: Filtro por ubicación
- `type`: Tipo de trabajo (full_time, part_time, contract, internship, freelance)
- `experience`: Nivel de experiencia (entry, junior, mid, senior, lead)
- `remote`: Trabajo remoto (true/false)

**Example:**
```http
GET /api/v1/jobs/?q=python&remote=true&experience=mid
```

**Response Success (200):**
```json
[
    {
        "id": 1,
        "title": "Senior Python Developer",
        "description": "Desarrollador Python con experiencia en Django...",
        "requirements": "3+ años de experiencia en Python, Django, PostgreSQL",
        "benefits": "Trabajo remoto, seguro médico, bonos",
        "location": "Madrid, España",
        "job_type": "full_time",
        "job_type_display": "Tiempo completo",
        "experience_level": "senior",
        "experience_display": "Senior (5+ años)",
        "salary_min": 45000.00,
        "salary_max": 65000.00,
        "status": "active",
        "is_remote": true,
        "application_deadline": "2025-07-15T23:59:59Z",
        "created_at": "2025-06-16T10:30:00Z",
        "updated_at": "2025-06-16T12:00:00Z",
        "view_count": 150,
        "application_count": 25,
        "interactions_score": 75.5,
        "company": {
            "id": "comp123",
            "company_name": "TechCorp S.A.",
            "industry": "Software Development",
            "website": "https://techcorp.com"
        }
    }
]
```

### 2. Obtener Job Específico
```http
GET /api/v1/jobs/{job_id}/
```

**Response:** Igual que el objeto individual del listado anterior.

### 3. Crear Job (Solo Empresas)
```http
POST /api/v1/jobs/
```

**Request Body:**
```json
{
    "title": "Senior Python Developer",
    "description": "Buscamos un desarrollador Python senior...",
    "requirements": "3+ años de experiencia en Python, Django",
    "benefits": "Trabajo remoto, seguro médico",
    "location": "Madrid, España",
    "job_type": "full_time",
    "experience_level": "senior",
    "salary_min": 45000.00,
    "salary_max": 65000.00,
    "is_remote": true,
    "application_deadline": "2025-07-15T23:59:59Z",
    "status": "active"
}
```

### 4. Actualizar Job (Solo Empresas Propietarias)
```http
PUT /api/v1/jobs/{job_id}/
```

**Request Body:** Igual que POST, todos los campos opcionales.

### 5. Eliminar Job (Solo Empresas Propietarias)
```http
DELETE /api/v1/jobs/{job_id}/
```

---

## 📝 SISTEMA DE POSTULACIONES

### 1. Postular a Job
```http
POST /api/v1/applications/
```

**Request Body:**
```json
{
    "job_id": 1,
    "cover_letter": "Estimados señores, me interesa mucho esta posición...",
    "resume": "archivo_cv.pdf" // File upload
}
```

### 2. Listar Mis Postulaciones
```http
GET /api/v1/applications/
```

**Response Success (200):**
```json
[
    {
        "id": 1,
        "job": {
            "id": 1,
            "title": "Senior Python Developer",
            "company": {
                "company_name": "TechCorp S.A."
            }
        },
        "status": "pending",
        "status_display": "Pendiente",
        "cover_letter": "Estimados señores...",
        "resume": "/media/resumes/archivo_cv.pdf",
        "applied_at": "2025-06-16T14:30:00Z",
        "updated_at": "2025-06-16T14:30:00Z"
    }
]
```

### 3. Ver Postulaciones de un Job (Solo Empresas)
```http
GET /api/v1/applications/?job_id={job_id}
```

---

## 🤖 SISTEMA DE RECOMENDACIONES

### 1. Recomendaciones de Jobs Personalizadas
```http
GET /api/v1/jobs/recommendations/
```

**Query Parameters:**
- `limit`: Número de recomendaciones (default: 10)

**Response Success (200):**
```json
{
    "recommendations": [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "description": "...",
            "company": {...},
            "recommendation_score": 0.92,
            "similarity": 0.87,
            "hours_old": 24.5,
            "recommendation_reason": "Coincide con tu experiencia en Python y Machine Learning"
        }
    ],
    "total_count": 10,
    "user_id": "abcd123456"
}
```

### 2. Jobs en Tendencia
```http
GET /api/v1/jobs/trending/
```

**Response Success (200):**
```json
{
    "trending_jobs": [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "trending_score": 85.6,
            "hours_old": 12.0,
            "view_count": 150,
            "application_count": 25
        }
    ],
    "total_count": 10
}
```

### 3. Actualizar Embeddings de Usuario
```http
POST /api/v1/users/update-embeddings/
```

**Request Body:**
```json
{
    "interests": "machine learning, python, django, data science",
    "skills": "Python, Django, PostgreSQL, Machine Learning",
    "experience_summary": "5 años desarrollando aplicaciones web con Python"
}
```

---

## 📱 FEED SOCIAL

### 1. Obtener Feed Personalizado
```http
GET /api/v1/feed/?feed_type=personalized&limit=20
```

**Query Parameters:**
- `feed_type`: personalized, trending, latest
- `limit`: Número de posts (default: 20)
- `cursor`: Para paginación

**Response Success (200):**
```json
{
    "posts": [
        {
            "id": "uuid-1234-5678",
            "author": {
                "id": "user123",
                "first_name": "Ana",
                "last_name": "García",
                "username": "ana.garcia@uni.edu",
                "profile_picture": "/media/profile_pictures/ana.jpg"
            },
            "content": "Acabo de publicar mi nuevo paper sobre Machine Learning...",
            "embedding": null,
            "likes_count": 15,
            "comments_count": 3,
            "views_count": 89,
            "shares_count": 2,
            "engagement_score": 25.4,
            "is_public": true,
            "is_pinned": false,
            "created_at": "2025-06-16T10:30:00Z",
            "updated_at": "2025-06-16T12:00:00Z",
            "tags": ["machine-learning", "research", "ai"],
            "files": [
                {
                    "id": "file123",
                    "file_type": "image",
                    "file_url": "/media/feed_posts/image1.jpg",
                    "file_name": "research_results.jpg"
                }
            ],
            "user_has_liked": false
        }
    ],
    "has_next": true,
    "next_cursor": "cursor_token_123",
    "total_count": 1
}
```

### 2. Crear Post
```http
POST /api/v1/posts/
```

**Request Body (multipart/form-data):**
```json
{
    "content": "¡Acabo de terminar mi investigación sobre IA!",
    "tags": ["ai", "research", "machine-learning"],
    "is_public": true,
    "files": [archivo1.jpg, archivo2.pdf] // File uploads
}
```

### 3. Feed con Filtros
```http
POST /api/v1/feed/
```

**Request Body:**
```json
{
    "feed_type": "personalized",
    "limit": 20,
    "cursor": null,
    "filters": {
        "tags": ["machine-learning", "ai"],
        "date_from": "2025-06-01T00:00:00Z",
        "date_to": "2025-06-16T23:59:59Z",
        "authors": ["user123", "user456"],
        "has_files": true,
        "content_type": "research"
    }
}
```

### 4. Posts en Tendencia
```http
GET /api/v1/feed/trending/?limit=10
```

### 5. Recomendaciones de Feed
```http
GET /api/v1/feed/recommendations/?limit=15
```

---

## 💬 INTERACCIONES SOCIALES

### 1. Dar Like a Post
```http
POST /api/v1/posts/{post_id}/like/
```

### 2. Quitar Like
```http
DELETE /api/v1/posts/{post_id}/like/
```

### 3. Comentar Post
```http
POST /api/v1/posts/{post_id}/comments/
```

**Request Body:**
```json
{
    "content": "¡Excelente investigación! Me encantó el enfoque metodológico.",
    "parent_comment": null // Para responder a otro comentario
}
```

### 4. Listar Comentarios
```http
GET /api/v1/posts/{post_id}/comments/
```

**Response Success (200):**
```json
[
    {
        "id": "comment123",
        "author": {
            "id": "user456",
            "first_name": "Carlos",
            "last_name": "López",
            "profile_picture": "/media/profile_pictures/carlos.jpg"
        },
        "content": "¡Excelente investigación!",
        "parent_comment": null,
        "likes_count": 3,
        "created_at": "2025-06-16T11:30:00Z",
        "replies": [
            {
                "id": "reply123",
                "author": {...},
                "content": "Gracias por el feedback!",
                "created_at": "2025-06-16T12:00:00Z"
            }
        ],
        "user_has_liked": false
    }
]
```

### 5. Registrar Interacción del Usuario
```http
POST /api/v1/interactions/
```

**Request Body:**
```json
{
    "interaction_type": "view", // view, like, comment, share
    "content_type": "post", // post, job
    "content_id": "uuid-1234-5678",
    "metadata": {
        "time_spent": 45, // segundos
        "scroll_depth": 0.8
    }
}
```

---

## 📊 ESTADÍSTICAS Y MÉTRICAS

### 1. Estadísticas del Usuario en Feed
```http
GET /api/v1/feed/stats/
```

**Response Success (200):**
```json
{
    "user_stats": {
        "posts_count": 25,
        "total_likes_received": 150,
        "total_comments_received": 45,
        "total_views": 1200,
        "followers_count": 35,
        "following_count": 42,
        "engagement_rate": 12.5
    },
    "recent_activity": {
        "posts_this_week": 3,
        "likes_this_week": 12,
        "comments_this_week": 8
    }
}
```

### 2. Métricas de Job (Solo Empresas)
```http
GET /api/v1/jobs/{job_id}/metrics/
```

**Response Success (200):**
```json
{
    "job_metrics": {
        "view_count": 150,
        "application_count": 25,
        "applications_rate": 16.7,
        "avg_time_on_page": 120,
        "bounce_rate": 35.2,
        "top_referrers": ["linkedin", "indeed", "direct"]
    },
    "applicant_demographics": {
        "experience_levels": {
            "junior": 8,
            "mid": 12,
            "senior": 5
        },
        "locations": {
            "Madrid": 10,
            "Barcelona": 8,
            "Remote": 7
        }
    }
}
```

---

## 🔍 BÚSQUEDA Y FILTROS AVANZADOS

### 1. Búsqueda Semántica de Jobs
```http
POST /api/v1/jobs/semantic-search/
```

**Request Body:**
```json
{
    "query": "Busco trabajo remoto en inteligencia artificial con Python",
    "limit": 10,
    "filters": {
        "is_remote": true,
        "salary_min": 40000,
        "experience_level": ["mid", "senior"]
    }
}
```

### 2. Búsqueda Semántica en Feed
```http
POST /api/v1/feed/semantic-search/
```

**Request Body:**
```json
{
    "query": "investigaciones sobre machine learning en salud",
    "limit": 15,
    "include_embeddings": false
}
```

---

## ⚡ WEBSOCKETS (TIEMPO REAL)

### Base WebSocket URL
```
ws://localhost:8000/ws/
```

### 1. Notificaciones en Tiempo Real
```javascript
// Conectar al WebSocket de notificaciones
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

// Eventos que puedes recibir:
{
    "type": "new_job_match",
    "data": {
        "job_id": 123,
        "job_title": "Senior Python Developer",
        "match_score": 0.95
    }
}

{
    "type": "new_like",
    "data": {
        "post_id": "uuid-123",
        "liker": "Ana García",
        "total_likes": 16
    }
}
```

### 2. Chat de Aplicaciones (Jobs)
```javascript
// Chat entre empresa y aplicante
const chatWs = new WebSocket(`ws://localhost:8000/ws/job-chat/${applicationId}/`);
```

---

## 🛠️ COMANDOS DE ADMINISTRACIÓN

### 1. Actualizar Embeddings de Jobs
```bash
docker-compose exec web python manage.py update_job_embeddings
```

### 2. Generar Embeddings para Usuarios
```bash
docker-compose exec web python manage.py update_user_embeddings
```

### 3. Procesar Recomendaciones
```bash
docker-compose exec web python manage.py process_recommendations
```

---

## 🐛 CÓDIGOS DE ERROR COMUNES

### Errores de Autenticación
- `401 Unauthorized`: Token no válido o expirado
- `403 Forbidden`: Sin permisos para la acción

### Errores de Validación
- `400 Bad Request`: Datos de entrada inválidos
- `422 Unprocessable Entity`: Error de validación específico

### Errores de Recursos
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto (ej: ya postulado a este job)

### Errores del Servidor
- `500 Internal Server Error`: Error interno del servidor
- `503 Service Unavailable`: Servicio temporalmente no disponible

---

## 🔧 CONFIGURACIÓN DE DESARROLLO

### Variables de Entorno Importantes
```bash
# Configuración de embeddings
EMBEDDING_SERVICE_URL=http://localhost:5000
VECTOR_DIMENSIONS=768

# Redis para cache y websockets
REDIS_URL=redis://localhost:6379/0

# Base de datos con pgvector
DATABASE_URL=postgresql://user:pass@localhost:5432/social_consensus
```

### Requisitos del Sistema
- Python 3.11+
- PostgreSQL 14+ con extensión pgvector
- Redis 6+
- Docker y Docker Compose

---

## 📈 MÉTRICAS Y MONITOREO

El sistema incluye métricas detalladas para:
- **Performance de recomendaciones**: Precisión, recall, diversidad
- **Engagement del usuario**: Tiempo en plataforma, interacciones
- **Calidad de matches**: Éxito en postulaciones, satisfacción empresa-candidato
- **Uso de recursos**: Consultas vectoriales, cache hits, latencia API

---

Esta documentación cubre todas las funcionalidades principales del sistema integrado. Para detalles específicos de implementación o casos de uso avanzados, consulte el código fuente en los respectivos módulos.
