# Reglas de Negocio - Módulo Comite

## 1. Propósito

Este documento establece las reglas de negocio que definen el funcionamiento de la aplicación para la administración de condominios en lo referente a la definición y funcionamiento de los comités, participantes, asambleas, actas y convocatorias como documentos que se elaboran externamente y se cargan a la aplicación.

La funcionalidad actual esta al margen de los lineamientos legales que se indican en la Prosoc (Procuraduria Social) y de la Ley de Propiedad en Condominio.

Tampoco incluye votación automática mediante la aplicación permanece la votación manual a mano alzada.

El documento servirá como referencia para:
- Entender y seguir el proceso para la definición e integración de comités.
- Entender y seguir el proceso para la definición de convocatorias para asamblea.
- Entender y seguir el proceso para la definición actas para asamblea.
- Entender y seguir el proceso manual para la votación y conclusiones de las asambleas.
- Proporcionar información al asistente virtual basado en RAG para el area de Comité

## 2. Actores y Roles

### 2.1 Administrador
Persona responsable de la administración del condominio mediante la aplicación y que dentro del comité tendrá el rol de presidente

**Responsabilidades del administrador en los Comités
- Propone los integrantes del comité: Secretario o Comité de Vigilancia y en caso de ser aprobados los registra.
- Propone fechas para la celebración de asamblea.
- Elabora externamente la convocatoria para la celebración de asambleas ordinaria o extraordinaria, con la fecha ganadora e incluye la orden del dia que se evaluará. Guarda la Convocatoria en formato PDF en la aplicación para consultas futuras.
- Coordina la asamblea desahogando los puntos del orden del dia que se indico en la convocatoria.
- Somete a votación los puntos del orden del día que lo requieran, coordina la cuantificación manual de los votos y determina el resultado de acuerdo con las reglas de la asamblea.
- Elabora externamente el acta de la asamblea celebrada en términos de lo acordado en la asamblea. Guarda el Acta de Asamblea en formato PDF en la aplicación para consultas futuras.
- Transfiere el cargo de administración del condominio. La transferencia sera a un propietario activo del condominio este proceso inactiva el comité anterior con sus integrantes.

### 2.2 Propietarios
Persona dueñas de las propiedades que forman el condominio que dentro de los comités y asambleas que pueden tener roles activos o pasivos en estos órganos internos de los condominios.
Pueden arrendar su propiedad a un Inquilino y otorgar carta poder a éstos.

**Responsabilidades de los Propietarios en los Comités:**
- Atiende la asignación para ocupar un rol dentro de la definición de los comités en caso de ser propuesto
- Atiende las convocatorias de asamblea
- Asiste a las asambleas y emite su voto cuando el punto de la orden del día lo requiera.
- Emite los comentarios y preguntas que corresponda en cada caso.
- Otorga carta poder a otro propietario para que asista en su representación y voto a la asamblea.
- Otorga carta poder a su inquilino para que asista en su representación y voto a la asamblea.

### 2.3 Inquilinos
Persona que renta una propiedad del condominio.

**Responsabilidades de los Inquilinos en los Comités:**
- Pueden asistir a las asambleas para escuchar y comentar. Sin que sus comentarios se tomen en cuenta y tampoco pueden votar
- Pueden recibir carta poder del Propietario que les renta y acudir a la asamblea y si pueden proponer y votar en representación del propietario que le otorgo la carta poder.

## 3. Reglas de Negocio

### 3.1 Definición de tablas

#### RN-CMT-001 — Comité
Cada condominio tendrá un Comité que se integrará por algunos de los propietarios del condominio y que tendrán vigencia por un plazo determinado, el administrador del condominio sera el presidente del comité. El secretario y el órgano de vigilancia pueden ser algunos otros propietarios.
Los inquilinos no podrán ser parte del comité.

Tabla:Comite

- **Nombre:** Nombre que identifica el comite
- **Descripcion:** Descripcion adicional en la creación del comité 
- **Activo:** Indica si el comite está vigente en la sesión actual. Por default sera activo
- 
#### RN-CMT-002 — Integrantes del Comité
El comité estará integrado de forma obligatoria por el administrador; de forma opcional por uno, tres o cinco propietarios que integran el comité de vigilancia y también de forma opcional de un secretario.
Un miembro del comité solo podrá tener un rol activo en el comité
Los roles asignados al usuario dentro del condominio (UsuarioRol) son independientes de los roles que desempeña como integrante de un comité (ComiteIntegrante).
Registrar, modificar o inactivar la participación de un usuario en un comité no modifica sus roles dentro del condominio.

Tabla:ComiteIntegrante

- **Comité :** Comité del que forman parte
- **Propietario:** Propietario usuario perteneciente al condominio
- **Rol:** Indicación del rol o función del miembro del comité. Solo podrán tener los roles definidos a nivel sistema.
- **Activo:** Indica si el ese miembro del comité esta activo o no. Por default sera activo

#### RN-CMT-003 — Convocatoria 

El Administrador propondrá algunas fechas para celebrar una asamblea ya sea ordinaria o extraordinaria. 
Una vez acordada la fecha con los propietarios el administrador elaborará externamente el documento con la convocatoria para enviarsela a los propietarios e inquilinos.
El documento se cargará a la aplicación para su consulta histórica.

