from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.jobs.domain.entities.postulants import Postulants
from apps.jobs.infrastructure.api.v1.serializers.postulants_serializer import PostulantsSerializer


class PostulantsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Postulants.objects.get(pk=pk)
        except Postulants.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            postulant = self.get_object(pk)
            if not postulant:
                return Response({'error': 'Postulant not found'}, status=404)
            serializer = PostulantsSerializer(postulant)
            return Response(serializer.data)
        else:
            postulants = Postulants.objects.all()
            serializer = PostulantsSerializer(postulants, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = PostulantsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        postulant = self.get_object(pk)
        if not postulant:
            return Response({'error': 'Postulant not found'}, status=404)
        serializer = PostulantsSerializer(postulant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        postulant = self.get_object(pk)
        if not postulant:
            return Response({'error': 'Postulant not found'}, status=404)
        postulant.delete()
        return Response({'message': 'Postulant deleted successfully'}, status=204)

