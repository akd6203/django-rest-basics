from employee.views import EmployeeViewSet, UploadView
from django.urls import path,include 
from employee.urls import * 
from rest_framework import routers 

router = routers.SimpleRouter()
# router = routers.DefaultRouter()
router.register('employee', EmployeeViewSet)

urlpatterns=[
    path('', include(router.urls)),
    path('upload', UploadView.as_view(), name='file_upload')
]