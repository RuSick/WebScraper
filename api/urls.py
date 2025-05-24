
from rest_framework.routers import DefaultRouter
from api.views import ArticleViewSet, SourceViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'sources', SourceViewSet)
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