Tabla: Convocatoria

- **Documento:** Nombre del archivo de la convocatoria cargado en la aplicación.
- **Nombre:** Nombre que identifica la convocatoria
- **Descripcion:** Descripción adicional que identifica la convocatoria
- **Fecha:** Fecha a celebrar motivo de la convocatoria, debe ser mayor a la fecha del sistema.
- **Estado de la Convocatoria:** Estado que tiene una convocatoria, pueden ser CONVOCADA, CELEBRADA o CANCELADA.

#### RN-CMT-004 — Carta Poder
La carta poder es un documento que se administra manualmente durante la asamblea. La validez de la carta poder, la persona que representa al propietario y los efectos de dicha representación serán determinados manualmente durante la asamblea.

#### RN-CMT-005 — Inquilinos
La creación o definición del inquilino se administra manualmente.
La presencia del inquilino sin carta poder se controla manualmente en las asambleas. El inquilino puede asistir a la asamblea para escuchar y opinar, pero su participación no se considera para efectos de votación.
Cuando el inquilino presenta una carta poder del propietario que le renta la propiedad, participa en representación de dicho propietario y los efectos de su participación corresponden al propietario representado.


#### RN-CMT-006 — Votación
Cada asamblea podrá tener uno o mas puntos del orden del dia que se someterán a votación por parte de los propietarios del condominio y que fueron previamente convocados.
El voto se emitirá a mano alzada y en ese momento se determinará si el punto se aprueba o se rechaza.
La cuantificación de los votos se realizará manualmente durante la asamblea y la aplicación no registrará los votos individuales ni su resultado.


#### RN-CMT-007 — Acta
El administrador elaborará externamente el acta de la asamblea y la cargará en la aplicación para su consulta histórica. El documento será  cargado en formato PDF.

Tabla:ActaAsamblea.

- **Comite:** Es la referencia al comité vigente que realiza la asamblea.
- **Convocatoria:** Es la convocatoria de que dio lugar a la asamblea.
- **Documento:** Nombre del documento formato PDF para la Acta de asamblea del condominio

#### RN-CMT-008 — Transferencia Administración 
El cambio de administración requiere que el anterior Administrador del condominio transfiera el rol de Administrador al propietario que sera el nuevo administrador. Este proceso inactiva el rol del Administrador actual y agrega el rol de Administrador al nuevo.
El nuevo administrador debe ser un Propietario activo del condominio.
El administrador anterior conserva sus demás roles activos que correspondan y únicamente se inactiva su rol ADMINISTRADOR.
Solo el administrador activo del condominio puede ejecutar la transferencia de administración.
El propietario que recibe la administración conserva su rol de PROPIETARIO activo y adquiere el rol de ADMINISTRADOR
Además de la transferencia del rol de administrador, se debe inactivar el comite anterior y todos sus integrantes.
El nuevo administrador adquiere todas las responsabilidades y atribuciones como administrador como por ejemplo autorizar pagos, validar cobros de cuotas, emitir, integrar el nuevo comité, incluso emitir convocatorias de asamblea aunque no estén definidos los miembros del comité pues el único obligatorio es el Administrador del condominio.
La transferencia de administración debe registrar la fecha en que se realiza

Tabla:TransferenciaAdministracion.

- **Administrador Anterior:** Identifica al administrador anterior del condominio
- **Administrador Nuevo:** Identifica al administrador nuevo del condominio
- **Comité inactivado:** Identifica el comité anterior que se inactiva
- **Comentario:** Descripción del cambio de administración
- **Fecha:** Señala la fecha en que se hizo la transferencia de la administración.

### 3.3 Consultas y Reportes

#### RN-CMT-001 — Convocatorias
El administrador y los propietarios podrán consultar todas las convocatorias en formato PDF, contando con criterios de búsqueda por fecha


#### RN-CMT-002 — Actas
El administrador y los propietarios podrán consultar todas las actas en formato PDF, contando con criterios de búsqueda por fecha

## 4. Criterios de Aceptación

El módulo Comité cumple con las reglas de negocio cuando:

- ✅ El administrador pueda integrar, registrar y cambiar los integrantes del comité.
- ✅ El administrador pueda cargar las convocatorias para las asambleas del condominio en formato PDF.
- ✅ El administrador y los propietarios puedan buscar por fecha y descargar las convocatorias del condominio en formato PDF, mediante criterios de búsqueda por fecha.PDF.
- ✅ El administrador pueda cargar las actas de las asambleas del condominio en formato PDF.  
- ✅ El administrador y los propietarios puedan buscar y descargar las actas de asamblea del condominio en formato PDF, mediante criterios de búsqueda por fecha. 
- ✅ El administrador actual transfiera el rol de Administrador a otro Propietario activo del condominio. 
- ✅ El proceso de transferencia al nuevo Administrador inactive el comité anterior con todos sus integrantes.
- ✅ El nuevo administrador pueda definir un comité y sus integrantes. 
- ✅ El administrador nuevo tenga todos los privilegios de administrador. 
