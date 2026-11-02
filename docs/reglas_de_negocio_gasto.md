# Reglas de Negocio - Módulo Gastos en bienes y servicios

## 1. Propósito

Este documento establece las reglas de negocio que definen el funcionamiento de la aplicación para la administración de condominios en lo referente a los gastos de bienes y servicios que se realizan en el condominio: tipos de gastos, condiciones, registro, calificación de proveedores asi como sus pagos y estados de gastos o egresos.

La funcionalidad actual solo hace pagos en efectivo. Los pagos los podrá hacer el conserje en turno pero mayormente el administrador.

También se debe de contar con configuración a nivel condominio para para habilitar que el Conserje pueda hacer pagos y recibir los bienes y servicios por default el parámetro es no permitir.

El documento servirá como referencia para:
- Contar con un entendimiento  y un acuerdo explícito y claro con el usuario sobre el alcance de la aplicación
- Mantener una referencia común entre las personas que participan en el proyecto (desarrolladores, testers, líder de proyecto)
- Definir las funciones, restricciones y reglas de negocio en la sección de Gastos
- Elaborar casos de prueba
- Proporcionar información al asistente virtual basado en RAG

## 2. Actores y Roles

### 2.1 Administrador
Persona responsable de la administración del condominio mediante la aplicación.

**Responsabilidades en los Gastos de bienes y servicios
- Define los tipos y subtipos de gastos
- Define los proveedores de bienes y servicios
- Modifica en caso de ser necesario los datos de identificación del proveedor
- Recibe y valida los bienes y servicios de los proveedores con la documentación comprobatoria
- Valida los pagos efectuados por los conserjes en caso de permitirlos cuando el parámetro este habilitado
- Califica y en su caso veta a los proveedores de bienes y servicios
- Consulta reportes globales de los gastos y pagos del condominio

### 2.2 Conserje
Persona encargada de realizar funciones operativas dentro del condominio.

**Responsabilidades en los Gastos de bienes y servicios:**
- Solo en caso de tener habilitado el parámetro:
- Recibe, valida los bienes y servicios del proveedor
- Paga a los proveedores
- Recibe la documentación comprobatoria de los bienes y servicios cuando exista 

### 2.3 Proveedor de bienes o servicios
Persona física o moral que brinda los bienes o servicios que requiere el condominio

**Responsabilidades en Gastos:**
- Entregar los bienes y servicios a entera satisfacción del Administrador o Conserje con la documentación comprobatoria

### 2.4 Trabajadores o empleados
Persona física que trabajan de manera habitual para el condominio.
Podrán recibir el beneficio de IMSS, la versión actual no administrará habrá otro tipo de obligación fiscal.

**Responsabilidades en Gastos:**
- Desarrollar las actividades en el condominio por las que están relacionados

## 3. Reglas de Negocio

### 3.1 Definición de tablas

#### RN-GTO-001 — Tipo de gasto
Cada condominio definirá que tipo de gastos  que efectuará, siendo el administrador el responsable de definirlos;
Tabla:TipoGasto
Esta clasificación servirá clasificar el gasto para los reportes de gastos y estado de ingresos y gastos
Una vez usado un tipo de gasto en la clasificación de un gasto no se podra borrar. Si se podrá cambiar la clave y la descripción.
En un condominio no se podrá tener dos tipos de gasto con la misma clave

- **Clave:** Definición de los diferente conceptos o tipos de gastos
- **Descripcion:** Detalle adicional de los diferente conceptos o tipos de gastos
- **Orden:** Indicación de un orden específico

#### RN-GTO-002 — Sub Tipo de gasto
Cada condominio podrá definir un segundo nivel de clasificación de los gastos para análisis mas especifico del tipo de gastos  que efectuará, siendo el administrador el responsable de definirlos, con lo cual se tendra un detalle adicional en el registro de cada gasto, sera opcional;
Tabla:SubTipoGasto
Una vez usado un sub tipo de gasto en la clasificación de un gasto no se podra borrar. Si se podrá cambiar la clave y la descripcion
Esta clasificación servirá para los reportes de gastos y estado de ingresos y gastos
En un condominio no se podrá tener dos subtipos de gasto con la misma clave que pertenezcan al mismo tipo de gasto.

