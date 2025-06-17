"""
Script de prueba para el sistema de recomendaciones con pgvector
Ejecutar desde el shell de Django: python manage.py shell
"""

def test_vector_recommendations():
    """Función de prueba completa del sistema de recomendaciones"""
    
    from apps.jobs.domain.entities.jobs import Jobs
    from apps.custom_auth.domain.entities.company import Company
    from apps.jobs.domain.services.vector_recommendation_service import vector_service
    from django.contrib.auth import get_user_model
    import random
    
    User = get_user_model()
    
    print("=== TEST SISTEMA DE RECOMENDACIONES ===\n")
    
    # 1. Verificar que tenemos jobs en la base de datos
    jobs_count = Jobs.objects.filter(status='active').count()
    print(f"Jobs activos en la base de datos: {jobs_count}")
    
    if jobs_count == 0:
        print("⚠️  No hay jobs activos para probar. Creando job de ejemplo...")
        
        # Crear empresa de ejemplo si no existe
        company, created = Company.objects.get_or_create(
            company_name="Tech Startup Example",
            defaults={
                'email': 'test@example.com',
                'industry': 'technology',
                'description': 'Empresa de ejemplo para testing'
            }
        )
        
        # Crear job de ejemplo
        job = Jobs.objects.create(
            company=company,
            title="Desarrollador Python Senior",
            description="Buscamos un desarrollador Python con experiencia en Django, FastAPI y bases de datos PostgreSQL. El candidato ideal tendrá conocimientos en machine learning y procesamiento de lenguaje natural.",
            requirements="- 5+ años de experiencia en Python\n- Experiencia con Django y FastAPI\n- Conocimiento de PostgreSQL\n- Experiencia en ML/NLP es un plus",
            benefits="- Salario competitivo\n- Trabajo remoto\n- Flexibilidad horaria\n- Capacitación continua",
            location="Madrid, España",
            job_type="full_time",
            experience_level="senior",
            salary_min=50000,
            salary_max=70000,
            status="active",
            is_remote=True
        )
        print(f"✅ Job de ejemplo creado: {job.title} (ID: {job.id})")
    
    # 2. Seleccionar un job para actualizar su embedding
    sample_job = Jobs.objects.filter(status='active').first()
    print(f"\n=== ACTUALIZANDO EMBEDDING ===")
    print(f"Job seleccionado: {sample_job.title} (ID: {sample_job.id})")
    
    # Verificar si ya tiene embedding
    has_embedding = sample_job.embedding is not None and len(sample_job.embedding or []) > 0
    print(f"¿Ya tiene embedding?: {'Sí' if has_embedding else 'No'}")
    
    # Actualizar embedding
    print("Obteniendo embedding del microservicio...")
    success = vector_service.update_job_embedding(sample_job)
    
    if success:
        print("✅ Embedding actualizado exitosamente")
        sample_job.refresh_from_db()
        print(f"Dimensiones del vector: {len(sample_job.embedding or [])}")
    else:
        print("❌ Error al actualizar embedding")
        print("Verificar que el microservicio esté ejecutándose en la URL configurada")
        return
    
    # 3. Simular embedding de usuario
    print(f"\n=== GENERANDO RECOMENDACIONES ===")
    user_embedding = [random.uniform(-1, 1) for _ in range(768)]
    print("Embedding de usuario simulado generado (768 dimensiones)")
    
    # 4. Obtener recomendaciones
    try:
        recommendations = vector_service.get_similar_jobs(
            user_embedding=user_embedding,
            limit=5,
            similarity_threshold=0.0  # Umbral bajo para testing
        )
        
        print(f"Recomendaciones encontradas: {len(recommendations)}")
        
        for i, job in enumerate(recommendations, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Empresa: {job.company.company_name}")
            print(f"   Similitud: {float(job.similarity):.3f}")
            print(f"   Score recomendación: {float(job.recommendation_score):.3f}")
            print(f"   Horas desde creación: {float(job.hours_old):.1f}")
            
    except Exception as e:
        print(f"❌ Error al obtener recomendaciones: {str(e)}")
        return
    
    # 5. Probar actualización de interacciones
    print(f"\n=== REGISTRANDO INTERACCIONES ===")
    
    # Simular visualización
    vector_service.update_job_interactions(sample_job.id, 'view')
    print(f"✅ Interacción 'view' registrada para job {sample_job.id}")
    
    # Simular aplicación
    vector_service.update_job_interactions(sample_job.id, 'application')
    print(f"✅ Interacción 'application' registrada para job {sample_job.id}")
    
    # Verificar actualización
    sample_job.refresh_from_db()
    print(f"Visualizaciones: {sample_job.view_count}")
    print(f"Aplicaciones: {sample_job.application_count}")
    print(f"Score de interacciones: {sample_job.interactions_score}")
    
    # 6. Probar jobs en tendencia
    print(f"\n=== JOBS EN TENDENCIA ===")
    try:
        trending_jobs = vector_service.get_trending_jobs(limit=3)
        
        print(f"Jobs en tendencia encontrados: {len(trending_jobs)}")
        
        for i, job in enumerate(trending_jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Score trending: {float(job.trending_score):.3f}")
            print(f"   Interacciones: {job.interactions_score}")
            print(f"   Views: {job.view_count}")
            print(f"   Applications: {job.application_count}")
            
    except Exception as e:
        print(f"❌ Error al obtener jobs en tendencia: {str(e)}")
    
    print(f"\n=== TEST COMPLETADO ===")
    print("🎉 ¡Sistema de recomendaciones funcionando correctamente!")


def quick_test():
    """Prueba rápida del sistema"""
    print("Ejecutando prueba rápida...")
    
    from apps.jobs.domain.entities.jobs import Jobs
    
    # Verificar extensión pgvector
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Extensión pgvector instalada")
        else:
            print("❌ Extensión pgvector NO instalada")
            print("Ejecutar: python manage.py migrate")
            return
    
    # Verificar campos del modelo
    jobs_with_embedding = Jobs.objects.filter(embedding__isnull=False).count()
    total_jobs = Jobs.objects.count()
    
    print(f"Jobs totales: {total_jobs}")
    print(f"Jobs con embedding: {jobs_with_embedding}")
    
    if total_jobs > 0 and jobs_with_embedding == 0:
        print("💡 Ejecutar: python manage.py update_job_embeddings")


if __name__ == "__main__":
    # Ejecutar desde Django shell
    print("Para ejecutar las pruebas, usar:")
    print(">>> test_vector_recommendations()  # Prueba completa")
    print(">>> quick_test()                   # Prueba rápida")
