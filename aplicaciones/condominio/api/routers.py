from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()

router.register(r'definir-cuota', viewsets.DefinirCuota, basename="definir-cuota")
router.register(r'cancelar-cuota', viewsets.CancelarCuota, basename="cancelar-cuota")
router.register(r'cobrar-cuota', viewsets.CobrarCuota, basename="cobrar-cuota")
router.register(r'validar-cobro', viewsets.ValidarCobro, basename="validar-cobro")

router.register(r'registrar-tipo-gasto', viewsets.RegistrarTipoGasto, basename="registrar-tipo-gasto")
router.register(r'actualizar-tipo-gasto', viewsets.ActualizarTipoGasto, basename="actualizar-tipo-gasto")
router.register(r'registrar-sub-tipo-gasto', viewsets.RegistrarSubTipoGasto, basename="registrar-sub-tipo-gasto")
router.register(r'actualizar-sub-tipo-gasto', viewsets.ActualizarSubTipoGasto, basename="actualizar-sub-tipo-gasto")
router.register(r'registrar-proveedor', viewsets.RegistrarProveedor, basename="registrar-proveedor")
router.register(r'actualizar-proveedor', viewsets.ActualizarProveedor, basename="actualizar-proveedor")
router.register(r'actualizar-situacion-proveedor', viewsets.ActualizarSituacionProveedor, basename="actualizar-situacion-proveedor")
router.register(r'registrar-comentario-proveedor', viewsets.RegistrarComentarioProveedor, basename="registrar-comentario-proveedor")
router.register(r'registrar-gasto-pagado', viewsets.RegistrarGastoPagado, basename="registrar-gasto-pagado")
router.register(r'cancelar-gasto-pagado', viewsets.CancelarGastoPagado, basename="cancelar-gasto-pagado")
router.register(r'autorizar-gasto-pagado', viewsets.AutorizarGastoPagado, basename="autorizar-gasto-pagado")

router.register(r'registrar-comite', viewsets.RegistrarComite, basename="registrar-comite")
router.register(r"transferir-administracion", viewsets.TransferirAdministracion, basename="transferir-administracion")
router.register(r"modificar-integrante-comite", viewsets.ModificarIntegrantesComite, basename="modificar-integrante-comite")

urlpatterns = router.urls
