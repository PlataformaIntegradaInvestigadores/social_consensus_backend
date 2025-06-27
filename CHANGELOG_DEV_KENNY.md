# Changelog - Rama dev-kenny

## Resumen Ejecutivo

Esta rama implementa tres funcionalidades principales que extienden significativamente las capacidades del sistema Social Consensus:

1. **Sistema de Gestión de Empleos (Jobs)** - Plataforma completa para publicación y postulación a empleos
2. **Sistema de Feed Social** - Red social para investigadores con posts, comentarios y likes
3. **Sistema de Recomendaciones Vectoriales** - Motor de recomendaciones basado en AI/ML usando pgvector

## 🚀 Nuevas Funcionalidades

### 1. Módulo de Jobs (`apps/jobs/`)

#### Descripción
Sistema completo de gestión de empleos que permite a las empresas publicar ofertas laborales y a los usuarios (investigadores) postularse a ellas. Incluye un sofisticado sistema de recomendaciones basado en embeddings vectoriales.

#### Modelos Principales

**Jobs (`jobs.py`)**
- ✅ Gestión completa de ofertas laborales
- ✅ Campos: título, descripción, requisitos, beneficios, ubicación, tipo de trabajo, experiencia requerida
- ✅ Sistema de estados (activo, inactivo, cerrado, borrador)
- ✅ Soporte para trabajo remoto y rangos salariales
- ✅ **Vector embeddings (768 dimensiones)** para recomendaciones AI
- ✅ Métricas de interacción (visualizaciones, aplicaciones, score)

**Postulants (`postulants.py`)**
- ✅ Sistema de postulaciones con carta de presentación
- ✅ Subida de CV en archivos
- ✅ Estados de postulación (pendiente, revisión, entrevistado, aceptado, rechazado)
- ✅ Restricción: una postulación por usuario por trabajo
- ✅ Notas del reclutador

#### Sistema de Recomendaciones Vectoriales

**VectorRecommendationService (`vector_recommendation_service.py`)**
- ✅ **Integración con microservicio de embeddings** para generar vectores de trabajos
- ✅ Algoritmo de similitud coseno usando pgvector para recomendaciones
- ✅ Actualización automática de embeddings al crear/editar trabajos
- ✅ Filtros avanzados (umbral de similitud, exclusión de trabajos vistos)
- ✅ Scoring combinado: similitud vectorial + métricas de interacción

#### API Endpoints

**Jobs Management**
```
GET    /api/v1/jobs/                    # Lista de trabajos (filtrable)
POST   /api/v1/jobs/                    # Crear trabajo (solo empresas)
GET    /api/v1/jobs/{id}/               # Detalle de trabajo
PUT    /api/v1/jobs/{id}/               # Actualizar trabajo (solo empresa propietaria)
DELETE /api/v1/jobs/{id}/               # Eliminar trabajo (solo empresa propietaria)
```

**Postulations Management**
```
GET    /api/v1/postulants/              # Lista de postulaciones
POST   /api/v1/postulants/              # Crear postulación
GET    /api/v1/postulants/{id}/         # Detalle de postulación
PUT    /api/v1/postulants/{id}/         # Actualizar postulación
DELETE /api/v1/postulants/{id}/         # Cancelar postulación
```

**AI Recommendations**
```
GET    /api/v1/jobs/recommendations/    # Recomendaciones personalizadas para el usuario
POST   /api/v1/jobs/embeddings/update/ # Actualizar embeddings de trabajos
```

#### Comandos de Management
```bash
python manage.py update_job_embeddings  # Actualiza embeddings de todos los trabajos
```

---

### 2. Módulo de Feed Social (`apps/feeds/`)

#### Descripción
Red social completa para investigadores que permite crear posts, comentar, dar likes y compartir contenido. Incluye sistema de archivos adjuntos y embeddings para recomendaciones de contenido.

#### Modelos Principales

**FeedPost (`feed_post.py`)**
- ✅ Posts con contenido de texto rico
- ✅ **Vector embeddings (768 dimensiones)** para recomendaciones
- ✅ Métricas completas: likes, comentarios, visualizaciones, shares
- ✅ Score de engagement calculado automáticamente
- ✅ Sistema de privacidad (público/privado)
- ✅ Posts fijados (pinned)
- ✅ Tags y metadatos JSON flexibles
- ✅ UUIDs como primary keys para escalabilidad

