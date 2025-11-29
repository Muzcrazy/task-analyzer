from rest_framework import serializers

class TaskInputSerializer(serializers.Serializer):
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False)
    importance = serializers.IntegerField(required=False)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False)

class TaskOutputSerializer(serializers.Serializer):
    title = serializers.CharField()
    due_date = serializers.DateField(allow_null=True)
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.CharField())
    score = serializers.FloatField()
    reason = serializers.CharField()
