from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from apps.jobs.domain.entities.postulants import Postulants
from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.infrastructure.api.v1.serializers.postulants_serializer import PostulantsSerializer


class PostulantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Postulants.objects.get(pk=pk)
        except Postulants.DoesNotExist:
            return None

    def get_queryset(self):
        """
        Filtra las postulaciones según el tipo de usuario
        """
        user = self.request.user
        if hasattr(user, 'company_name'):  # Es una compañía
            # La compañía ve todas las postulaciones a sus trabajos
            return Postulants.objects.filter(job__company=user)
        else:  # Es un usuario normal
            # El usuario solo ve sus propias postulaciones
            return Postulants.objects.filter(user=user)

    def get(self, request, pk=None):
        if pk:
            postulant = self.get_object(pk)
            if not postulant:
                return Response({'error': 'Postulación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos
            user = request.user
            if hasattr(user, 'company_name'):
                # Las compañías solo ven postulaciones a sus trabajos
                if postulant.job.company != user:
                    return Response({'error': 'No tienes permisos para ver esta postulación'}, 
                                  status=status.HTTP_403_FORBIDDEN)
            else:
                # Los usuarios solo ven sus propias postulaciones
                if postulant.user != user:
                    return Response({'error': 'No tienes permisos para ver esta postulación'}, 
                                  status=status.HTTP_403_FORBIDDEN)
                    
            serializer = PostulantsSerializer(postulant)
            return Response(serializer.data)
        else:
            # Aplicar filtros
            queryset = self.get_queryset()
            job_id = request.GET.get('job_id', '')
            status_filter = request.GET.get('status', '')
            
            if job_id:
                queryset = queryset.filter(job_id=job_id)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            serializer = PostulantsSerializer(queryset, many=True)
            return Response(serializer.data)

    def post(self, request):
        # Solo los usuarios normales pueden postularse
        if hasattr(request.user, 'company_name'):
            return Response({'error': 'Las compañías no pueden postularse a trabajos'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        job_id = request.data.get('job')
        if not job_id:
            return Response({'error': 'ID del trabajo es requerido'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            job = Jobs.objects.get(id=job_id, status='active')
        except Jobs.DoesNotExist:
            return Response({'error': 'Trabajo no encontrado o no activo'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si ya se postuló
        if Postulants.objects.filter(user=request.user, job=job).exists():
            return Response({'error': 'Ya te has postulado a este trabajo'}, 
                          status=status.HTTP_400_BAD_REQUEST)
          # Crear los datos para el serializer sin incluir job en los datos de validación
        serializer_data = request.data.copy()
        if 'job' in serializer_data:
            del serializer_data['job']
            
        serializer = PostulantsSerializer(data=serializer_data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        postulant = self.get_object(pk)
        if not postulant:
            return Response({'error': 'Postulación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        # Solo las compañías pueden actualizar el estado de las postulaciones
        if hasattr(user, 'company_name'):
            if postulant.job.company != user:
                return Response({'error': 'No tienes permisos para actualizar esta postulación'}, 
                              status=status.HTTP_403_FORBIDDEN)
        else:
            # Los usuarios solo pueden actualizar su carta de presentación
            if postulant.user != user:
                return Response({'error': 'No tienes permisos para actualizar esta postulación'}, 
                              status=status.HTTP_403_FORBIDDEN)
            # Limitar campos que pueden actualizar
            allowed_fields = ['cover_letter', 'resume_file']
            data = {k: v for k, v in request.data.items() if k in allowed_fields}
            request.data.clear()
            request.data.update(data)
        
        serializer = PostulantsSerializer(postulant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        postulant = self.get_object(pk)
        if not postulant:
            return Response({'error': 'Postulación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Solo el usuario que se postuló puede eliminar su postulación
        if hasattr(request.user, 'company_name') or postulant.user != request.user:
            return Response({'error': 'No tienes permisos para eliminar esta postulación'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        postulant.delete()
        return Response({'message': 'Postulación eliminada exitosamente'}, status=status.HTTP_204_NO_CONTENT)

