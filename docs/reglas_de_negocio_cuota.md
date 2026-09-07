# Reglas de Negocio - Módulo Cuotas

## 1. Propósito

Este documento establece las reglas de negocio que definen el funcionamiento de la aplicación para la administración de condominios en lo referente a las cuotas: definición, tipos de cuotas, cobro y estados de adeudos.

La funcionalidad actual solo recibe depósitos en efectivo. La recepción del depósito tendrá una firma de aceptación del receptor y un parámetro a nivel condominio para incluir o no la confirmación del depósito.

El documento servirá como referencia para:
- Contar con un entendimiento completo y un acuerdo explícito con el usuario sobre el alcance de la aplicación
- Mantener una referencia común entre las personas que participan en el proyecto (desarrolladores, testers, líder de proyecto)
- Definir las funciones, restricciones y reglas de negocio en la sección de Cuotas
- Elaborar casos de prueba
- Proporcionar información al asistente virtual basado en RAG

## 2. Actores y Roles

### 2.1 Administrador
Persona responsable de la administración del condominio mediante la aplicación.

**Responsabilidades en Cuotas:**
- Define los tipos de cuotas, montos, vigencia y periodicidad
- Recibe los sobres con las cuotas de los conserjes
- Valida los pagos recibidos
- Consulta reportes globales de la operación del condominio

### 2.2 Propietario
Persona propietaria de una unidad dentro del condominio.

**Responsabilidades en Cuotas:**
- Paga la(s) cuota(s) que le corresponden dentro de los plazos y montos definidos
- Realiza depósitos en efectivo (único método disponible)
- Consulta el estado específico de su propiedad
- Consulta reportes de su propiedad

### 2.3 Conserje
Persona encargada de realizar funciones operativas dentro del condominio.

**Responsabilidades en Cuotas:**
- Recibe el importe de la cuota en sobre cerrado
- Firma el sobre como constancia de recepción
- Registra la recepción del pago en la aplicación
- Entrega los sobres al administrador 

## 3. Reglas de Negocio

### 3.1 Gestión de Cuotas

#### RN-CTA-001 — Tipos de cuota predefinidos
El sistema debe contar con los siguientes tipos de cuota; tabla:TipoCuota
- **ORDINARIA:** Cuota regular del condominio
- **EXTRAORDINARIA:** Cuota especial para gastos no previstos
- **CADA CUANDO ES EXIGIBLE:** al definir el tipo de cuota también se indica cada cuando se exige

#### RN-CTA-002 — Definir cuota
El administrador debe registrar una cuota con la siguiente información; tabla: Cuota
- **Tipo:** ORDINARIA o EXTRAORDINARIA dentro de esta selección también se tiene la indicación de cada cuando se cobra
- **Nombre:** Descriptivo de la cuota (ej. "Mantenimiento 2026")
- **Importe:** Monto de la cuota (obligatorio para las dos ORDINARIA y  EXTRAORDINARIA)
- **Fecha de inicio aplicación:** Inicio de la vigencia puede ser igual, menor o mayor a la fecha del sistema. Después de guardada no se puede cambiar la fecha.
- **Fecha de fin de aplicación:** Se debe indicar cuando termina no importa que tipo de cuota sea. Después de guardada no se puede cambiar la fecha.
- **Activo:** Indica si la cuota está vigente se agrega por default Activa, se puede inactivar en cualquier momento por el administrador

#### RN-CTA-003 — Vigencia única
No pueden existir dos cuotas del mismo tipo y condominio con estado ACTIVO.

#### RN-CTA-004 — Desactivación de cuotas
Las cuotas no se eliminan físicamente. Solo pueden desactivarse para mantener el historial y en ese momento se asigna la fecha fin de vigencia con la fecha del sistema sobre todo cuando se adelanta la cancelación de la cuota, solo puede hacer el administrador. La cancelación se realiza actualizando el campo Activo a False y asignando en la fecha aplica hasta la fecha del sistema en la que se realiza la cancelación. Y en comentario se debe indicar el motivo de la cancelación.

