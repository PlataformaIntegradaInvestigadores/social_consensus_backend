# Sistema de Recomendaciones con pgvector

## Configuración Implementada

### 1. Base de Datos
- ✅ Extensión pgvector habilitada
- ✅ Campo `embedding` (768 dimensiones) agregado al modelo Jobs
- ✅ Campos de métricas: `interactions_score`, `view_count`, `application_count`

### 2. Servicio de Vectores
- ✅ Integración con microservicio de embeddings
- ✅ Endpoint: `{base_url}/{api_prefix}/text-processing/vectorize/`
- ✅ Soporte para traducción automática y limpieza de texto

### 3. API Endpoints

#### Recomendaciones Personalizadas
```
GET /api/v1/jobs/recommendations/?limit=10
Headers: Authorization: Bearer {token}
```

#### Jobs en Tendencia  
```
GET /api/v1/jobs/trending/?limit=10
```

#### Registrar Interacción
```
POST /api/v1/jobs/{job_id}/interaction/
{
    "interaction_type": "view"  // o "application"
}
```

#### Actualizar Embedding
```
POST /api/v1/jobs/{job_id}/update-embedding/
Headers: Authorization: Bearer {token}
```

### 4. Comandos de Gestión

#### Actualizar todos los embeddings
```bash
python manage.py update_job_embeddings
```

#### Opciones del comando
```bash
# Procesar en lotes de 5 con pausa de 2 segundos
python manage.py update_job_embeddings --batch-size=5 --delay=2

# Forzar actualización de todos los jobs (incluso los que ya tienen embedding)
python manage.py update_job_embeddings --force

# Combinar opciones
python manage.py update_job_embeddings --batch-size=20 --delay=0.5 --force
```

## Configuración del Entorno

### Variables de Entorno
Agregar al archivo `.env`:
```env
# Microservicio de embeddings
EMBEDDING_SERVICE_URL=http://localhost:8000
EMBEDDING_SERVICE_API_PREFIX=api/v1
```

### Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar Migraciones
```bash
python manage.py migrate
```

## Flujo de Trabajo

### 1. Creación de Job
```python
# Cuando se crea un nuevo job, automáticamente obtener su embedding
from apps.jobs.domain.services.vector_recommendation_service import vector_service

job = Jobs.objects.create(
    title="Desarrollador Python",
    description="...",
    # ... otros campos
)

# Actualizar embedding
vector_service.update_job_embedding(job)
```

### 2. Obtener Recomendaciones
```python
# Para un usuario específico
user_embedding = get_user_embedding_vector(user_id)
recommendations = vector_service.get_similar_jobs(
    user_embedding=user_embedding,
    limit=10,
    similarity_threshold=0.7
)
```

### 3. Registro de Interacciones
```python
# Cuando un usuario ve un job
vector_service.update_job_interactions(job_id, 'view')

# Cuando un usuario aplica a un job  
vector_service.update_job_interactions(job_id, 'application')
```

## Consulta SQL Directa

Si prefieres usar consultas SQL directas para recomendaciones:

```sql
-- Recomendaciones basadas en similitud coseno
SELECT *,
  (1 - (embedding <#> '[...vector usuario...]')) AS similarity,
  interactions_score,
  EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600 AS hours_old,
  (
    0.6 * (1 - (embedding <#> '[...vector usuario...]')) +  -- 60% similitud
    0.3 * interactions_score -                              -- 30% engagement  
    0.1 * (EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600) -- 10% penalización tiempo
  ) AS recommendation_score
FROM jobs_jobs 
WHERE status = 'active' 
  AND embedding IS NOT NULL
  AND (1 - (embedding <#> '[...vector usuario...]')) >= 0.6  -- umbral similitud
ORDER BY recommendation_score DESC
LIMIT 10;
```

## Próximos Pasos

### 1. Implementar Perfil de Usuario
- Crear endpoint para obtener embedding del perfil del usuario
- Considerar: CV, habilidades, experiencia, trabajos anteriores, etc.

### 2. Mejorar el Algoritmo
- Experimentar con diferentes pesos en el score compuesto
- Agregar más factores: localización, tipo de contrato, salario, etc.
- Implementar filtros personalizables

### 3. Analítica
- Tracking de efectividad de recomendaciones
- A/B testing de diferentes algoritmos
- Métricas de engagement

### 4. Optimización
- Índices pgvector para consultas más rápidas
- Cache de embeddings de usuarios frecuentes
- Batch processing para updates masivos

## Operadores de pgvector

- `<#>` - Distancia coseno negativa (menor = más similar)
- `<->` - Distancia euclidiana  
- `<=>` - Distancia del producto interno negativo
- `<+>` - Distancia Manhattan

## Ejemplo de Uso Completo

```python
# 1. Crear job y generar embedding
job = Jobs.objects.create(
    title="Senior Python Developer",
    description="Desarrollo de APIs con Django y FastAPI...",
    requirements="5+ años experiencia Python, Django, PostgreSQL...",
    company=company,
    # ... otros campos
)

# 2. Generar embedding
success = vector_service.update_job_embedding(job)

# 3. Obtener recomendaciones para un usuario
user_embedding = get_user_embedding_vector(user_id=123)
recommendations = vector_service.get_similar_jobs(
    user_embedding=user_embedding,
    limit=5,
    similarity_threshold=0.7
)

# 4. Registrar interacción cuando el usuario ve el job
vector_service.update_job_interactions(job.id, 'view')
```
