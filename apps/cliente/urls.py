from rest_framework.routers import DefaultRouter,SimpleRouter
from .views import ListaClienteViewSet, ClienteViewSet

router = SimpleRouter()
router.register(r'clientes', ListaClienteViewSet, basename='clientes')
router.register(r'clientes-completo', ClienteViewSet, basename='cliente')

urlpatterns = router.urls