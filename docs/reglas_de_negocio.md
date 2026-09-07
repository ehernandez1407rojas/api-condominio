# Reglas de Negocio Para la Aplicación Administración de Condominios

## 1. Propósito del documento

Este documento establece las reglas de negocio que definen el funcionamiento de la aplicación para la administración de condominios.

Las reglas describen el comportamiento esperado del negocio independientemente de la tecnología utilizada para implementar la aplicación.

El documento servirá como referencia para:

* Definir y desarrollar las funciones de la aplicación.
* Validar el comportamiento esperado de cada función.
* Elaborar casos de prueba.
* Facilitar el desarrollo de aplicaciones cliente, incluyendo Flutter.
* Proporcionar información al asistente virtual basado en RAG.
* Mantener una referencia común entre las personas que participan en el proyecto.

---

# 2. Actores del sistema

## 2.1 Administrador

Persona responsable de la administración del condominio mediante la aplicación.

El administrador puede realizar las operaciones que correspondan a sus facultades administrativas.

## 2.2 Propietario

Persona propietaria de una unidad dentro del condominio.

El propietario puede consultar y realizar las operaciones que correspondan a sus facultades dentro del condominio.

## 2.3 Conserje

Persona encargada de realizar funciones operativas dentro del condominio.

El conserje puede realizar únicamente las operaciones que correspondan a sus facultades.

---

# 3. Conceptos generales

## 3.1 Condominio

Conjunto habitacional que es administrado mediante la aplicación.

## 3.2 Usuario

Persona que tiene acceso a la aplicación y que desempeña un determinado rol dentro de un condominio.

## 3.3 Rol

Conjunto de facultades que determinan las operaciones que un usuario puede realizar dentro de la aplicación.

Los roles definidos actualmente son:

* ADMINISTRADOR
* PROPIETARIO
* CONSERJE

---

# 4. Área: Registro

## 4.1 Objetivo

Establecer las reglas que permiten registrar un condominio y crear al usuario administrador responsable de su administración inicial.

El registro constituye el punto de inicio para que un condominio pueda utilizar la aplicación.

---

## 4.2 Reglas de negocio

### RN-REG-001 — Registro del condominio

Todo condominio debe ser registrado antes de utilizar las funciones de administración disponibles en la aplicación.

### RN-REG-002 — Identificación del condominio

Cada condominio debe contar con la información necesaria para identificarlo dentro de la aplicación.

La información que permita identificar al condominio deberá ser única cuando así lo determine el negocio.

### RN-REG-003 — Administrador del condominio

Todo condominio debe contar con al menos un usuario con el rol de ADMINISTRADOR para realizar las funciones administrativas correspondientes.

### RN-REG-004 — Administrador inicial

Durante el registro inicial del condominio debe establecerse el usuario que será responsable de su administración inicial.

### RN-REG-005 — Asociación del administrador

El usuario administrador registrado inicialmente debe quedar asociado al condominio que se está registrando.

### RN-REG-006 — Rol del administrador

El usuario responsable de la administración inicial debe tener asignado el rol ADMINISTRADOR.

### RN-REG-007 — Información obligatoria

El registro del condominio debe contener toda la información que el negocio haya definido como obligatoria.

Si falta información obligatoria, el registro no puede completarse.

### RN-REG-008 — Información del administrador

Para registrar al administrador deben proporcionarse los datos necesarios para identificarlo y permitir su acceso a la aplicación.

### RN-REG-009 — Identificación única del usuario

Los datos definidos por el negocio como identificadores únicos de un usuario no pueden pertenecer simultáneamente a más de un usuario.

### RN-REG-010 — Integridad del registro

El registro de un condominio y la creación de su administrador deben considerarse una misma operación de negocio.

El registro no debe considerarse exitoso si no es posible completar todos los elementos necesarios para establecer correctamente esta relación.

### RN-REG-011 — Registro exitoso

El registro de un condominio se considera exitoso cuando:

1. El condominio ha sido creado.
2. El usuario administrador ha sido creado o identificado correctamente.
3. El administrador ha quedado asociado al condominio.
4. El administrador tiene asignado el rol ADMINISTRADOR.

