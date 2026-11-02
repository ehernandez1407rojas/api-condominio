from rest_framework import serializers, pagination
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.validators import RegexValidator, validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


from django.utils import timezone
from django.db.models import Q
from .constants import PASSWORD_MIN_LENGTH, MESES_EXIGIBLES_POSTERIORES_HOY

from ..models import *


class NormalizaTextoMixin:

    campos_excluidos_normalizacion = {'password', 'email_whatsapp'}

    def to_internal_value(self, data):
        data = data.copy()

        for field_name, field in self.fields.items():

            if field_name not in data:
                continue

            if field_name in self.campos_excluidos_normalizacion:
                continue

            valor = data[field_name]

            if not isinstance(valor, str):
                continue

            if isinstance(field, serializers.EmailField):
                data[field_name] = valor.lower()

            elif isinstance(field, serializers.CharField):
                data[field_name] = valor.upper()

        return super().to_internal_value(data)

class PaginationSerializer(pagination.PageNumberPagination):
    page_size = 3
    max_page_size = 20


class CreoModificoSerializer(NormalizaTextoMixin, serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'fecha_modificacion', 'usuario_modifico')
                                
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agrega claims personalizados
        token['user_id'] = user.id
        token['condominio_id'] = user.condominio.id if user.condominio else None
        # token['tipo_usuario'] = user.tipo_usuario
        token['nombre_completo'] = user.nombre_completo

        if user.condominio:            
            roles = UsuarioRol.objects.filter(
                usuario=user,
                condominio=user.condominio,
                activo=True
            ).filter(
                Q(fecha_fin__isnull=True) |
                Q(fecha_fin__gte=timezone.localdate())
            ).values_list(
                'rol__clave',
                flat=True
            )

            token['roles'] = list(roles)
        else:
            token['roles'] = []

        return token
    
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
            
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'email_whatsapp', 
            'nombre_completo',                                     
            'password'            
        ]
        extra_kwargs = {
            'password': {'write_only': True}                        
        }

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            email_whatsapp=validated_data['email_whatsapp'],
            nombre_completo=validated_data['nombre_completo'],
            password=validated_data['password'],                        
        )
        return user

# seralizaser de las tablas transaccionales ---        
class CondominioSerializer(CreoModificoSerializer):
    class Meta(CreoModificoSerializer.Meta):        
        model = Condominio
        fields = ['id', 'nombre', 'direccion']        
                
    def get_string_fields(self):
        base_fields = super().get_string_fields()
        return [field for field in base_fields if field != 'correo']  # Excluye campo

# 1. Serializer para la PETICIÓN (Request)
class RegistrarCondominioSerializer(NormalizaTextoMixin, serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    nombre_corto = serializers.CharField(max_length=20)
    direccion = serializers.CharField(max_length=100)
    inicio_servicio = serializers.DateField()
    propiedad_cantidad = serializers.IntegerField()
    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )

    def validate_email_whatsapp(self, value):
        valor = value.strip()

        # 1. Si son solo números, es un WhatsApp válido
        if valor.isdigit():
            return valor

        # 2. Si no son solo números, verificar si es un email válido
        try:
            validate_email(valor)
            return valor
        except DjangoValidationError:
            raise serializers.ValidationError(
                'Ingrese un correo electrónico válido o solo números para el WhatsApp.'
            )

# 2. (Opcional) Serializer para la RESPUESTA (Response)
class RegistrarCondominioResponseSerializer(serializers.Serializer):
    condominio_id = serializers.IntegerField(        source="condominio.id"    )
    nombre = serializers.CharField(        source="condominio.nombre"    )
    nombre_corto = serializers.CharField(        source="condominio.nombre_corto"    )
    usuario_id = serializers.IntegerField(        source="usuario.id"    )
    nombre_completo = serializers.CharField(        source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField(        source="usuario.email_whatsapp"    )    
    rol = serializers.CharField(        source="usuario_rol.rol.clave"    ) 

class UsuarioRolSerializer(serializers.Serializer):
    class Meta:
        model = UsuarioRol
        fields = (
            '__all__'
    )

class PropiedadSerializer( CreoModificoSerializer):
    class Meta(CreoModificoSerializer.Meta):
        model = Propiedad
        
    def get_string_fields(self):
        base_fields = super().get_string_fields()
        return [field for field in base_fields if field != 'correo']  # Excluye campo
    
                        


class EstadoCondominioSerializer(NormalizaTextoMixin, serializers.ModelSerializer):
    class Meta:
        model = EstadoCondominio
        fields = (
            '__all__'
        )        

class RolSerializer(NormalizaTextoMixin, serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = (
            '__all__'
        )         



class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(
        write_only=True
    )

    password_nueva = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )        

class CambiarPasswordResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()    

# # Serializer de entrada para registrar un propietario y su propiedad.
class RegistrarPropietarioSerializer(NormalizaTextoMixin, serializers.Serializer):
    nombre = serializers.CharField(max_length=50)    
    direccion = serializers.CharField(max_length=100)    

    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)

