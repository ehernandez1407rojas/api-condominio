
# Reglas de Negocio - Módulo Parámetros de Operación

## 1. Propósito

Este documento establece las reglas de negocio que definen el funcionamiento de la aplicación para la administración de condominios en lo referente a los parámetros de operación que cada condominio puede definir.

La funcionalidad, permite adecuar la operación de la aplicación en algunos aspectos a cada condominio

El documento servirá como referencia para:
- Contar con un entendimiento  y un acuerdo explícito y claro con el usuario sobre que condiciones puedes especificarse para la operación especifica de cada condominio
- Mantener una referencia común entre las personas que participan en el proyecto (desarrolladores, testers, líder de proyecto)
- Definir las funciones, restricciones y reglas de negocio en la sección de Parámetros
- Elaborar casos de prueba
- Proporcionar información al asistente virtual basado en RAG

## 2. Actores y Roles

### 2.1 Administrador
Persona responsable de la administración del condominio mediante la aplicación.

**Responsabilidades en la definición de Parámetros de operación
- Define los parámetros vigentes a la fecha que la aplicación ofrece a cada condominio para su selección y que la operación sea lo mas apegada a cada condominio.


**Responsabilidades en Parametros de operación:**
- Desarrollar las actividades en el condominio por las que están relacionados

## 3. Reglas de Negocio

### 3.1 Definición de tablas

RN-PAR-001
Las definiciones de parámetros son parte del sistema y serán creadas
exclusivamente por los desarrolladores de la aplicación.

RN-PAR-002
Cada parámetro tendrá una clave única dentro del sistema.

RN-PAR-003
Cada parámetro tendrá un tipo de dato y un valor predeterminado.

RN-PAR-004
Los tipos de datos serán definidos por el sistema y no podrán cambiarse
una vez que el parámetro haya sido creado y utilizado.

RN-PAR-005
Si un condominio no tiene un valor específico para un parámetro,
se utilizará el valor predeterminado definido por el sistema.

RN-PAR-006
Los valores particulares de los parámetros podrán ser modificados
exclusivamente por el administrador del condominio.

RN-PAR-007
Cada combinación de condominio y parámetro tendrá un único valor vigente.

RN-PAR-008
Toda modificación de un parámetro deberá conservar un historial que
identifique claramente el parámetro, el condominio, el valor anterior,
el nuevo valor, la fecha y el usuario que realizó el cambio.

RN-PAR-009
Las definiciones de parámetros no podrán eliminarse.

RN-PAR-010
Los parámetros estarán siempre activos; no se manejará estado
activo/inactivo.

RN-PAR-011
Los valores numéricos no tendrán límites genéricos establecidos por
el componente de parámetros. Las restricciones particulares, cuando
existan, serán determinadas por la definición y regla de negocio
correspondiente a cada parámetro.


## 4. Criterios de Aceptación

El módulo Parámetros de Operación cumple con las reglas de negocio cuando:
- ✅ El administrador puede definir los parámetros de operación que mejor se adapten a el condominio 
- ✅ El administrador no pueda borrar un parámetro de operación  
- ✅ En caso de que el administrador no defina un parámetro de operación la aplicación propondrá uno por default
