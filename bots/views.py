from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import History, Raspberry, Command
from .serializers import HistorySerializer,  RaspberrySerializer, CommandSerializer, PendingCommandSerializer, AckCommandSerializer, CommandResponseSerializer, AckResponseSerializer
from rest_framework.permissions import IsAuthenticated

class HistoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = History.objects.all()
    serializer_class = HistorySerializer

class HistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = History.objects.all().order_by("-created_at")[:30] #filter(status='pending')
    serializer_class = HistorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por raspberry si se proporciona
        raspberry_slug = self.request.query_params.get('raspberry')
        if raspberry_slug:
            queryset = queryset.filter(raspberry__slug=raspberry_slug)
            
        # Filtrar por comando si se proporciona
        command_slug = self.request.query_params.get('command')
        if command_slug:
            queryset = queryset.filter(command__slug=command_slug)
            
        # Filtrar por status si se proporciona
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

class HistoryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = History.objects.all()
    serializer_class = HistorySerializer

class RaspberryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Raspberry.objects.all()
    serializer_class = RaspberrySerializer

class CommandListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Command.objects.all()
    serializer_class = CommandSerializer

class PendingCommandView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, raspberry_slug):
        """
        Obtiene el primer comando pendiente para el Raspberry Pi
        """
        try:
            pending_command = History.objects.filter(
                raspberry__slug=raspberry_slug,
                status='pending'
            ).first()
            
            if not pending_command:
                return Response(
                    {'message': 'No pending commands'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CommandResponseSerializer({
                'id': pending_command.id,
                'command': pending_command.command.slug
            })

            # Marcar como enviado
            pending_command.status = 'sent'
            pending_command.save()

            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'message': f'Error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AckCommandView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, raspberry_slug):
        """
        Reconoce la ejecución de un comando
        """
        try:
            ack_serializer = AckCommandSerializer(data=request.data)
            if not ack_serializer.is_valid():
                return Response(
                    {'message': 'Invalid data', 'errors': ack_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            command_id = ack_serializer.validated_data['command_id']
            result = ack_serializer.validated_data['result']

            command_history = get_object_or_404(
                History, 
                id=command_id,
                raspberry__slug=raspberry_slug
            )

            command_history.status = 'executed'
            command_history.result = result
            command_history.save()

            response_serializer = AckResponseSerializer({'status': 'success'})
            return Response(response_serializer.data)
            
        except History.DoesNotExist:
            return Response(
                {'message': 'Command not found for this Raspberry Pi'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'message': f'Error updating command status: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )