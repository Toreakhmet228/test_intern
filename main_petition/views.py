from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import generics, permissions
from django.contrib.auth import authenticate
from .serialzer import RegisterSerializer, UserSerializer

from main_petition.serialzer import PetitionSerializer
from .models import Petition, Vote

class AddVoteToPetition(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, number_petition):
        petition = get_object_or_404(Petition, id=number_petition)
        
        if Vote.objects.filter(user=request.user, petition=petition).exists():
            return Response({"detail": "Вы уже голосовали за эту петицию."}, status=status.HTTP_400_BAD_REQUEST)

        Vote.objects.create(user=request.user, petition=petition)

        petition.votes_count += 1
        petition.save()

        return Response({"detail": "Голос успешно добавлен."}, status=status.HTTP_201_CREATED)
    
class RemoveVoteFromPetition(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, number_petition):
        petition = get_object_or_404(Petition, id=number_petition)

        try:
            vote = Vote.objects.get(user=request.user, petition=petition)
            vote.delete()

            petition.votes_count -= 1
            petition.save()

            return Response({"detail": "Голос успешно удалён."}, status=status.HTTP_204_NO_CONTENT)
        except Vote.DoesNotExist:
            return Response({"detail": "Вы не голосовали за эту петицию."}, status=status.HTTP_400_BAD_REQUEST)


class PetitionList(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        petitions = Petition.objects.all()
        serializer = PetitionSerializer(petitions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PetitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PetitionDetail(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, pk):
        petition = get_object_or_404(Petition, id=pk)
        serializer = PetitionSerializer(petition)
        return Response(serializer.data)

    def put(self, request, pk):
        petition = get_object_or_404(Petition, id=pk)
        serializer = PetitionSerializer(petition, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        petition = get_object_or_404(Petition, id=pk)
        petition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=400)