**Comment (`comment.py`)**
- ✅ **Sistema de comentarios recursivos** (comentarios en comentarios)
- ✅ Métricas de likes por comentario
- ✅ Notificaciones automáticas a autores
- ✅ Soft delete para moderación
- ✅ Timestamps de edición

**Like (`like.py`)**
- ✅ Sistema de likes para posts y comentarios
- ✅ Prevención de likes duplicados
- ✅ Tipos de reacciones extensibles (like, love, laugh, etc.)
- ✅ Tracking de usuarios que dieron like

**PostFile (`post_file.py`)**
- ✅ Archivos adjuntos en posts (imágenes, documentos, videos)
- ✅ Múltiples archivos por post
- ✅ Metadatos de archivo (tamaño, tipo MIME)
- ✅ Rutas organizadas por UUID

#### API Endpoints

**Feed Posts**
```
GET    /api/v1/feeds/                   # Feed principal (algorítmico)
POST   /api/v1/feeds/                   # Crear post
GET    /api/v1/feeds/{id}/              # Detalle de post
PUT    /api/v1/feeds/{id}/              # Editar post (solo autor)
DELETE /api/v1/feeds/{id}/              # Eliminar post (solo autor)
```

**Comments**
```
GET    /api/v1/feeds/{post_id}/comments/     # Comentarios de un post
POST   /api/v1/feeds/{post_id}/comments/     # Crear comentario
PUT    /api/v1/comments/{id}/                # Editar comentario
DELETE /api/v1/comments/{id}/               # Eliminar comentario
```

**Likes**
```
POST   /api/v1/feeds/{post_id}/like/         # Toggle like en post
POST   /api/v1/comments/{comment_id}/like/   # Toggle like en comentario
```

---

### 3. Mejoras en Custom Auth (`apps/custom_auth/`)

#### Nuevas Entidades

**Company (`company.py`)**
- ✅ **Modelo completo de empresas** que extiende AbstractBaseUser
- ✅ Campos especializados: industry, company_size, website, description
- ✅ Logo de empresa con upload personalizado
- ✅ Sistema de verificación de empresas
- ✅ Información de contacto completa
- ✅ Manager personalizado para empresas

**UserVectorService (`user_vector_service.py`)**
- ✅ **Servicio de vectorización de perfiles de usuario**
- ✅ Generación de embeddings basados en: campo de investigación, institución, intereses, habilidades
- ✅ Integración con microservicio de embeddings
- ✅ Actualización automática de vectores de usuario
- ✅ Historial de interacciones para mejorar recomendaciones

#### Nuevas Vistas y APIs

**Company Management**
```
POST   /api/v1/companies/register/     # Registro de empresas
GET    /api/v1/companies/profile/      # Perfil de empresa
PUT    /api/v1/companies/profile/      # Actualizar perfil empresa
```

**User Vectors**
```
POST   /api/v1/users/update-vector/    # Actualizar vector de usuario
GET    /api/v1/users/recommendations/  # Recomendaciones personalizadas
```

---

## 🛠 Cambios Técnicos

### Dependencias Agregadas
```
pgvector==0.3.5          # Extensión PostgreSQL para vectores
psycopg2-binary==2.9.9   # Driver PostgreSQL
requests==2.31.0         # Cliente HTTP para microservicios
celery==5.3.1            # Tareas asíncronas
redis==4.6.0             # Cache y broker para Celery
```

### Configuración de Base de Datos
- ✅ **Extensión pgvector habilitada** en PostgreSQL
- ✅ VectorField configurado con 768 dimensiones (compatible con BERT/embeddings modernos)
- ✅ Índices optimizados para búsquedas vectoriales
- ✅ Índices compuestos para queries de recomendación

### Arquitectura
- ✅ **Arquitectura hexagonal** mantenida en todos los módulos
- ✅ Separación clara entre domain, infrastructure y application layers
- ✅ Servicios especializados para lógica de negocio compleja
- ✅ Serializers dedicados por endpoint
- ✅ URLs organizadas por funcionalidad

### Integraciones Externas
- ✅ **Microservicio de embeddings** para procesamiento de texto a vectores
- ✅ API REST endpoints para generación de embeddings
- ✅ Traducción automática a inglés para mejor precisión de embeddings
- ✅ Limpieza de texto automática

## 📊 Métricas y Observabilidad

### Sistema de Scoring
- ✅ **Engagement Score** para posts: `(likes * 1.0 + comments * 1.5 + shares * 2.0) / age_factor`
- ✅ **Interaction Score** para jobs: similar combinado con aplicaciones y visualizaciones
- ✅ Decay temporal para contenido trending
- ✅ Normalización de scores para comparabilidad