La cancelación de una cuota puede obedecer a que de forma inicial existió un error en su definición , monto, fechas, tipo cuota etc. o por decisión del condominio durante la vigencia de dicha cuota. En virtud de que al guardar la cuota se generan todas las cuotas exigibles de todas las propiedades del condominio entonces el proceso de cancelación de la cuota también cancelara la cuotas exigibles de cada propiedad esto se logra al actualizar el Estado de la Cuota Exigible a CANCELADA = 'C'. Las cuotas exigibles que se cancelaran son todas aquellas que tienen superiores en mes y año a la fecha de sistema que se esta cancelando la cuota y que tengan el Estado en EXIGIBLE = 'E' es decir si hay alguna cuota exigible que se adelantó el pago esa exigibilidad no se cancelara se dejara con el estado de  PAGADA = 'P' de hecho esta regla es general no se cambiara el estado de una cuota exigible que ya este pagada.


### 3.2 Exigibilidad de Cuotas

#### RN-CTA-005 — Recepción de pago
Cuando el administrador definió la cuota y cuando oprime guardarla el sistema general la totalidad de las cuotas exigibles para todas las propiedades de ese condominio; tabla: CuotaExigible :
- **Propiedad:** Propiedad a la que se le exigirirá la cuota
- **Cuota:** Importe exigible de la cuota puede ser ordinaria o extraordinaria
- **Fecha de exigibilidad:** puede ser una fecha única cuando se trata de cuota EXTRAORDINARIA o un conjunto de fechas exigibles cuando es mensual. La fecha de exigibilidad sera el dia uno del mes de que se trate, tanto en el caso de MENSUAL o UNICA.
- **Estado :** Los diferentes estados son: EXIGIBLE = 'E', PAGADA = 'P', CANCELADA = 'C'. Al crear el registro se marca como EXIGIBLE = 'E'. Cuando se cobra se marca como PAGADA = 'P'. Y cuando se cancela la cuota se marca como CANCELADA = 'C'


### 3.3 Cobro de Cuotas

#### RN-CTA-006 — Recepción de cobro
El administrador o conserje puede registrar el cobro de una cuota con los siguientes datos; tabla:CuotaCobrada
- **Propiedad:** Propiedad que realiza el pago
- **Cuota exigible:** Cuota exigible que se está cobrando, puede ser una ordinaria o extraordinaria
- **Importe cobrado:** Siempre será mayor que cero. Puede ser mayor, menor o igual al importe definido para la cuota qeu se está pagando.
- **Quien recibe:** Persona que recibe el pago (administrador o conserje)
- **Fecha de recepción:** Fecha y hora del sistema (automática)
- **Comprobante:** Descripción libre del comprobante (ej. "Sobre #123")
- **Comprobante digital:** Archivo PDF o JPG (opcional). La version actual solo recibe en efectivo por lo que no resulta util este momento.
- **Persona que valida:** Solo puede ser el administrador. Cuando el conserje cobra esta información se queda vacía.
- **Fecha de validación:** Es cuando el administrador la valida. Cuando el administrador cobra la cuota será la misma fecha en la que cobró.
- **Esta validada:** Si la cuota la cobro el conserje se queda como falsa. Es cuando el administrador la valida o cuando el administrador cobra la cuota se marca como verdadero.
- **Saldo:** Cuando es el primer cobro de una cuota exigible, es la diferencia entre el importe de la exigibilidad de la cuota y el importe cobrado. Cuando queda un saldo después del primer cobro; se toma el saldo anterior para hacer la diferencia contra el cobro que se esta haciendo y asi seguirá iterativamente hasta que el saldo sea igual a cero. En caso de que el saldo sea a favor ahi se mantendrá y se aplicara como cobro en la siguiente exigibilidad de la misma cuota.
- A nivel configuración general se podrá cobrar hasta dos meses posteriores a la fecha del sistema.
- **Esta validado:** Cuando cobra el conserje se guarda falso. Se marcara verdadero cuando el administrador lo valida o desde el momento del cobro si el administrador cobra la cuota.

#### RN-CTA-006 — Pago en efectivo
Actualmente solo se aceptan pagos en efectivo. El pago se entrega en sobre.