### RN-REG-012 — Prevención de duplicados

La aplicación debe impedir la creación de registros duplicados cuando la información proporcionada corresponda a una entidad que, de acuerdo con las reglas del negocio, debe ser única.

---

# 5. Funciones del área de Registro

## 5.1 Registrar condominio

### Actor

Persona que realiza el registro inicial del condominio.

### Objetivo

Crear un condominio y establecer al usuario responsable de su administración inicial.

### Información requerida

La información definida como obligatoria para:

* Identificar al condominio.
* Identificar al administrador.
* Permitir el acceso del administrador a la aplicación.

### Resultado exitoso

El condominio queda registrado y cuenta con un usuario con el rol ADMINISTRADOR asociado a él.

### Resultado no exitoso

El condominio no se considera registrado cuando alguna de las condiciones necesarias para completar el registro no puede cumplirse.

---

## 5.2 Registrar propietario

### Actor

ADMINISTRADOR.

### Objetivo

Incorporar un propietario al condominio.

### Resultado esperado

El propietario queda registrado y asociado al condominio correspondiente.

Las reglas específicas de la relación entre propietarios, unidades y condominio se definirán en las áreas de negocio correspondientes.

---

## 5.3 Registrar conserje

### Actor

ADMINISTRADOR.

### Objetivo

Incorporar un conserje al condominio.

### Resultado esperado

El conserje queda registrado y asociado al condominio correspondiente.

Las reglas específicas relacionadas con las funciones y facultades del conserje se definirán en el área correspondiente.

---

# 6. Reglas de autorización

### RN-REG-AUT-001 — Facultades administrativas

Las operaciones que requieran facultades administrativas solamente pueden ser realizadas por usuarios autorizados para ello.

### RN-REG-AUT-002 — Facultades según el rol

Las operaciones que puede realizar un usuario están determinadas por el rol que tenga asignado.

### RN-REG-AUT-003 — Operaciones no autorizadas

Un usuario no puede realizar una operación para la cual no tenga las facultades correspondientes.

---

# 7. Reglas de integridad

### RN-REG-INT-001 — Asociación válida

Todo usuario asociado a un condominio debe mantener una relación válida con dicho condominio.

### RN-REG-INT-002 — Condominio existente

No puede existir una relación entre un usuario y un condominio que no exista dentro de la aplicación.

### RN-REG-INT-003 — Consistencia del registro

La información generada durante el registro debe mantener consistencia entre el condominio, el usuario administrador y la relación entre ambos.

---

# 8. Escenarios de negocio

## 8.1 Registro exitoso

1. Se proporciona la información requerida del condominio.
2. Se proporciona la información requerida del administrador.
3. La información cumple las reglas establecidas.
4. No existen duplicidades que impidan el registro.
5. Se registra el condominio.
6. Se registra el administrador.
7. El administrador queda asociado al condominio.
8. El administrador recibe el rol ADMINISTRADOR.
9. El registro finaliza exitosamente.

## 8.2 Registro con información incompleta

Si falta información obligatoria, el registro no puede completarse.

## 8.3 Registro con información duplicada

Si la información proporcionada corresponde a una entidad que ya existe y no puede duplicarse, el registro debe rechazarse.

## 8.4 Registro incompleto

Si no es posible completar alguno de los elementos necesarios para establecer correctamente el condominio y su administrador, el registro no debe considerarse exitoso.

## 8.5 Usuario sin facultades

Cuando una operación requiera facultades administrativas, debe rechazarse si el usuario que intenta realizarla no cuenta con dichas facultades.

---

# 9. Criterios de aceptación del área

El área de Registro cumple con las reglas de negocio cuando:

* Es posible registrar un condominio con información válida.
* El condominio queda correctamente identificado.
* El condominio cuenta con un administrador.
* El administrador queda asociado al condominio.
* El administrador tiene el rol ADMINISTRADOR.
* Se impiden registros duplicados cuando corresponda.
* Se rechazan registros que no contienen la información obligatoria.
* Se mantiene la integridad de la relación entre el condominio y sus usuarios.
* Las operaciones administrativas solamente pueden ser realizadas por usuarios con las facultades correspondientes.