#  (Opcional) Serializer para la RESPUESTA del resgistro propiedad
class RegistrarPropietarioResponseSerializer(serializers.Serializer):
    condominio_id = serializers.IntegerField( source="propiedad.condominio.id"    )
    nombre = serializers.CharField( source="propiedad.nombre"    )    
    usuario_id = serializers.IntegerField( source="usuario.id"    )
    nombre_completo = serializers.CharField( source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField( source="usuario.email_whatsapp"    )
    rol = serializers.CharField( source="usuario_rol.rol.clave"    )       

class TokenUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenUsuario
        fields = (
            '__all__'
    )    

class TipoTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoToken
        fields = (
            '__all__'
    )         



class GenerarTokenSerializer(serializers.Serializer):
    email_whatsapp = serializers.CharField(max_length=50)
    tipo_token = serializers.CharField(max_length=50)

class GenerarTokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
                    
class EstablecerPasswordSerializer(serializers.Serializer):
    token = serializers.IntegerField()
    nuevo_password = serializers.CharField(
        write_only=True,
        max_length=50,
        min_length=PASSWORD_MIN_LENGTH)

class EstablecerPasswordResponseSerializer(serializers.Serializer):    
    mensaje = serializers.CharField(max_length=50)    
                  

# # Serializer de entrada para registrar un propietario y su propiedad.
class RegistrarPropietarioTokenSerializer(NormalizaTextoMixin, serializers.Serializer):
    nombre_propiedad = serializers.CharField(max_length=50)    
    direccion = serializers.CharField(max_length=100)    

    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)

#  Serializer para la RESPUESTA del resgistro propiedad, propietario y token
class RegistrarPropietarioTokenResponseSerializer(serializers.Serializer):
    condominio_id = serializers.IntegerField( source="propiedad.condominio.id"    )
    nombre = serializers.CharField( source="propiedad.nombre"    )    
    usuario_id = serializers.IntegerField( source="usuario.id"    )
    nombre_completo = serializers.CharField( source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField( source="usuario.email_whatsapp"    )
    rol = serializers.CharField( source="usuario_rol.rol.clave"    )    
    token_temporal = serializers.IntegerField() 

# # Serializer de entrada para registrar un conserje.
class RegistrarConserjeTokenSerializer(NormalizaTextoMixin, serializers.Serializer):    
    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)

