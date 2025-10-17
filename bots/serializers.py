from rest_framework import serializers
from .models import History, Raspberry, Command

class HistorySerializer(serializers.ModelSerializer):
    # Campos para mostrar información relacionada (solo lectura)
    raspberry_name = serializers.CharField(source='raspberry.name', read_only=True)
    command_name = serializers.CharField(source='command.name', read_only=True)
    command_comm = serializers.CharField(source='command.comm', read_only=True)  # Nuevo campo
    
    # Campos para la creación (escritura)
    raspberry_slug = serializers.SlugRelatedField(
        queryset=Raspberry.objects.all(),
        slug_field='slug',
        write_only=True,
        source='raspberry'
    )
    
    command_slug = serializers.SlugRelatedField(
        queryset=Command.objects.all(),
        slug_field='slug',  # Ahora usa el campo slug
        write_only=True,
        source='command'
    )

    class Meta:
        model = History
        fields = [
            'id',
            'raspberry_slug', 'raspberry_name',
            'command_slug', 'command_name', 'command_comm',
            'status', 'result',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 
            'raspberry_name', 'command_name', 'command_comm'
        ]

class RaspberrySerializer(serializers.ModelSerializer):
    # Campo calculado para contar histories asociados
    history_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Raspberry
        fields = [
            'id', 'name', 'slug', 
            'history_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'history_count']
    
    def get_history_count(self, obj):
        return obj.history_set.count()
    
class CommandSerializer(serializers.ModelSerializer):
    # Campo calculado para contar usage
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Command
        fields = [
            'id', 'name', 'comm', 'slug',
            'usage_count', 'created_at', 'updated_at'
        ]   
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count']
    
    def get_usage_count(self, obj):
        return obj.history_set.count()
    
class PendingCommandSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    command = serializers.CharField(source='command.comm')

class AckCommandSerializer(serializers.Serializer):
    command_id = serializers.IntegerField()
    result = serializers.CharField()

class CommandResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    command = serializers.CharField()

class AckResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default='success')