#### RN-CTA-007 — Firma de recepción
La persona que recibe el pago (administrador o conserje) debe firmar el sobre  como constancia de recepción mas el comentario en el campo Comprobante al registrar el cobro de la cuota.

#### RN-CTA-008 — Entrega del sobre al administrador
Cuando el conserje recibe un pago:
1. Registra la recepción en la aplicación
2. Custodia el sobre al administrador
3. Posteriormente lo entrega al administrador


#### RN-CTA-009 — Validación del administrador
El administrador debe validar los pagos recibidos, confirmando:
- Que el sobre fue recibido físicamente
- Que el importe es correcto contra lo registrado

La validación registra:
- **Quién valida:** El administrador
- **Cuándo valida:** Fecha y hora del sistema (automática)
- **Esta Validado** Se registra en la aplicación cuando lo valida el administrador o desde el momento que lo cobro el administrador 
- **Comentario Validación** Se registra comentario u observación que quiera hacer el administrador. En caso de que la cantidad no sea el importe cobrado que se reportó, la diferencia se solventará y gestionará al margen del sistema

#### RN-CTA-010 — Momentos distintos
La **recepción** y la **validación** son momentos distintos:
- **Recepción:** Cuando el conserje o administrador recibe el pago
- **Validación:** Cuando el administrador confirma el pago

#### RN-CTA-011 — Pago completo, menor o mayor
Si se permiten pagos menor, mayor o  igual al importe de la cuota que se paga. Siempre será un importe mayor a cero.
No se podrá cobrar un mes si hay meses de cuotas anteriores pendientes de cobro total, del mismo tipo de cuota
En caso de que en un mes exista una cuota ORDINARIA y también una EXTRAORDINARIA, primero se cobrará la ORDINARIA.

### 3.3 Consultas y Reportes

#### RN-CTA-012 — Estado de cuenta del propietario
El propietario puede consultar el estado de sus cuotas:
- **Pagadas:** Cuotas que ya han sido pagadas y validadas
- **Saldo Pendiente:** Cuotas pagadas parcialmente
- **Saldo a Favor:** Cuotas pagadas en exceso

#### RN-CTA-013 — Reporte global del administrador
El administrador puede consultar el estado general de cobros del condominio:
- Propiedades con adeudos
- Montos recaudados
- Fechas de pago

#### RN-CTA-014 — Reporte del conserje
El conserje puede consultar solo los pagos que ha recibido.

### 3.4 Reglas de Autorización

| Operación     | ADMINISTRADOR | PROPIETARIO | CONSERJE |
|---------------|---------------|-------------|----------|
| Definir cuota |    ✅        |    ❌        | ❌ |
| Cobrar cuota  |    ✅        |    ❌        | ✅ |
| Validar cobro |    ✅        |    ❌        | ❌ |
| Ver estado de cuenta propio | ✅ | ✅ | ❌ |
| Ver estado de cuenta de otro | ✅ | ❌ | ❌ |
| Ver reporte global | ✅ | ❌ | ❌ |
| Ver reporte de pagos recibidos | ✅ | ❌ | ✅ |


## 4. Criterios de Aceptación

El módulo Cuotas cumple con las reglas de negocio cuando:
- ✅ El administrador puede definir cuotas con todos sus datos pueden ser de tipo ORDINARIA o EXTRAORDINARIA 
- ✅ Cuando el administrador define una cuota el sistema general las cuotas exigibles de todas las propiedades
- ✅ No se permite mas de una cuota de cualquier tipo ORDINARIA o EXTRAORDINARIA  por condominio y que este activa
- ✅ El administrador y conserje pueden registrar cobros
- ✅ Solo el administrador puede validar cobros
- ✅ Solo el administrador puede cancelar una cuota
- ✅ El importe cobrado puede ser mayor, menor o igual al importe de la cuota, el importe siempre será mayor a cero
- ✅ Si se permiten pagos parciales o en exceso
- ✅ La fecha de recepción es automática y no editable
- ✅ La fecha de validación es automática y no editable 
- ✅ El propietario puede ver su estado de cuenta
- ✅ El administrador puede ver el reporte global del condominio
- ✅ El administrador puede ver todos los pagos que se han recibido 