# # Serializer de respuesta para registrar un conserje.
class RegistrarConserjeTokenResponseSerializer(serializers.Serializer): 
    condominio_id = serializers.IntegerField( source="usuario.condominio.id"    )   
    usuario_id = serializers.IntegerField( source="usuario.id"    )
    nombre_completo = serializers.CharField( source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField( source="usuario.email_whatsapp"    )
    rol = serializers.CharField( source="usuario_rol.rol.clave"    )    
    token_temporal = serializers.IntegerField() 


# la basica que pone todos los campos en el payload
# se descarta en requerimientos reales de negocio
""" 
class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ('__all__')

class CuotaCobradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaCobrada
        fields = (
            '__all__'
    )     
"""

# # Serializer  para registrar una cuota y las cuotas exigibles de manera interna a los propietarios
class DefinirCuotaSerializer(NormalizaTextoMixin, serializers.Serializer): 
    tipo_cuota = serializers.PrimaryKeyRelatedField(
        queryset=TipoCuota.objects.all(),
        help_text="ID del Tipo de Cuota. Opciones válidas: 1=ORDINARIA, 2=EXTRAORDINARIA"        
    ) 

    nombre = serializers.CharField(max_length=100)
    importe = serializers.DecimalField(decimal_places=2, max_digits=12)
    aplica_desde = serializers.DateField()
    aplica_hasta = serializers.DateField()    
    
# # Serializer de respuesta por el registro una cuota y las cuotas exigibles de manera interna a los propietarios
class DefinirCuotaResponseSerializer(serializers.Serializer): 
    nombre = serializers.CharField()
    tipo_cuota = serializers.CharField()
    cuotas_exigibles = serializers.IntegerField()

  
# # Serializer  para registrar la cancelacion de una cuota y las cuotas exigibles pendientes de manera interna a los propietarios
class CancelarCuotaSerializer(NormalizaTextoMixin, serializers.Serializer): 
    cuota = serializers.PrimaryKeyRelatedField(
            queryset=Cuota.objects.all()
        )    
    comentario_cancelacion = serializers.CharField(max_length=100)

# # Serializer  para la respuesta de registrar la cancelacion de una cuota y las cuotas exigibles pendientes de manera interna a los propietarios
class CancelarCuotaResponseSerializer(serializers.Serializer): 
    nombre = serializers.CharField()   
    tipo_cuota = serializers.CharField()
    cuotas_exigibles_canceladas = serializers.IntegerField()    

# # Serializer  para registrar el cobro de una cuota
class CobrarCuotaSerializer(NormalizaTextoMixin, serializers.Serializer): 
    propiedad = serializers.PrimaryKeyRelatedField(queryset=Propiedad.objects.all())
    cuota_exigible = serializers.PrimaryKeyRelatedField(queryset=CuotaExigible.objects.all())
    importe_cobrado = serializers.DecimalField(decimal_places=2, max_digits=12)
    descripcion_comprobante = serializers.CharField(max_length=100)


# # Serializer  para la respuesta de registrar el cobro de una cuota
class CobrarCuotaResponseSerializer(serializers.Serializer): 
    propiedad = serializers.CharField()   
    importe_cobrado = serializers.DecimalField(decimal_places=2, max_digits=12)


# # Serializer  para validar el cobro de una cuota
class ValidarCobroSerializer(NormalizaTextoMixin, serializers.Serializer):     
    cuota_cobrada = serializers.PrimaryKeyRelatedField(queryset=CuotaCobrada.objects.all())    
    comentario_validacion = serializers.CharField(max_length=100)


# # Serializer  para la respuesta de validar el cobro de una cuota
class ValidarCobroResponseSerializer(serializers.Serializer): 
    comentario = serializers.CharField()   
    

# # Serializer  para validar el registro de un tipo gasto
class RegistrarTipoGastoSerializer(NormalizaTextoMixin,serializers.Serializer):     
    clave = serializers.CharField(max_length=50)    
    descripcion = serializers.CharField(max_length=100)
    orden = serializers.DecimalField(max_digits=5, decimal_places=2)


# # Serializer  para enviar  la respuesta del registro de un tipo gasto
class RegistrarTipoGastoResponseSerializer(serializers.Serializer):    
    id = serializers.IntegerField()
    clave = serializers.CharField()
    descripcion = serializers.CharField()
    orden = serializers.DecimalField(max_digits=5, decimal_places=2)

# # Serializer  para validar la actulizacion  de un tipo gasto
class ActualizarTipoGastoSerializer(NormalizaTextoMixin,serializers.Serializer):    
    clave = serializers.CharField(max_length=50, required=False)    
    descripcion = serializers.CharField(max_length=100, required=False)
    orden = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


# # Serializer  para enviar  la respuesta de la actualizacion de un tipo gasto
class ActualizarTipoGastoResponseSerializer(serializers.Serializer):    
    id = serializers.IntegerField()
    clave = serializers.CharField()
    descripcion = serializers.CharField()
    orden = serializers.DecimalField(max_digits=5, decimal_places=2)    
    
# # Serializer  para validar el registro de un sub tipo gasto
class RegistrarSubTipoGastoSerializer(NormalizaTextoMixin, serializers.Serializer):   
    tipo_gasto = serializers.PrimaryKeyRelatedField(queryset=TipoGasto.objects.all(), error_messages={
            'does_not_exist': 'El tipo de gasto seleccionado no existe.'
        })  
    clave = serializers.CharField(max_length=50)    
    descripcion = serializers.CharField(max_length=100)
    orden = serializers.DecimalField(max_digits=5, decimal_places=2)


# # Serializer  para enviar  la respuesta del registro de un sub tipo gasto
class RegistrarSubTipoGastoResponseSerializer(serializers.Serializer):    
    id = serializers.IntegerField()
    clave = serializers.CharField()
    descripcion = serializers.CharField()
    orden = serializers.DecimalField(max_digits=5, decimal_places=2)

# # Serializer  para validar la actualizacion  de un sub tipo gasto
class ActualizarSubTipoGastoSerializer(NormalizaTextoMixin,serializers.Serializer):    
    clave = serializers.CharField(max_length=50, required=False)    
    descripcion = serializers.CharField(max_length=100, required=False)
    orden = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


# # Serializer  para enviar  la respuesta de la actualizacion de un sub tipo gasto
class ActualizarSubTipoGastoResponseSerializer(serializers.Serializer):    
    id = serializers.IntegerField()
    clave = serializers.CharField()
    descripcion = serializers.CharField()
    orden = serializers.DecimalField(max_digits=5, decimal_places=2)    

# # Serializer  para validar el registro del proveedor
class RegistrarProveedorSerializer(    NormalizaTextoMixin,    serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    direccion = serializers.CharField(max_length=100)
    celular = serializers.CharField( max_length=30, min_length=10, required=False, allow_blank=True
            , validators=[
                RegexValidator(
                    regex=r'^\d+$',
                    message='El celular debe contener solamente números.',
                    code='invalid_numeric'
                )
            ]
            , allow_null=True )
    correo = serializers.EmailField( max_length=30, required=False, allow_blank=True, allow_null=True )   

    def validate_celular(self, value):
        if value == '':
            return None

        return value

    def validate_correo(self, value):
        if value == '':
            return None

        return value 

class RegistrarProveedorResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    direccion = serializers.CharField()
    celular = serializers.CharField(
        allow_null=True
    )    


class ActualizarProveedorSerializer(    NormalizaTextoMixin,    serializers.Serializer):
    nombre = serializers.CharField(max_length=50, required=False)
    direccion = serializers.CharField(max_length=100, required=False)
    celular = serializers.CharField( max_length=30, min_length=10, required=False, allow_blank=True
            , validators=[
                RegexValidator(
                    regex=r'^\d+$',
                    message='El celular debe contener solamente números.',
                    code='invalid_numeric'
                )
            ]
            , allow_null=True )
    correo = serializers.EmailField( max_length=30, required=False, allow_blank=True, allow_null=True )   

    def validate_celular(self, value):
        if value == '':
            return None

        return value

    def validate_correo(self, value):
        if value == '':
            return None

        return value 

class ActualizarProveedorResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    direccion = serializers.CharField()
    celular = serializers.CharField(
        allow_null=True
    ) 

# # Serializer  para validar la actualizacion de la situacion de un proveedor
class ActualizarSituacionProveedorSerializer(NormalizaTextoMixin,serializers.Serializer):   
    situacion_proveedor = serializers.PrimaryKeyRelatedField(queryset=SituacionProveedor.objects.all()
            , error_messages={
                'required': 'Debe indicar la situación que desea asignar al proveedor.',
                'does_not_exist': 'La situacion del proveedor seleccionado no existe.',
                'null': 'Debe indicar una situación para el proveedor.',
            }
        )      

# # Serializer  para la respuesta de la actualizacion de la situacion de un proveedor
class ActualizarSituacionProveedorResponseSerializer(serializers.Serializer):   
    nombre = serializers.CharField()
    situacion = serializers.CharField()

# # Serializer  para validar el registro de un comentario a un proveedor
class RegistrarComentarioProveedorSerializer(NormalizaTextoMixin,serializers.Serializer):   
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all()
            , error_messages={
                'required': 'Debe indicar el proveedor.',
                'does_not_exist': 'El proveedor seleccionado no existe.',
                'null': 'Debe indicar un proveedor.',
            }
        )        
    comentario = serializers.CharField(max_length=200)

# # Serializer  para la respuesta del regisgtro de comentario a un proveedor
class RegistrarComentarioProveedorResponseSerializer(serializers.Serializer):   
    nombre = serializers.CharField()
    comentario = serializers.CharField()    



# # Serializer  para validar el registro un gasto pagado
class RegistrarGastoPagadoSerializer(    NormalizaTextoMixin,    serializers.Serializer):
    tipo_gasto = serializers.PrimaryKeyRelatedField(queryset=TipoGasto.objects.all()
                , error_messages={
                    'required': 'Debe indicar un tipo de gasto.',
                    'does_not_exist': 'El tipo de gasto seleccionado no existe.',
                    'null': 'Debe indicar un tipo de gasto.',
                }                                    )
    sub_tipo_gasto = serializers.PrimaryKeyRelatedField(queryset=SubTipoGasto.objects.all()
                ,required=False
                ,allow_null=True                                        
                , error_messages={                                    
                                    'does_not_exist': 'El sub tipo de gasto seleccionado no existe.',
                                    'null': 'Debe indicar un sub tipo de gasto.',
                                }                                        )
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all()
                ,required=False
                ,allow_null=True                                     
                , error_messages={                                  
                                  'does_not_exist': 'El proveedor seleccionado no existe.',
                                  'null': 'Debe indicar un proveedor.',
                              }                                 )
    importe_pagado = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'),
                        error_messages={
                            'required': 'Debe indicar el importe pagado.',
                            'invalid': 'El importe pagado no es válido.',                            
                            'min_value': 'El importe pagado debe ser mayor a cero.',
                        })
    descripcion = serializers.CharField(max_length=200, min_length=10,
                    error_messages={
                    'required': 'Debe indicar una descripción del gasto.',
                    'blank': 'Debe indicar una descripción del gasto.',
                    'min_length': 'La descripción debe contener al menos 10 caracteres.',
                    'max_length': 'La descripción no puede exceder 200 caracteres.',
                    }                )
    fecha = serializers.DateField( error_messages={
            'required': 'Debe indicar la fecha del gasto.',
            'invalid': 'La fecha del gasto no es válida.',
        })
    ## LO QUITAMOS HASTA QUE SE IMPLEMENTE minIO ## gasto_comprobante = serializers.CharField(max_length=100)

