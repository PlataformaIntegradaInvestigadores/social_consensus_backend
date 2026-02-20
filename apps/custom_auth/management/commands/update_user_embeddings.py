"""
Management command para actualizar embeddings de usuarios existentes.
Busca usuarios sin feed_recommendations_embedding o job_recommendations_embedding
y genera los vectores llamando al microservicio de embeddings.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = (
        'Actualiza los embeddings de usuarios que no los tienen o fuerza la actualización. '
        'Genera tanto feed_recommendations_embedding como job_recommendations_embedding.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la actualización de embeddings incluso si ya existen',
        )
        parser.add_argument(
            '--user-id',
            type=str,
            help='Actualiza solo el usuario con el ID especificado',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Número de usuarios a procesar por lote (default: 50)',
        )
        parser.add_argument(
            '--feed-only',
            action='store_true',
            help='Solo actualiza el embedding de feed (feed_recommendations_embedding)',
        )
        parser.add_argument(
            '--job-only',
            action='store_true',
            help='Solo actualiza el embedding de jobs (job_recommendations_embedding)',
        )

    def handle(self, *args, **options):
        from apps.custom_auth.domain.services.user_vector_service import user_vector_service

        force = options['force']
        user_id = options['user_id']
        batch_size = options['batch_size']
        feed_only = options['feed_only']
        job_only = options['job_only']

        update_feed = not job_only
        update_job = not feed_only

        # Construir filtros
        if user_id:
            filters = Q(id=user_id)
        elif force:
            filters = Q(is_active=True)
        else:
            # Usuarios sin al menos uno de los embeddings
            missing_feed = Q(feed_recommendations_embedding__isnull=True) if update_feed else Q()
            missing_job = Q(job_recommendations_embedding__isnull=True) if update_job else Q()

            if update_feed and update_job:
                filters = Q(is_active=True) & (missing_feed | missing_job)
            elif update_feed:
                filters = Q(is_active=True) & missing_feed
            else:
                filters = Q(is_active=True) & missing_job

        users_to_process = User.objects.filter(filters)
        total_users = users_to_process.count()

        if total_users == 0:
            self.stdout.write(
                self.style.WARNING('No hay usuarios para procesar con los criterios especificados.')
            )
            return

        scope = []
        if update_feed:
            scope.append('feed')
        if update_job:
            scope.append('job')

        self.stdout.write(
            self.style.SUCCESS(f'Procesando {total_users} usuarios (scope: {", ".join(scope)})...')
        )

        processed = 0
        feed_ok = 0
        job_ok = 0
        errors = 0

        for i in range(0, total_users, batch_size):
            batch = users_to_process[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_users - 1) // batch_size + 1
            self.stdout.write(f'Procesando lote {batch_num}/{total_batches}...')

            for user in batch:
                try:
                    user_feed_result = False
                    user_job_result = False

                    if update_feed and (force or not user.feed_recommendations_embedding):
                        user_feed_result = user_vector_service.update_user_feed_embedding(user.id)
                        if user_feed_result:
                            feed_ok += 1

                    if update_job and (force or not user.job_recommendations_embedding):
                        user_job_result = user_vector_service.update_user_job_embedding(user.id)
                        if user_job_result:
                            job_ok += 1

                    if user_feed_result or user_job_result:
                        parts = []
                        if user_feed_result:
                            parts.append('feed')
                        if user_job_result:
                            parts.append('job')
                        self.stdout.write(
                            f'  ✓ {user.first_name} {user.last_name} ({user.id}): {", ".join(parts)}'
                        )
                    else:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ {user.first_name} {user.last_name} ({user.id}): sin cambios'
                            )
                        )

                    processed += 1

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Usuario {user.id}: {str(e)}')
                    )
                    logger.error(f'Error procesando usuario {user.id}: {str(e)}')

        # Resumen final
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Procesamiento completado:'))
        self.stdout.write(f'  • Total procesados: {processed}')
        if update_feed:
            self.stdout.write(f'  • Feed embeddings actualizados: {feed_ok}')
        if update_job:
            self.stdout.write(f'  • Job embeddings actualizados: {job_ok}')
        self.stdout.write(f'  • Errores/sin cambios: {errors}')

        if feed_ok > 0 or job_ok > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ {feed_ok + job_ok} embeddings generados exitosamente.'
                )
            )
