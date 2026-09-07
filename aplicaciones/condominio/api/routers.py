from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()

router.register(r'definir-cuota', viewsets.DefinirCuota, basename="definir-cuota")
router.register(r'cancelar-cuota', viewsets.CancelarCuota, basename="cancelar-cuota")
router.register(r'cobrar-cuota', viewsets.CobrarCuota, basename="cobrar-cuota")
router.register(r'validar-cobro', viewsets.ValidarCobro, basename="validar-cobro")

urlpatterns = router.urls
