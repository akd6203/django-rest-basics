from django.http import request
from django.shortcuts import render, get_object_or_404
from poll import serializers
from poll.serializers import ChoiceSerializer, QuestionSerializer
from poll.models import *
from django.http.response import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import  Response
from rest_framework import generics, mixins 
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet
from django_filters import rest_framework as filters
'''
VIewSets amd routers
'''
class CsrfExemptSessionAuthentication(SessionAuthentication):
    
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class PollFilter(FilterSet):
    tags = filters.CharFilter(method='filter_by_tags')

    class Meta:
        model = Question
        fields=['tags',]

    def filter_by_tags(self, queryset,name,value):
        tag_names = value.strip().split(",")
        tags = Tag.objects.filter(name__in=tag_names)
        return queryset.filter(tags__in=tags).distinct() #unique



class PollVIewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    lookup_field = 'id'
    filter_backends=(DjangoFilterBackend,)
    filter_class=PollFilter
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @action(detail=True, methods=["GET"])
    def choices(self, request,id=None):
        question = self.get_object()
        choices = Choice.objects.filter(question=question)
        serializer = ChoiceSerializer(choices, many=True)
        return Response(serializer.data, status=200)

    
    @action(detail=True, methods=["POST"])
    def choice(self, request,id=None):
        question = self.get_object()
        data = request.data
        data["question"] = question.id
        serializer = ChoiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class PollGAPI(generics.GenericAPIView,
            mixins.ListModelMixin,
            mixins.RetrieveModelMixin,
            mixins.CreateModelMixin,
            mixins.UpdateModelMixin,
            mixins.DestroyModelMixin):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    lookup_field='id'
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, id=None):
        if id:
            return self.retrieve(id)
        else:
            return self.list(request)

    def post(self,request):
        return self.create(request)

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)

    def put(self, request, id=None):
        return self.update(request,id)
    
    def perform_update(self, serializer):
        serializer.save(created_by = self.request.user)

    def delete(self, request, id=None):
        return self.destroy(id)

class PollAPIView(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = request.data 
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400) 

class PollDetaileView(APIView):
    def get_object(self,id):
        try:
            instance = Question.objects.get(id=id)
            return instance 
        except Question.DoesNotExist as e:
            return Response({'message':'No data found with this ID'}, status=404)
    
    def get(self, request, id=None):
        instance = self.get_object(id)
        serializer = QuestionSerializer(instance)
        return Response(serializer.data)

    def put(self, request, id=None):
        instance = self.get_object(id)
        serializer = QuestionSerializer(instance, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    def delete(self, request,id=None):
        instance = self.get_object(id)
        instance.delete()
        return Response(status=204)        
@csrf_exempt
def poll(request):
    if request.method=="GET":
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return JsonResponse(serializer.data, safe=False)
        
    elif request.method=="POST":
        data = JSONParser().parse(request)
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def poll_details(request,id):
    try:
        instance = Question.objects.get(id=id)
    except Question.DoesNotExist as e:
        return JsonResponse({"error":"No Question found with this ID"}, status=404)

    if request.method=="GET":
        serializer = QuestionSerializer(instance)
        return JsonResponse(serializer.data)

    elif request.method=="PUT":
        data = JSONParser().parse(request)
        serializer = QuestionSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method=="DELETE":
        instance.delete()
        return HttpResponse(status=204)