### Logging y Monitoreo
- ✅ Logging estructurado para todas las operaciones vectoriales
- ✅ Métricas de rendimiento de recomendaciones
- ✅ Tracking de errores en microservicios
- ✅ Auditoría de interacciones de usuario

## 🚦 Estados y Flujos

### Jobs Workflow
1. **Draft** → Empresa crea trabajo (estado borrador)
2. **Active** → Trabajo publicado y visible para usuarios
3. **Applications** → Usuarios aplican con CV y carta
4. **Review** → Empresa revisa postulaciones
5. **Interviews** → Proceso de entrevistas
6. **Closed** → Trabajo cerrado (plaza ocupada)

### Feed Interaction Flow
1. **Create Post** → Usuario publica contenido
2. **Generate Embedding** → Sistema vectoriza contenido automáticamente
3. **Distribution** → Post aparece en feeds relevantes
4. **Interactions** → Likes, comentarios, shares
5. **Trending** → Algorithm boost basado en engagement

## 🔄 Migraciones de Base de Datos

**Jobs App Migrations:**
- `0001_initial.py` - Creación de modelos Jobs y Postulants
- `0002_add_vectors.py` - Agregado de campos vectoriales
- `0003_add_metrics.py` - Métricas de interacción

**Feeds App Migrations:**
- `0001_initial.py` - Modelos de feed completos
- `0002_add_indexes.py` - Índices de rendimiento

**Custom Auth Migrations:**
- `0003_company_model.py` - Modelo de empresa
- `0004_user_vectors.py` - Campos vectoriales en usuarios

## 📈 Rendimiento y Escalabilidad

### Optimizaciones Implementadas
- ✅ **Índices vectoriales HNSW** para búsquedas de similaridad ultra-rápidas
- ✅ Paginación en todos los endpoints de lista
- ✅ Eager loading de relaciones frecuentes
- ✅ Cache de embeddings para evitar recálculos
- ✅ Queries optimizadas con select_related y prefetch_related

### Escalabilidad
- ✅ UUIDs como primary keys para sharding futuro
- ✅ Separación de reads/writes preparada
- ✅ Microservicios para operaciones computacionalmente intensivas
- ✅ Task queue con Celery para procesamiento asíncrono

## 🔐 Seguridad

### Autenticación y Autorización
- ✅ **Dual user system**: Users (investigadores) y Companies
- ✅ Permisos granulares por recurso
- ✅ Validación de ownership en todas las operaciones
- ✅ Rate limiting en endpoints de recomendación

### Privacidad
- ✅ Posts privados/públicos
- ✅ Vectores de usuario anonimizados
- ✅ Control de visibilidad de información empresarial
- ✅ Soft deletes para auditoría

## 🧪 Testing y Quality

### Estructura de Tests
- ✅ Tests unitarios para servicios de vectores
- ✅ Tests de integración para APIs
- ✅ Tests de performance para queries vectoriales
- ✅ Mocks para microservicios externos

## 📋 Postman Collection

**Updated Collection**: `Social_Consensus_API.postman_collection.json`
- ✅ Todos los endpoints de Jobs documentados
- ✅ Todos los endpoints de Feeds documentados
- ✅ Ejemplos de requests/responses
- ✅ Environment variables configuradas
- ✅ Tests automatizados en requests

## 🚀 Próximos Pasos Recomendados

1. **Optimización de Recomendaciones**
   - Implementar A/B testing para algoritmos de recomendación
   - Agregar filtros colaborativos
   - Machine learning para tuning de pesos

2. **Escalabilidad**
   - Implementar cache Redis para recomendaciones
   - Considerar Elasticsearch para búsqueda de texto
   - Métricas de rendimiento en producción

3. **Características Sociales Avanzadas**
   - Sistema de seguimiento entre usuarios
   - Notificaciones en tiempo real
   - Integración con conferencias/eventos académicos

4. **Analytics**
   - Dashboard de métricas para empresas
   - Analytics de engagement para usuarios
   - Reportes de efectividad de recomendaciones

---

## 📊 Estadísticas del Desarrollo

- **Archivos modificados**: 80+
- **Líneas de código agregadas**: ~15,000
- **Nuevos endpoints**: 25+
- **Nuevos modelos**: 7
- **Servicios especializados**: 3
- **Comandos de management**: 2

**Commit Principal**: `e3df6e1 - chore: fixes on jobs + feeds + microservice connection`

---

*Desarrollado por Kenny - Diciembre 2024*
