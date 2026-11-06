# Donación · Seguimiento de desarrollo e incorporación técnica

Fecha de seguimiento: **6 de noviembre de 2026**. Fase: **DESARROLLAR completada**. Estado editorial: **borrador para revisión del conjunto**.

Rama de trabajo: `feat/cf-donacion-pro-001`. Solicitud de cambios: [PR #15](https://github.com/iskayApp/como-funciona/pull/15).

## Secuencia y alcance de esta incorporación

Las 40 fichas se desarrollaron y presentaron completas en sus tres roles y 16 etapas antes de continuar el código, conforme a la indicación del usuario. La entrega editorial tiene un documento maestro por ficha, un índice conjunto y un PDF completo de revisión. Después de esa presentación se autorizó el traslado al repositorio.

Esta incorporación completa el espejo técnico del conjunto presentado. Conserva los cuerpos públicos, los códigos y la trazabilidad; prepara las portadas de categoría, rol y etapa con los componentes comunes. La autorización para trabajar el código no se registra como una aprobación editorial o una publicación de las fichas.

## Avance por rol

| Rol | Etapas | Fichas desarrolladas | Pendientes de desarrollar | Aprobadas | Publicadas | Registros CL principales |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Promotores | 7 | 18 | 0 | 0 | 0 | 71 |
| Donantes | 5 | 14 | 0 | 0 | 0 | 42 |
| Colaboradores | 4 | 8 | 0 | 0 | 0 | 23 |
| **Total** | **16** | **40** | **0** | **0** | **0** | **136** |

Las 39 fichas sustentadas en la clasificación conservan el destino principal único de los 136 registros. CF-DON-DON-004 utiliza fuentes operativas propias, sin crear un registro CL. Los recuentos de registros y de fichas son unidades diferentes.

## Fuente editorial y funcional

La fuente maestra editorial está en **12 como-funciona / 02 Donación**, organizada en Promotores, Donantes y Colaboradores, y dentro de cada rol en sus etapas. Cada archivo canónico conserva el título de su documento maestro mediante `editorial_source`. No se incorporan URLs ni identificadores privados de esos documentos al repositorio público.

- **Fuente general:** `1 Donación.docx`, original restaurado con el reemplazo autorizado por «Sin comisión para el donante» y su párrafo sobre cargos bancarios. Última modificación del archivo consultado: `2026-11-06T11:00:41.160Z`. La versión de la guía no está identificada expresamente.
- **Precampaña:** `Ayuda_iskayapp_Boton_Iniciar_Precampana_Donacion.docx`, versión 1.0 de 10 de agosto de 2026, como fuente operativa separada para CF-DON-PRO-011 y CF-DON-DON-007.
- **Presentación pública del donante:** calendario `1.1 Aprobacion_calendario_Donacion_iskay.xlsm`, registros DON-EDU-02 y DON-INS-02, y `DON-VEN-02 - Producción`, para CF-DON-DON-004. La aprobación de esas fuentes no aprueba automáticamente la ficha.

Se conserva el texto de la entrega editorial, incluidos los siete tramos de comisiones, la comisión mínima, el descuento directo a la tasa, la distinción entre precampaña y campaña, la notificación de transferencia al promotor y la revisión de una posible reversión. La guía funcional no se modifica mediante esta incorporación técnica.

## Estado y trazabilidad en el código

| Campo | Valor del conjunto |
| --- | --- |
| `status` | `draft` |
| `editorial_status` | `pending_review` |
| `published` | `false` |
| `visibility` | `private` |
| `reviewed` | `false` |
| `content_version` | `1` |
| `source_checked_on` | `2026-11-06` |
| `stage_id` / `stage_url` | Etapa propia y ruta reservada de cada ficha |
| `classification_refs` | Registros principales completos, expandidos con tres dígitos |
| `classification_secondary_refs` | Referencias secundarias diferenciadas |
| `prev_code` / `next_code` | Secuencia dentro del mismo rol |
| `prev_url` / `next_url` | Nulos hasta contar con destinos públicos comprobados |

`source_checked_on` acredita el contraste de la fuente; no sustituye la revisión editorial. `visibility` controla la salida del sitio, no la visibilidad de los archivos en GitHub: el repositorio es público.

Las rutas de CF-DON-PRO-001 y CF-DON-PRO-002 se conservan. Las otras 38 se reservan con código y pregunta propios. No hay multimedia, activos de distribución ni asociaciones de marketing añadidas por inferencia.

## Índices y catálogo común

Se preparan **20 índices**: una portada de Donación, tres recorridos por rol y 16 etapas. Reutilizan la navegación, el buscador y la orientación existentes. Donación Colaboradores utiliza cuatro etapas, sin copiar las áreas profesionales de FR.

El registro de categorías declara los tres roles de Donación y conserva `status: preparation`. `_config.yml` mantiene excluido `ideas/donacion`, y las 60 páginas del conjunto conservan los estados de borrador. El catálogo compartido debe tener **139 fichas inventariadas**, de las cuales **99 FR son públicas y buscables**; las 40 Donación tienen `public_searchable: false`.

El control público de mantenimiento refleja **40 fichas desarrolladas en borrador** y mantiene los recuentos de clasificación 71/42/23. Los catálogos JSON son resultados generados, no fuentes duplicadas ni archivos que deban incorporarse al commit.

## Fichas incorporadas

Los enlaces siguientes abren los archivos de revisión del repositorio. No son enlaces de publicación del sitio.

### Promotores

#### 1. Conoce Donación y tu papel como promotor

- **CF-DON-PRO-001** · [¿Quién puede promover una iniciativa en Donación y qué causas puede presentar?](../../ideas/donacion/promotores/01-conoce-donacion-y-tu-papel-como-promotor/cf-don-pro-001-quien-puede-promover-y-que-causas-puede-presentar.md)
- **CF-DON-PRO-002** · [¿Cómo funciona el apoyo de los donantes en esta categoría?](../../ideas/donacion/promotores/01-conoce-donacion-y-tu-papel-como-promotor/cf-don-pro-002-como-funciona-el-apoyo-de-los-donantes-en-esta-categoria.md)
- **CF-DON-PRO-003** · [¿Qué vínculo se establece con el donante y qué riesgos existen?](../../ideas/donacion/promotores/01-conoce-donacion-y-tu-papel-como-promotor/cf-don-pro-003-que-vinculo-se-establece-con-el-donante-y-que-riesgos-existen.md)

#### 2. Organiza el apoyo a tu iniciativa

- **CF-DON-PRO-004** · [¿Necesito colaboradores y qué pueden aportar a mi iniciativa?](../../ideas/donacion/promotores/02-organiza-el-apoyo-a-tu-iniciativa/cf-don-pro-004-necesito-colaboradores-y-que-pueden-aportar-a-mi-iniciativa.md)
- **CF-DON-PRO-005** · [¿Puedo acordar una retribución con un colaborador?](../../ideas/donacion/promotores/02-organiza-el-apoyo-a-tu-iniciativa/cf-don-pro-005-puedo-acordar-una-retribucion-con-un-colaborador.md)

#### 3. Conoce las comisiones y los descuentos

- **CF-DON-PRO-006** · [¿Qué comisión pago como promotor y cuándo se calcula?](../../ideas/donacion/promotores/03-conoce-las-comisiones-y-los-descuentos/cf-don-pro-006-que-comision-pago-como-promotor-y-cuando-se-calcula.md)
- **CF-DON-PRO-007** · [¿Qué descuento obtengo al incorporar colaboradores?](../../ideas/donacion/promotores/03-conoce-las-comisiones-y-los-descuentos/cf-don-pro-007-que-descuento-obtengo-al-incorporar-colaboradores.md)
- **CF-DON-PRO-008** · [¿Donar en mi campaña tiene comisiones o cargos?](../../ideas/donacion/promotores/03-conoce-las-comisiones-y-los-descuentos/cf-don-pro-008-donar-en-mi-campana-tiene-comisiones-o-cargos.md)

#### 4. Prepara y publica tu campaña

- **CF-DON-PRO-009** · [¿Qué debe incluir la presentación de mi campaña?](../../ideas/donacion/promotores/04-prepara-y-publica-tu-campana/cf-don-pro-009-que-debe-incluir-la-presentacion-de-mi-campana.md)
- **CF-DON-PRO-010** · [¿Qué debo indicar sobre el monto y los tiempos de mi iniciativa?](../../ideas/donacion/promotores/04-prepara-y-publica-tu-campana/cf-don-pro-010-que-debo-indicar-sobre-el-monto-y-los-tiempos-de-mi-iniciativa.md)
- **CF-DON-PRO-011** · [¿Cómo funciona la precampaña y cómo se inicia la campaña?](../../ideas/donacion/promotores/04-prepara-y-publica-tu-campana/cf-don-pro-011-como-funciona-la-precampana-y-como-se-inicia-la-campana.md)
- **CF-DON-PRO-012** · [¿Qué compromiso de actualización asumo al publicar mi campaña?](../../ideas/donacion/promotores/04-prepara-y-publica-tu-campana/cf-don-pro-012-que-compromiso-de-actualizacion-asumo-al-publicar-mi-campana.md)

#### 5. Cierre y transferencia de fondos

- **CF-DON-PRO-013** · [¿Qué pasa con lo recaudado al finalizar la campaña?](../../ideas/donacion/promotores/05-cierre-y-transferencia-de-fondos/cf-don-pro-013-que-pasa-con-lo-recaudado-al-finalizar-la-campana.md)
- **CF-DON-PRO-014** · [¿Qué cuenta y certificado bancario necesito para recibir los fondos?](../../ideas/donacion/promotores/05-cierre-y-transferencia-de-fondos/cf-don-pro-014-que-cuenta-y-certificado-bancario-necesito-para-recibir-los-fondos.md)

#### 6. Usa los fondos según lo declarado y comunica avances

- **CF-DON-PRO-015** · [¿Cómo uso los fondos y mantengo informados a los donantes?](../../ideas/donacion/promotores/06-usa-los-fondos-segun-lo-declarado-y-comunica-avances/cf-don-pro-015-como-uso-los-fondos-y-mantengo-informados-a-los-donantes.md)

#### 7. Reclamaciones y posibles reversiones

- **CF-DON-PRO-016** · [¿Qué sucede ante el uso indebido de recursos o un incumplimiento grave?](../../ideas/donacion/promotores/07-reclamaciones-y-posibles-reversiones/cf-don-pro-016-que-sucede-ante-el-uso-indebido-de-recursos-o-un-incumplimiento-grave.md)
- **CF-DON-PRO-017** · [¿Qué situaciones llevan a revisar una posible reversión de fondos?](../../ideas/donacion/promotores/07-reclamaciones-y-posibles-reversiones/cf-don-pro-017-que-situaciones-llevan-a-revisar-una-posible-reversion-de-fondos.md)
- **CF-DON-PRO-018** · [¿Qué ocurre durante la revisión y si se decide revertir los fondos?](../../ideas/donacion/promotores/07-reclamaciones-y-posibles-reversiones/cf-don-pro-018-que-ocurre-durante-la-revision-y-si-se-decide-revertir-los-fondos.md)

### Donantes

#### 1. Comprender qué implica donar

- **CF-DON-DON-001** · [¿Qué significa donar en iskay.app?](../../ideas/donacion/donantes/01-comprender-que-implica-donar/cf-don-don-001-que-significa-donar-en-iskay-app.md)
- **CF-DON-DON-002** · [¿Qué causas puedo apoyar y qué puedo elegir al donar?](../../ideas/donacion/donantes/01-comprender-que-implica-donar/cf-don-don-002-que-causas-puedo-apoyar-y-que-puedo-elegir-al-donar.md)
- **CF-DON-DON-003** · [¿Qué vínculo tengo con el promotor y qué riesgos debo conocer?](../../ideas/donacion/donantes/01-comprender-que-implica-donar/cf-don-don-003-que-vinculo-tengo-con-el-promotor-y-que-riesgos-debo-conocer.md)
- **CF-DON-DON-004** · [¿Cómo se presenta públicamente mi apoyo como donante?](../../ideas/donacion/donantes/01-comprender-que-implica-donar/cf-don-don-004-como-se-presenta-publicamente-mi-apoyo-como-donante.md)

#### 2. Conocer la iniciativa y a su equipo

- **CF-DON-DON-005** · [¿Qué información puedo revisar de una iniciativa?](../../ideas/donacion/donantes/02-conocer-la-iniciativa-y-a-su-equipo/cf-don-don-005-que-informacion-puedo-revisar-de-una-iniciativa.md)
- **CF-DON-DON-006** · [¿Quién impulsa la iniciativa y qué hacen sus colaboradores?](../../ideas/donacion/donantes/02-conocer-la-iniciativa-y-a-su-equipo/cf-don-don-006-quien-impulsa-la-iniciativa-y-que-hacen-sus-colaboradores.md)
- **CF-DON-DON-007** · [¿Cuánto dura la campaña y qué es la precampaña?](../../ideas/donacion/donantes/02-conocer-la-iniciativa-y-a-su-equipo/cf-don-don-007-cuanto-dura-la-campana-y-que-es-la-precampana.md)

#### 3. Entender los costes y la transferencia de fondos

- **CF-DON-DON-008** · [¿Qué costes puede tener mi donación?](../../ideas/donacion/donantes/03-entender-los-costes-y-la-transferencia-de-fondos/cf-don-don-008-que-costes-puede-tener-mi-donacion.md)
- **CF-DON-DON-009** · [¿Qué comisión paga el promotor y cómo influyen los colaboradores?](../../ideas/donacion/donantes/03-entender-los-costes-y-la-transferencia-de-fondos/cf-don-don-009-que-comision-paga-el-promotor-y-como-influyen-los-colaboradores.md)
- **CF-DON-DON-010** · [¿Cómo se entrega al promotor lo recaudado?](../../ideas/donacion/donantes/03-entender-los-costes-y-la-transferencia-de-fondos/cf-don-don-010-como-se-entrega-al-promotor-lo-recaudado.md)

#### 4. Seguir la iniciativa y pedir información

- **CF-DON-DON-011** · [¿Cómo puedo informarme sobre los avances y el uso de los fondos?](../../ideas/donacion/donantes/04-seguir-la-iniciativa-y-pedir-informacion/cf-don-don-011-como-puedo-informarme-sobre-los-avances-y-el-uso-de-los-fondos.md)

#### 5. Reclamar y conocer las situaciones de reversión

- **CF-DON-DON-012** · [¿Qué puedo hacer ante un uso indebido de fondos o un incumplimiento grave?](../../ideas/donacion/donantes/05-reclamar-y-conocer-las-situaciones-de-reversion/cf-don-don-012-que-puedo-hacer-ante-un-uso-indebido-de-fondos-o-un-incumplimiento-grave.md)
- **CF-DON-DON-013** · [¿En qué situaciones se revisa la reversión de fondos?](../../ideas/donacion/donantes/05-reclamar-y-conocer-las-situaciones-de-reversion/cf-don-don-013-en-que-situaciones-se-revisa-la-reversion-de-fondos.md)
- **CF-DON-DON-014** · [¿Cómo se comunica una reversión y dónde se devuelven los fondos?](../../ideas/donacion/donantes/05-reclamar-y-conocer-las-situaciones-de-reversion/cf-don-don-014-como-se-comunica-una-reversion-y-donde-se-devuelven-los-fondos.md)

### Colaboradores

#### 1. Tu papel como colaborador

- **CF-DON-COL-001** · [¿Qué significa ser colaborador en una iniciativa de Donación?](../../ideas/donacion/colaboradores/01-tu-papel-como-colaborador/cf-don-col-001-que-significa-ser-colaborador-en-una-iniciativa-de-donacion.md)
- **CF-DON-COL-002** · [¿Cómo elijo con qué iniciativas colaborar?](../../ideas/donacion/colaboradores/01-tu-papel-como-colaborador/cf-don-col-002-como-elijo-con-que-iniciativas-colaborar.md)

#### 2. Formas de aportar y compartir documentos

- **CF-DON-COL-003** · [¿De qué formas puedo apoyar una iniciativa?](../../ideas/donacion/colaboradores/02-formas-de-aportar-y-compartir-documentos/cf-don-col-003-de-que-formas-puedo-apoyar-una-iniciativa.md)
- **CF-DON-COL-004** · [¿Puedo publicar documentos como colaborador?](../../ideas/donacion/colaboradores/02-formas-de-aportar-y-compartir-documentos/cf-don-col-004-puedo-publicar-documentos-como-colaborador.md)

#### 3. Acuerdos y condiciones económicas

- **CF-DON-COL-005** · [¿Puedo acordar una compensación con el promotor?](../../ideas/donacion/colaboradores/03-acuerdos-y-condiciones-economicas/cf-don-col-005-puedo-acordar-una-compensacion-con-el-promotor.md)
- **CF-DON-COL-006** · [¿Cómo influye mi colaboración en la comisión del promotor?](../../ideas/donacion/colaboradores/03-acuerdos-y-condiciones-economicas/cf-don-col-006-como-influye-mi-colaboracion-en-la-comision-del-promotor.md)

#### 4. Funcionamiento de la iniciativa y responsabilidades

- **CF-DON-COL-007** · [¿Quién recibe lo recaudado y responde por su uso?](../../ideas/donacion/colaboradores/04-funcionamiento-de-la-iniciativa-y-responsabilidades/cf-don-col-007-quien-recibe-lo-recaudado-y-responde-por-su-uso.md)
- **CF-DON-COL-008** · [¿Qué debo saber sobre la revisión de una posible reversión?](../../ideas/donacion/colaboradores/04-funcionamiento-de-la-iniciativa-y-responsabilidades/cf-don-col-008-que-debo-saber-sobre-la-revision-de-una-posible-reversion.md)

## Validación técnica

La validación comprueba el conjunto real y la conservación de FR. La vista de prueba aislada activa temporalmente las 40 fichas en una copia, resuelve sus enlaces por código y genera sus 60 rutas; no cambia ni despliega la configuración real.

- Contraste exacto de los 40 cuerpos con la entrega editorial; conservación literal de los cuerpos y permalinks de PRO-001/002.
- Identidad única de códigos, rutas y etapas; cobertura principal única de los 136 registros CL y secuencia dentro de cada rol.
- Pruebas existentes Python y JavaScript, catálogos e integridad del sitio real, sin rutas públicas de Donación.
- Construcción Jekyll y comprobación de las 60 rutas y 139 fichas en la copia aislada.
- Navegación, filtros y búsqueda en escritorio y móvil, sin mezclar roles o categorías.

**Validación local del conjunto:** 51 pruebas Python, 25 pruebas JavaScript y comprobación de sintaxis de los 10 scripts JavaScript superadas. El catálogo real contiene 139 fichas inventariadas: 99 FR públicas y buscables, y 40 Donación excluidas de la búsqueda pública. La preparación de la copia aislada verifica las 40 fichas, sus tres roles, 16 etapas y 136 referencias principales; conserva los cuerpos y la configuración de las fuentes. El árbol de FR y los componentes compartidos permanecen sin cambios.

**Construcción y navegación:** el workflow de [validación de la PR #15](https://github.com/iskayApp/como-funciona/pull/15/checks) construye el sitio real y la copia aislada con Jekyll, comprueba las rutas y ejecuta las pruebas de escritorio y móvil. La ejecución asociada al commit que se vaya a revisar determina su resultado vigente; un resultado de un commit anterior no acredita uno posterior.

## Cortes conservados y continuidad

La [clasificación](DONACION_CLASIFICACION_2026-11-06.md), la [organización](DONACION_ORGANIZACION_2026-11-06.md) y la [identificación](DONACION_IDENTIFICACION_2026-11-06.md) conservan sus cortes originales. El primer avance técnico contenía únicamente PRO-001 y PRO-002; este registro lo sustituye como estado actual del desarrollo.

Las 40 fichas están desarrolladas y representadas en el código. La revisión del conjunto, la aprobación de sus versiones y la activación pública permanecen diferenciadas. La propuesta se mantiene revisable en la PR; esta incorporación no fusiona el cambio ni habilita la publicación de Donación.
