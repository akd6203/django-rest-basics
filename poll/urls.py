from django.urls import path
from django.urls.conf import include 
from poll.views import * 
from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
router.register("poll", PollVIewSet)

poll_list_view = PollVIewSet.as_view({
    "get":"list",
    "post":"create",
})

urlpatterns = [
    # path('poll/', poll),
    path('poll/<int:id>/', poll_details),
    path('cpoll/', PollAPIView.as_view()),
    path('cpoll/<int:id>/', PollDetaileView.as_view()),

    # Generic API Urls 
    path('generics/poll/', PollGAPI.as_view()),
    path('generics/poll/<int:id>/', PollGAPI.as_view()),

    # Viewsets and routers
    path("vs_poll/", include(router.urls)),
]