# # Serializer  para la respuesta  del registro de un gasto pagado
class RegistrarGastoPagadoResponseSerializer( serializers.Serializer):
    tipo_gasto= serializers.CharField()         
    descripcion= serializers.CharField()
    importe= serializers.DecimalField(max_digits=12, decimal_places=2)


# # Serializer  para validar la cancelacion del gasto pagado
class CancelarGastoPagadoSerializer(NormalizaTextoMixin,serializers.Serializer):      
    motivo_cancelacion = serializers.CharField(max_length=100, min_length=10,
            error_messages={
            'required': 'Debe indicar motivo de la cancelacion del gasto pagado.',
            'blank': 'Debe indicar una descripción de la cancelacion del gasto.',
            'min_length': 'La descripción debe contener al menos 10 caracteres.',
            'max_length': 'La descripción no puede exceder 100 caracteres.',
            }    )


# # Serializer  para respuesta de la cancelación del gasto pagado
class CancelarGastoPagadoResponseSerializer(serializers.Serializer):      
    gasto= serializers.CharField()         
    motivo_cancelacion= serializers.CharField()
    fecha= serializers.DateField()

# # Serializer  para respuesta de la autorizacion del gasto pagado
class AutorizarGastoPagadoResponseSerializer(serializers.Serializer):      
    descripcion= serializers.CharField()             
    fecha= serializers.DateField()    

