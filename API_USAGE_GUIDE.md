# 🚀 Guía de Uso de la API - Social Consensus Backend

## 📋 Resumen

Esta documentación cubre la API completa del sistema Social Consensus Backend, que integra:

- **Sistema de Autenticación Dual** (Investigadores y Empresas)
- **Plataforma de Jobs** con IA para recomendaciones
- **Feed Social** con embeddings vectoriales
- **Sistema de Recomendaciones** usando pgvector
- **WebSockets** para tiempo real

## 🛠️ Integración de Nuevas Funcionalidades

### ✨ **Jobs con IA**
- **Vectorización automática**: Cada job se convierte en embeddings de 768 dimensiones
- **Recomendaciones personalizadas**: Basadas en el perfil del usuario y similitud semántica
- **Búsqueda semántica**: "Busco trabajo remoto en IA" encuentra jobs relevantes sin palabras exactas
- **Trending jobs**: Algoritmo que considera views, aplicaciones y tiempo

### ✨ **Feed Social Inteligente**
- **Posts con embeddings**: Contenido vectorizado para recomendaciones
- **Feed personalizado**: Algoritmo que aprende de las interacciones del usuario
- **Score de engagement**: Métrica compuesta (likes×1 + comments×2 + shares×3 + views×0.1)
- **Decay temporal**: Los posts pierden relevancia con el tiempo

### ✨ **Usuarios con Perfiles Vectoriales**
- **Doble embedding**: Uno para jobs y otro para posts del feed
- **Actualización inteligente**: Los vectores se actualizan basado en interacciones
- **Intereses textuales**: Procesados por IA para generar embeddings
- **Historial de interacciones**: Para mejorar las recomendaciones

## 📚 Archivos de Documentación

### 📖 `API_DOCUMENTATION_COMPLETE.md`
Documentación técnica completa con:
- Todos los endpoints disponibles
- Ejemplos de request/response
- Códigos de error
- Parámetros de configuración
- Variables de entorno

### 📮 `Social_Consensus_API.postman_collection.json`
Colección de Postman con:
- 50+ requests organizados por categorías
- Scripts de automatización (auto-refresh de tokens)
- Variables dinámicas
- Ejemplos de payloads realistas

### 🌍 `Social_Consensus_Environment.postman_environment.json`
Variables de entorno para Postman:
- URLs configurables
- Tokens de autenticación
- IDs de recursos
- Configuración de desarrollo/producción

## 🚀 Cómo Empezar

### 1. **Importar en Postman**
```bash
1. Abrir Postman
2. File > Import
3. Arrastrar los archivos .json
4. Seleccionar el environment "Social Consensus - Development"
```

### 2. **Configurar el Entorno**
```bash
# Asegúrate de que el backend esté corriendo
docker-compose up -d

# Verificar que esté funcionando
curl http://localhost:8000/api/health/
```

### 3. **Autenticarse**
```bash
# Usar la carpeta "🔐 Autenticación" en Postman
1. Ejecutar "Registro de Usuario" o "Registro de Empresa"
2. Ejecutar "Login" (auto-guarda el token)
3. ¡Ya puedes usar todas las APIs protegidas!
```

## 🔥 Funcionalidades Destacadas

### 🤖 **Recomendaciones Inteligentes**
```http
GET /api/v1/jobs/recommendations/?limit=10
```
- Usa el perfil vectorial del usuario
- Considera historial de aplicaciones
- Excluye jobs ya vistos
- Incluye score de similitud y razón de recomendación

### 🔍 **Búsqueda Semántica**
```http
POST /api/v1/jobs/semantic-search/
{
    "query": "trabajo remoto python machine learning"
}
```
- Busca por significado, no solo palabras exactas
- Combina filtros tradicionales con IA
- Resultados rankeados por relevancia

### 📱 **Feed Personalizado**
```http
GET /api/v1/feed/?feed_type=personalized&limit=20
```
- Algoritmo que aprende de tus interacciones
- Balance entre contenido relevante y diversidad
- Actualización en tiempo real del engagement

## 🎯 Casos de Uso Comunes

### **Para Investigadores:**
1. **Buscar oportunidades laborales**: `GET /api/v1/jobs/recommendations/`
2. **Compartir investigación**: `POST /api/v1/posts/` con archivos adjuntos
3. **Interactuar socialmente**: Like, comentar, seguir tendencias
4. **Actualizar perfil**: Para mejores recomendaciones

### **Para Empresas:**
1. **Publicar jobs**: `POST /api/v1/jobs/` con descripción detallada
2. **Ver aplicaciones**: `GET /api/v1/applications/?job_id=X`
3. **Gestionar candidatos**: Actualizar estado de aplicaciones
4. **Analizar métricas**: `GET /api/v1/jobs/{id}/metrics/`

## 🧪 Testing y Desarrollo

### **Scripts de Test Incluidos**
Los requests de Postman incluyen:
- **Tests automáticos**: Verifican respuestas exitosas
- **Extracción de datos**: Auto-guardan IDs para requests siguientes
- **Validación de tokens**: Verifican expiración automáticamente

### **Datos de Prueba**
Incluidos en los requests:
- Usuarios de ejemplo con perfiles realistas
- Jobs con descripciones completas
- Posts con tags y metadatos
- Interacciones simuladas

## 🐛 Troubleshooting

### **Problemas Comunes:**

1. **Error 401 (Unauthorized)**
   - Verificar que el token esté en el environment
   - Ejecutar login nuevamente si expiró

2. **Error 403 (Forbidden)**
   - Verificar que el usuario tenga permisos
   - Empresas vs Usuarios tienen accesos diferentes

3. **Error con pgvector**
   - Verificar que el Docker esté actualizado
   - Confirmar que pgvector esté instalado (ya solucionado)

4. **Recomendaciones vacías**
   - Actualizar embeddings del usuario
   - Verificar que haya jobs con embeddings generados

## 📊 Métricas y Monitoreo

### **Endpoints de Estadísticas:**
- `/api/v1/feed/stats/`: Métricas del usuario
- `/api/v1/jobs/{id}/metrics/`: Métricas del job
- `/api/v1/companies/dashboard/`: Dashboard empresarial

### **Información del Sistema:**
- `/api/health/`: Estado de la API
- `/api/system-info/`: Información técnica
- `/api/config/`: Configuración actual

## 🔐 Seguridad

### **Autenticación JWT:**
- Tokens con expiración automática
- Refresh tokens para renovación
- Headers de autorización requeridos

### **Validaciones:**
- Sanitización de inputs
- Validación de tipos de archivo
- Límites de rate limiting (configurables)

### **Permisos:**
- RBAC (Role-Based Access Control)
- Separación Usuario/Empresa
- Validación de ownership de recursos

## 🚀 Próximos Pasos

1. **Integrar microservicio de embeddings** para generar vectores en tiempo real
2. **Implementar WebSockets** para notificaciones push
3. **Añadir más filtros** a las búsquedas semánticas
4. **Dashboard analytics** más avanzado
5. **Sistema de seguimiento** entre usuarios

---

## 📞 Soporte

Para preguntas técnicas o issues:
1. Revisar esta documentación
2. Consultar los logs del Docker: `docker-compose logs web`
3. Verificar el estado de la base de datos y Redis
4. Comprobar las migraciones: `docker-compose exec web python manage.py showmigrations`

¡La API está lista para soportar un sistema completo de consenso social con IA! 🎉
