from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReviewCreateViewSet.as_view({'post': 'post'}), name='create-view'),
    path("retrieve/<str:task_id>/", views.ReviewStatusViewSet.as_view({'get': 'retrieve'}), name='review-status'),
    path("<int:pk>/", views.ReviewStatusViewSet.as_view({'get': 'get', 'put': 'put', 'delete': 'delete'}), name='review-status'),
    path("search", views.search, name="search"),
]