- **Relacion con Tipo de Gasto:** Indicacion de a que tipo de gasto pertenece el subtipo
- **Clave:** Definición del subtipo gasto, ejemplo nombre del empleado
- **Descripcion:** Detalle adicional de los  subtipos de gastos, es opcional este catalogo
- **Orden:** Indicación de un orden específico

#### RN-GTO-003 — Situación del Proveedor
El administrador podrá asignar una calificación al proveedor para futuros pedidos; 
Tabla: SituacionProveedor
- **Clave:** Definición de los diferente estado que puede tener un proveedor Ej: "RECOMENDABLE", "VETADO", "PENDIENTE"
- **Descripcion:** Detalle adicional de los diferentes estado que puede tener un proveedor Ej: "RECOMENDABLE", "VETADO", "PENDIENTE"
- **Orden:** Indicación de un orden específico

#### RN-GTO-004 — Proveedor
Cada condominio podrá definir un catalogo de proveedores para usarlo de forma opcional en la definición del gasto, siendo el administrador el responsable de definirlos;
También se permitirá la actulización de datos de identificación del proveedor como: dirección, celular y correo, solo por parte del administrador.
El administrador podrá actualizar la situación del proveedor.
Tabla:Proveedor.
No se podrá borrar si ya se utilizo en la definición de un gasto
Si podrá modificarse todos los datos de identificacion.
- **Nombre:** Nombre del proveedor del bien o servicio
- **Direccion:** Direccion del proveedor del bien o servicio
- **Celular:** 
- **Correo:** Correo electronico
- **Situacion:** Ultima calificación que le asiga el administrador

#### RN-GTO-005 — Comentarios al Proveedor
El administrador podrán agregar un comentario relativo al comportamiento del proveedor respecto del bien o servicio otorgado.
Se podrán agregar varios comentarios en cada proveedor una vez guardado no se podrá cambiar.
Tabla:ProveedorComentario
- **Comentario:** Comentario respecto del bien o servicio recibido del proveedor, tiempo, calidad, lo agrega el administrador

#### RN-GTO-006 — Gasto Pagado
Aquí se registran todos los pagos efectuados por gastos del condominio. El registro lo realiza el administrador, salvo que el parámetro del condominio permita al conserje registrar y pagar gastos.
Cada registro representa un pago efectivamente realizado por el condominio para adquirir un bien o servicio.
Tabla:GastoPagado
- **Tipo de Gasto:** Todos los gastos deben tener esta clasificación
- **Subtipo de Gasto:** Este detalle adicional es opcional se da mas detalle de a quien o a que corresponde el gasto
- **Proveedor:** Esta información también es opcional, depende si el tipo de gasto se hizo a un proveedor
- **Importe Pagado:** Importe efectivamente pagado por el condominio en este registro. Debe ser mayor a cero.
- **Descripcion:** También es opcional un detalle adicional del gasto efectuado
- **Fecha:** Fecha del gasto en caso de comprobante el que se indique en dicho comprobante, no puede ser mayor a la fecha del sistema
- **Esta Autorizado:** En un estado del gasto, si el administrador lo hizo queda como verdadero, si lo hace el conserje queda con el default 
- **Quien Autorizo:** Sera el administrador
- **Cuando Autorizo:** Es la fecha de sistema en la que el administrador lo autorizo
- **Esta Cancelado:** Estado cancelado del gasto, solo el administrador lo puede cancelar 
- **Quien Cancelo:** Sera el administrador
- **Cuando Cancelo:** Es la fecha de sistema en la que el administrador lo cancelo
- **Motivo Cancelacion:** Justificacion de porque se cancela para mas detalle


#### RN-GTO-007 — Cancelación de Gasto
De forma excepcional se permitirá cancelar un gasto. Solo lo podrá hacer el administrador, en cualquier momento, y deberá indicar un motivo de la cancelación con una longitud mínima de 10 caracteres.
El gasto cancelado permanecerá disponible para consulta y formará parte del reporte histórico; sin embargo, su importe considerado para los totales financieros será $0.00 y deberá identificarse claramente como cancelado
Un gasto pagado solo se podrá cancelar una vez.

