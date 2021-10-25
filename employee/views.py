from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action, authentication_classes, parser_classes, permission_classes
from employee.serializers import EmployeeSerializer,LoginSerializer, ProfileSerializer
from django.shortcuts import render
from rest_framework import serializers, viewsets
from employee.serializers import EmployeeSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from rest_framework.authtoken.models import Token 
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import generics, mixins 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters, FilterSet
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated

class LoginView(APIView):
    serializer_class=LoginSerializer

    @csrf_exempt
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request,user)
        token,created = Token.objects.get_or_create(user=user)
        return Response({"token":token.key}, status=200)

class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    def post(self, request):
        django_logout(request)
        return Response(status=204)

class EmployeeFilter(FilterSet):
    # is_active = filters.CharFilter('is_active')
    designation = filters.CharFilter('profile__designation')
    min_salary = filters.CharFilter(method="filter_by_min_salary")
    max_salary = filters.CharFilter(method="filter_by_max_salary")

    class Meta:
        model = User 
        fields = ('is_active', 'designation', 'username')

    def filter_by_min_salary(self, queryset, name, value):
        queryset = queryset.filter(profile__salary__gt=value)
        return queryset

    def filter_by_max_salary(self, queryset, name, value):
        queryset = queryset.filter(profile__salary__lt=value)
        return queryset

    
class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    queryset = User.objects.all()

    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    # filter_fields=('is_active','profile__designation')
    filter_class = EmployeeFilter

    ordering_fields=('username','profile__designation')
    search_fields=('username',  'profile__designation')
    ordering=('username') #default 
    parser_classes=(JsonResponse, MultiPartParser, FormParser)

            

    # def get_queryset(self): #override queryset
    #     queryset = User.objects.all()
    #     active = self.request.query_params.get('is_active','')
    #     if active:
    #         if active=='True':
    #             active = True 
    #         elif active=='False':
    #             active=False 
    #         else:
    #             queryset=queryset
    #         queryset=queryset.filter(is_active=active)
    #     else:
    #         queryset=queryset
    #     return queryset


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = EmployeeFilter
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    ordering_fields = ('is_active','username')
    oredring=('username')
    search_fields = ('username', 'first_name')

    @action(detail=True,methods=['PUT'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = user.profile
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

class UploadView(APIView):
    parser_classes = (FileUploadParser, )
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        file = request.data.get('file',None)
        import pdb; pdb.set_trace()
        print(file)
        if file:
            return Response({"message":"File is received"}, status=200)
        else:
            return Response({"message":"File is missing"}, status=400)