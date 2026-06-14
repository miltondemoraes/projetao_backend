from rest_framework.routers import DefaultRouter

from relatorios.views.relatorio import RelatorioViewSet

router = DefaultRouter()
router.register(r'', RelatorioViewSet, basename='relatorio')

urlpatterns = router.urls