#### RN-GTO-008 — Pago en efectivo
Actualmente todos los gastos registrados en la aplicación se realizan mediante pagos en efectivo.
Cada registro de GastoPagado representa un importe efectivamente pagado.
Un mismo bien o servicio podrá ser pagado mediante varios registros de GastoPagado, permitiendo realizar pagos parciales.
En estos casos podrá repetirse el proveedor, comprobante y/o descripción que identifique el bien o servicio relacionado con el pago.
La aplicación no administrará cuentas por pagar ni saldos pendientes de comprobantes.
El administrador será responsable de verificar y pagar el importe correcto del bien o servicio, conforme al comprobante correspondiente. Cualquier pago superior al importe que corresponda será responsabilidad del administrador.
La aplicación en esta versión no impedirá técnicamente que el administrador registre un importe superior al comprobante; la responsabilidad de verificar el importe correcto corresponde al administrador.

#### RN-GTO-009 — Pago completo y parciales
El importe de cada pago deberá ser mayor a cero.
Se permite registrar uno o varios pagos relacionados con un mismo bien o servicio.
La suma de los pagos podrá representar el pago completo o pagos parciales del bien o servicio.

### 3.3 Consultas y Reportes

#### RN-GTO-010 — Estado de Gastos
Se podrá consultar el estado de gastos por mes y acumulado por el año en curso:


#### RN-GTO-011 — Reporte global del administrador
El administrador puede consultar el estado general cuotas y gastos

#### RN-GTO-012 — Correspondencia Tipo/Subtipo de gasto
Cuando un gasto incluya un subtipo de gasto, éste deberá pertenecer al tipo de gasto seleccionado. El sistema no permitirá registrar un gasto cuya combinación de tipo y subtipo no corresponda.

### RN-GTO-013 — Descripción del Gasto

La descripción del gasto es obligatoria. No podrá estar compuesta únicamente por espacios. Después de eliminar los espacios al inicio y al final, deberá contener al menos 10 caracteres.


## 4. Criterios de Aceptación

El módulo Gastos Pagados cumple con las reglas de negocio cuando:
- ✅ El administrador puede definir los tipos de gastos en los que clasificara el condominio 
- ✅ El administrador no podrá definir dos tipos de gastos con la misma clave en el condominio 
- ✅ El administrador no pueda borrar un tipo ni subtipo de gasto ya usado en un gasto 
- ✅ El administrador no podrá definir dos subtipos de gastos con la misma clave en el mismo tipo de gasto en el condominio  
- ✅ El administrador si pueda modificar la clave y/o descripción de un tipo y subtipo de gasto 
- ✅ El administrador puede modificar el orden de los tipos y subtipos de gasto.
- ✅ El administrador o el conserje si es que este ultimo esta habilitado podrá registrar un gasto 
- ✅ El administrador podrá registrar proveedores. 
- ✅ No se podrá borrar un proveedor si ya se utilizo en un gasto
- ✅ Si podrá cambiar los datos de identificación del proveedor 
- ✅ El administrador podrá calificar a proveedor
- ✅ El sistema no permite registrar un pago con importe menor o igual a cero.
- ✅ Un gasto cancelado permanece en el historial y en los reportes, pero se considera con importe $0.00 para los totales financieros y se identifica como cancelado.
- ✅ El administrador puede registrar pagos parciales del mismo bien o servicio mediante varios registros de GastoPagado.
- ✅ Se debe generar el reporte de gastos por mes y acumulado por el año en curso
- ✅ El sistema no permite registrar un gasto con un subtipo que no pertenezca al tipo de gasto seleccionado
- ✅ Un GastoPagado registrado no puede modificarse; cualquier corrección deberá realizarse mediante cancelación y nuevo registro.
- ✅ Un gasto registrado por el administrador queda autorizado automáticamente. Si no lo tiene que hacer el administrador.
- ✅ Solo el administrador puede cancelar un gasto y debe indicar el motivo con descripción mínima de 10 caracteres
- ✅ El sistema no permite registrar un gasto sin una descripción.
- ✅ Un gasto pagado solo se podrá cancelar una vez.