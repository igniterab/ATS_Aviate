from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .models import Candidate
from .serializers import CandidateSerializer
from django.db.models import Count, Q

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        email = request.data.get('email')
        
        if email != instance.email:
            return Response(
                {"email": ["You cannot update email, as it is unique."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def search(self, request):
        name = request.query_params.get('name', '')
        if name:
            name_words = name.lower().split()
            filter_condition = Q()

            for word in name_words:
                filter_condition |= Q(name__icontains=word)

            candidates = Candidate.objects.filter(filter_condition)
            candidates = candidates.annotate(
                relevancy=Count('id', filter=Q(name__icontains=name))
            ).order_by('-relevancy')
            
            serializer = self.get_serializer(candidates, many=True)
            return Response(serializer.data)

        return Response({"detail": "No query parameter provided"}, status=status.HTTP_400_BAD_REQUEST)
