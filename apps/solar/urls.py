from rest_framework.routers import DefaultRouter,SimpleRouter
from .views import ConsumoViewSet

router = SimpleRouter()
router.register(r'consumos', ConsumoViewSet, basename='consumos')

urlpatterns = router.urls