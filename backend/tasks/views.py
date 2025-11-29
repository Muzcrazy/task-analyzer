from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer
from .scoring import compute_scores

class AnalyzeTasksView(APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({'error': 'Expected a list of tasks'}, status=status.HTTP_400_BAD_REQUEST)
        validated = []
        for t in data:
            ser = TaskInputSerializer(data=t)
            if not ser.is_valid():
                continue
            validated.append(ser.validated_data)

        strategy = request.query_params.get('strategy', 'smart')
        scored = compute_scores(validated, strategy=strategy)
        return Response(scored)

class SuggestTasksView(APIView):
    def get(self, request):
        import json
        payload = request.query_params.get('tasks')
        strategy = request.query_params.get('strategy', 'smart')
        try:
            tasks = json.loads(payload) if payload else []
        except Exception:
            return Response({'error': 'invalid tasks payload'}, status=status.HTTP_400_BAD_REQUEST)

        scored = compute_scores(tasks, strategy=strategy)
        top3 = scored[:3]
        for t in top3:
            t['explanation'] = f"Score {t['score']}: {t['reason']}"
        return Response(top3)
