import time
import uuid
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.feeds.domain.services.feed_service import feed_service
from apps.feeds.domain.entities.feed_post import FeedPost

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Valida métricas funcionales y de rendimiento (CRUD < 1.2s, Feed < 1.8s)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando Validación Funcional y de Rendimiento...'))
        
        # 1. Setup - Crear usuario temporal
        user_email = f"test_perf_{uuid.uuid4().hex[:8]}@example.com"
        password = "test_password_123"
        try:
            user = User.objects.create_user(
                username=user_email, 
                password=password,
                first_name="Test",
                last_name="Performance"
            )
            # Simular info para embedding de perfil
            user.investigation_camp = "Artificial Intelligence"
            user.interests = "Machine Learning, Neural Networks"
            user.save()
            
            # Generar embedding de perfil para habilitar recomendaciones
            # Nota: Esto no se mide porque es setup
            from apps.custom_auth.domain.services.user_vector_service import user_vector_service
            user_vector_service.update_user_feed_embedding(user.id)
            
            self.stdout.write(f"Usuario temporal creado: {user.username}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error en setup: {str(e)}"))
            return

        metrics = {
            "CRUD": [],
            "FEED": []
        }
        
        created_posts = []

        try:
            # 2. Pruebas CRUD (25 iteraciones)
            self.stdout.write("\n--- Ejecutando Pruebas CRUD (25 casos) ---")
            for i in range(25):
                start_time = time.perf_counter()
                
                # A. Crear Post
                content = f"Benchmark post iteración {i}: Análisis de rendimiento en sistemas distribuidos."
                post = feed_service.create_post(author=user, content=content, is_public=True)
                
                # B. Dar Like (a su propio post para simplificar)
                feed_service.toggle_like(user, post)
                
                # C. Comentar
                feed_service.create_comment(user.id, post.id, "Interesante punto de vista.")
                
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                metrics["CRUD"].append(duration)
                if post:
                    created_posts.append(post)
                
                self.stdout.write(f"  Iteración {i+1}: {duration:.4f}s")

            # 3. Pruebas FEED (25 iteraciones)
            self.stdout.write("\n--- Ejecutando Pruebas FEED PERSONALIZADO (25 casos) ---")
            for i in range(25):
                start_time = time.perf_counter()
                
                # Obtener feed personalizado
                # Nota: Usamos get_personalized_feed que hace la búsqueda vectorial compleja
                feed, _, _ = feed_service.get_personalized_feed(user=user, limit=10)
                
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                metrics["FEED"].append(duration)
                self.stdout.write(f"  Iteración {i+1}: {duration:.4f}s (Items: {len(feed)})")

            # 4. Reporte
            self.print_report(metrics)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error durante las pruebas: {str(e)}"))
        
        finally:
            # Teardown
            self.stdout.write("\nLimpiando datos de prueba...")
            user.delete() # Debería borrar posts en cascada si está configurado, si no borramos manual
            for post in created_posts:
                if FeedPost.objects.filter(id=post.id).exists():
                    post.delete()
            self.stdout.write("Limpieza completada.")

    def print_report(self, metrics):
        report_path = 'apps/feeds/docs/functional_validation_results_2026_01_11.md'
        
        crud_avg = sum(metrics["CRUD"]) / len(metrics["CRUD"])
        crud_target = 1.2
        crud_passed = crud_avg < crud_target
        crud_status = "✅ PASSED" if crud_passed else "❌ FAILED"
        
        feed_avg = sum(metrics["FEED"]) / len(metrics["FEED"])
        feed_target = 1.8
        feed_passed = feed_avg < feed_target
        feed_status = "✅ PASSED" if feed_passed else "❌ FAILED"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Validación Funcional y de Rendimiento\n\n")
            f.write("**Fecha:** 11 de Enero de 2026\n")
            f.write("**Objetivo**: Validar tiempos de respuesta de operaciones críticas.\n\n")
            
            f.write("## 1. Operaciones CRUD (Create + Like + Comment)\n")
            f.write(f"- **Promedio**: {crud_avg:.4f}s\n")
            f.write(f"- **Meta**: < {crud_target}s\n")
            f.write(f"- **Estado**: {crud_status}\n\n")
            
            f.write("## 2. Generación de Feed Personalizado\n")
            f.write(f"- **Promedio**: {feed_avg:.4f}s\n")
            f.write(f"- **Meta**: < {feed_target}s\n")
            f.write(f"- **Estado**: {feed_status}\n\n")
            
            if crud_passed and feed_passed:
                f.write("## Conclusión\n**EL SISTEMA CUMPLE LOS REQUISITOS DE RENDIMIENTO.**\n")
            else:
                f.write("## Conclusión\n**ALGUNOS REQUISITOS NO SE CUMPLIERON.**\n")
                
        self.stdout.write(self.style.SUCCESS(f"Reporte generado en: {report_path}"))