# # Serializer  para validar el registro de un comite y el integrante administrador
class RegistrarComiteSerializer(NormalizaTextoMixin, serializers.Serializer):   
    nombre = serializers.CharField(max_length=50)   
    descripcion= serializers.CharField(max_length=100)

# # Serializer  para validar la respuesta al registro de un comite y el integrante administrador
class RegistrarComiteResponseSerializer(serializers.Serializer):   
    id  = serializers.IntegerField()  
    nombre= serializers.CharField()    

# # Serializer  para validar la transferencia de la administracion del condominio
class TransferirAdministracionSerializer( NormalizaTextoMixin, serializers.Serializer):
    administrador_nuevo = serializers.PrimaryKeyRelatedField( queryset=Usuario.objects.all() )
    comentario = serializers.CharField( max_length=200, min_length=10, error_messages={                
                'min_length': 'La descripción debe contener al menos 10 caracteres.',                
            } )

# # Serializer  para validar la respuesta de la transferencia de la administracion del condominio
class TransferirAdministracionResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    administrador_anterior = serializers.CharField()
    administrador_nuevo = serializers.CharField()
    fecha_transferencia = serializers.DateField()    

class IntegranteComiteSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    rol_id = serializers.IntegerField()

# # Serializer  para validar la modificación de integrantes en el comité
class ModificarIntegrantesComiteSerializer( NormalizaTextoMixin, serializers.Serializer):
    comite = serializers.PrimaryKeyRelatedField(queryset=Comite.objects.all())
    miembros_quitar = IntegranteComiteSerializer(
        many=True,
        required=False,
        default=list
    )
    miembros_agregar = IntegranteComiteSerializer(
        many=True,
        required=False,
        default=list
    )     

# # Serializer  para validar la modificación de integrantes en el comité
class ModificarIntegrantesComiteResponseSerializer( NormalizaTextoMixin, serializers.Serializer):
    nombre = serializers.CharField()
    mensaje = serializers.CharField()
   

# # Serializer  para validar la reinicio de password
class ReiniciarPaswordSerializer( NormalizaTextoMixin, serializers.Serializer):
    email_whatsapp = serializers.CharField()


# # Serializer  para validar la reinicio de password
class ReiniciarPaswordResponseSerializer(  serializers.Serializer):
    token = serializers.CharField()
   