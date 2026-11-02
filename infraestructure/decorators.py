# infrastructure/decorators.py

import re
from functools import wraps

from django.db import IntegrityError, transaction

from domain.exceptions import RecursoDuplicadoError


# Mapeo: nombre real en BD → nombre "amigable" para la API
# Ej: "condominio_condominio_nombre_key" → "nombre"
PATRONES_UNIQUE = {
    "condominio_condominio_direccion_key": "direccion",
    "condominio_condominio_nombre_key": "nombre",
    "condominio_condominio_nombre_corto_key": "nombre_corto",
    "condominio_usuario_email_whatsapp_key": "email_whatsapp",    
    "unique_direccion_propiedad_por_condominio":"condominio_direccion",
    "unique_cuota_activa_por_condominio_y_tipo":"cuota_activa_condominio",
    "unique_proveedor_celular_por_condominio":"celular_proveedor_condominio",
    "unique_proveedor_correo_por_condominio":"correo_proveedor_condominio",
    "unique_clave_por_condominio_y_subtipo_gasto":"subtipo_gasto_condominio",
    "unique_clave_por_condominio_y_tipo_gasto":"tipo_gasto_condominio",


    
    # agrega aquí todos los unique que tengas
}



def manejar_unique_violation(func):
    """
    Decorador para métodos `execute` de casos de uso.

    - Envuelve en transaction.atomic.
    - Captura IntegrityError y lo traduce a RecursoDuplicadoError
      con el nombre del campo que violó la unicidad.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                return func(*args, **kwargs)
        except IntegrityError as e:
            mensaje = str(e)

            # Buscamos el nombre del constraint en el mensaje de Postgres
            campo = next(
                (v for k, v in PATRONES_UNIQUE.items() if k in mensaje),
                None,
            )

            if campo:
                # Intentamos extraer el valor duplicado del mensaje
                match = re.search(r"\(([^)]+)\)=\(([^)]+)\)", mensaje)
                valor = match.group(2) if match else None

                raise RecursoDuplicadoError(campo=campo, valor=valor)

            # Si no supimos identificar el campo, relanzamos tal cual
            raise

    return wrapper