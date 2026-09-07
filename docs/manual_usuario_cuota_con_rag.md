# Manual de Usuario y RAG - Módulo Cuotas

## Preguntas Frecuentes

### ¿Cómo se define una nueva cuota?
**Solo el Administrador** puede definir cuotas.

1. Inicia sesión como Administrador
2. Ve a la sección "Cuotas" → "Definir Cuota"
3. Completa los datos requeridos:
   - **Tipo:** Ordinaria (pago regular) o Extraordinaria (gasto especial)
   - **Nombre:** Descripción de la cuota
   - **Importe:** Monto a pagar (solo para cuotas ordinarias)
   - **Vigencia:** Solo Fecha de inicio
4. Haz clic en "Guardar", la cuota quedara Activa
5. La cuota quedará disponible para cobrar

### ¿Cómo se registra un pago?
**El Administrador o Conserje** pueden registrar pagos.

1. Recibe el pago del propietario en **sobre cerrado**
2. Firma el sobre como constancia de recepción
3. En la aplicación, ve a "Cobros" → "Registrar Pago"
4. Selecciona:
   - **Propiedad:** Quién paga
   - **Cuota:** Cuál cuota está pagando
   - **Importe:** El monto recibido
   - **Comprobante:** Descripción del comprobante (ej. "Sobre #123")
5. Opcionalmente, adjunta una foto o PDF del comprobante
6. Haz clic en "Guardar"
7. **Importante:** El importe puede ser mayor, menor o igual el monto definido para la cuota

### ¿Qué hace el conserje con el pago?
1. Recibe el pago del propietario
2. Firma el sobre cerrado
3. Registra el pago en la aplicación
4. Entrega el sobre al Administrador
5. Registra en la aplicación que entregó el sobre

### ¿Cómo valida el administrador los pagos?
1. El Administrador recibe los sobres de los Conserjes
2. Abre cada sobre y verifica el contenido
3. En la aplicación, busca el cobro pendiente
4. Haz clic en "Validar Pago"
5. El sistema registra automáticamente quién validó y cuándo
6. El pago queda confirmado

### ¿Puede el conserje validar un pago?
**No.** Solo el Administrador puede validar pagos. El conserje solo puede recibirlos y registrarlos.

### ¿Puedo pagar una cuota en parcialidades?
**Si.** Se pueden realizar pagos menores al importe de la cuota, lo que genera un saldo pendiente. También se pueden realizar pagos mayores, lo que genera un saldo a favor.

### ¿Qué pasa si el importe que pago no coincide?
El sistema registrara un saldo a favor o un saldo pendiente según corresponda pago mayor o menor respectivamente.

### ¿Qué pasa si pago después de la fecha de vigencia?
No importa la fecha en que se pague, esta versión aun no controla la fecha en que se paga.

### ¿Cómo consulto mis cuotas pagadas y pendientes?
**Como Propietario:**
1. Inicia sesión
2. Ve a "Mi Estado de Cuenta"
3. Verás listado de cuotas y su estado:
   - ✅ **Pagado:** Cuota pagada y validada
   - ⏳ **Pendiente:** Cuota aún no pagada

**Como Administrador:**
1. Inicia sesión
2. Ve a "Reportes" → "Estado General"
3. Verás todas las propiedades y sus adeudos

### ¿Puedo eliminar una cuota?
**No.** Las cuotas no se eliminan. Pero el Administrador puede **desactivarlas** para que no puedan cobrarse.

### ¿Qué documentos debo presentar para pagar?
Actualmente, solo necesitas entregar el **efectivo en sobre cerrado**. El sistema te permite:
- Describir el comprobante (ej. "Sobre #123")
- Adjuntar opcionalmente una foto del comprobante (PDF o JPG)

### ¿Qué diferencia hay entre cuota ordinaria y extraordinaria?
- **Ordinaria:** Pago regular establecido (ej. mantenimiento mensual)
- **Extraordinaria:** Pago especial para gastos no previstos (ej. reparaciones mayores)

## Glosario

| Término | Significado |
|---------|-------------|
| **Cuota** | Pago establecido por el condominio |
| **Cuota Ordinaria** | Pago regular (ej. mantenimiento) |
| **Cuota Extraordinaria** | Pago especial para gastos no previstos |
| **Sobre Cerrado** | Método actual de recepción de pagos |
| **Recepción** | Momento en que se recibe el pago |
| **Validación** | Momento en que el administrador confirma el pago |
| **Pago Completo** | Pago del importe total de la cuota |
| **Pago Parcial** | Pago de solo una parte de la cuota (no permitido) |