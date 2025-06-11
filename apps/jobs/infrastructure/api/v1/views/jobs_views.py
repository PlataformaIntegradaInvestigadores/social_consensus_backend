from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.infrastructure.api.v1.serializers.jobs_serializer import JobsSerializer


# apps/jobs/infrastructure/api/v1/views/jobs_views.py

class JobsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Jobs.objects.get(pk=pk)
        except Jobs.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            job = self.get_object(pk)
            if not job:
                return Response({'error': 'Job not found'}, status=404)
            serializer = JobsSerializer(job)
            return Response(serializer.data)
        else:
            jobs = Jobs.objects.all()
            serializer = JobsSerializer(jobs, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = JobsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        job = self.get_object(pk)
        if not job:
            return Response({'error': 'Job not found'}, status=404)
        serializer = JobsSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        job = self.get_object(pk)
        if not job:
            return Response({'error': 'Job not found'}, status=404)
        job.delete()
        return Response({'message': 'Job deleted successfully'}, status=204)

