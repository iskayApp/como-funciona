# Donación · Desarrollo, publicación y vinculación multimedia

Fecha de seguimiento: **6 de noviembre de 2026**. Fase: **DESARROLLAR completada; publicación autorizada**. Estado editorial: **pendiente de revisión del conjunto**.

Rama de trabajo: `feat/cf-donacion-pro-001`. Solicitud de cambios: [PR #15](https://github.com/iskayApp/como-funciona/pull/15).

## Secuencia y autorización

Las 40 fichas se desarrollaron y presentaron completas en sus tres roles y 16 etapas antes de continuar el código, conforme a la indicación del usuario. La entrega editorial tiene un documento maestro por ficha, un índice conjunto y un PDF completo de revisión. Después se autorizó el traslado al repositorio.

El usuario autorizó expresamente el siguiente paso: **«La revisión editorial la realizo posteriormente. Avanza con Donación hasta su publicación y vinculación con los vídeos existentes para esa categoría Donación»**. Esta decisión habilita la publicación del conjunto y su multimedia existente, manteniendo pendiente la revisión editorial. No aprueba las versiones de las fichas ni modifica la guía funcional.

## Avance por rol

| Rol | Etapas | Fichas desarrolladas | Pendientes de desarrollar | Aprobadas editorialmente | Con publicación autorizada | Registros CL principales |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Promotores | 7 | 18 | 0 | 0 | 18 | 71 |
| Donantes | 5 | 14 | 0 | 0 | 14 | 42 |
| Colaboradores | 4 | 8 | 0 | 0 | 8 | 23 |
| **Total** | **16** | **40** | **0** | **0** | **40** | **136** |

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
| `status` | `published` |
| `editorial_status` | `pending_review` |
| `published` | `true` |
| `visibility` | `public` |
| `reviewed` | `false` |
| `content_version` | `1` |
| `source_checked_on` | `2026-11-06` |
| `stage_id` / `stage_url` | Etapa propia y ruta de cada ficha |
| `classification_refs` | Registros principales completos, expandidos con tres dígitos |
| `classification_secondary_refs` | Referencias secundarias diferenciadas |
| `prev_code` / `next_code` | Secuencia dentro del mismo rol |
| `prev_url` / `next_url` | Rutas existentes dentro del mismo rol, nulas en los extremos |

`source_checked_on` acredita el contraste de la fuente; no sustituye la revisión editorial. La publicación autorizada y la aprobación editorial son estados separados. Las 60 páginas conservan `pending_review` y `reviewed: false`.

Las rutas y los cuerpos de las 40 fichas se conservan. Los recursos multimedia se vinculan mediante un registro separado; no se reescribe el contenido funcional para incorporar vídeos.

## Índices, búsqueda y mantenimiento

Los **20 índices** comprenden una portada de Donación, tres recorridos por rol y 16 etapas. Reutilizan navegación, búsqueda y orientación. Donación Colaboradores utiliza cuatro etapas propias, sin copiar las áreas profesionales de FR.

El registro de categorías declara Donación como `available` y `_config.yml` permite construir sus 60 páginas. El catálogo compartido contiene **139 fichas públicas y buscables: 99 FR y 40 Donación**. Las tres categorías todavía no desarrolladas conservan sus exclusiones. `noindex: true` permanece durante la prueba pública del sitio.

Donación pasa de la tarjeta de preparación a las fichas publicadas del control de mantenimiento. Las 40 aparecen pendientes de revisión editorial, con un acceso a este seguimiento. Los catálogos JSON siguen siendo resultados generados, no fuentes duplicadas.

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

## Vinculación de vídeos existentes

La vinculación utiliza publicaciones públicas verificadas de la cuenta oficial **@iskay.app**, contrastadas con los documentos de producción de Donación. El registro separa el código de categoría, el código de pieza y los códigos de ficha; un código publicitario repetido en FR no permite cruzar categorías.

El registro `_data/donacion_tiktok_publicaciones.json` conserva los IDs y las URLs oficiales, las relaciones principales y complementarias y su evidencia. La autorización para vincular estos recursos no se transforma en una aprobación editorial: `association_status` permanece `pending_review` y no se inventa una versión de ficha de la que derive el vídeo.

| Pieza Donación | Publicación oficial | Ficha principal | Fichas complementarias |
| --- | --- | --- | --- |
| PRO-EDU-02 · Cuatro elementos que ayudan a presentar una iniciativa con claridad | [TikTok · 15 de agosto de 2026](https://www.tiktok.com/@iskay.app/video/7674293282129595670) | CF-DON-PRO-009 | Ninguna |
| PRO-ENT-02 · Adaptación «Reflexión personal» | [TikTok · 21 de agosto de 2026](https://www.tiktok.com/@iskay.app/video/7675772626580638998) | CF-DON-PRO-009 | Ninguna |
| DON-VEN-02 · Apoya una campaña en iskay.app: así realizas tu aporte | [TikTok · 19 de agosto de 2026](https://www.tiktok.com/@iskay.app/video/7675768314064358678) | CF-DON-DON-005 | CF-DON-DON-002, CF-DON-DON-004 y CF-DON-DON-008 |

Son **tres vídeos, seis vinculaciones y cinco fichas con vídeo**. El inventario autenticado del canal, completo al generar el informe del 6 de noviembre de 2026 a las 13:15:39 UTC, acredita las publicaciones. El contraste con Producción, los subtítulos y el calendario identifica las piezas. Algunos documentos conservan un estado de publicación pendiente anterior: la existencia de estas publicaciones se acredita con la cuenta oficial, sin reescribir esos documentos.

La carpeta de producción contiene seis MP4 correspondientes a esas tres piezas, incluidas variantes de montaje y una base sin audio. No se duplican variantes como vídeos nuevos. No se encontró una publicación de vídeo de Colaboradores; COL-ENT-02 conserva preproducción de imagen estática. No se deducen enlaces de Facebook de archivos locales ni se cambian permisos de Drive.

Las piezas de Promotores se vinculan a la claridad de la presentación; no acreditan el inicio de Campaña o Precampaña ni se asocian a PRO-011. DON-VEN-02 se relaciona con la información de la iniciativa, la elección del aporte, perfil/anonimato y costes explícitos en sus subtítulos.

Los reproductores, los enlaces compartibles y mantenimiento consumen ese mismo registro. Cada vínculo dispone de ancla multimedia y acceso al original. Las fichas sin correspondencia comprobada muestran que todavía no tienen vídeo explicativo.

## Validación técnica

La validación comprueba ahora el sitio publicable real: las 60 rutas de Donación y las 99 fichas de FR. Se conserva la prueba aislada de una categoría ficticia para comprobar que los componentes siguen siendo extensibles.

- Contraste de los 40 cuerpos con la entrega editorial y conservación de sus permalinks.
- Identidad única de códigos, rutas y etapas; cobertura principal única de los 136 registros CL y secuencia dentro de cada rol.
- Pruebas Python y JavaScript, catálogos e integridad del sitio con 139 fichas públicas.
- Construcción Jekyll y comprobación de las 60 rutas de Donación.
- Navegación, filtros y búsqueda en escritorio y móvil, sin mezclar roles o categorías.
- Reproductores, anclas multimedia, enlaces al original y diagnóstico de los vídeos registrados.

La comprobación local de esta publicación superó **59 pruebas Python, 25 pruebas JavaScript y la sintaxis de los 10 scripts JavaScript**. Los catálogos contienen 139 fichas públicas; las 40 Donación siguen pendientes de revisión. Las 99 entradas FR del catálogo coinciden íntegramente con las anteriores a la ampliación multimedia. Donación incorpora tres vídeos, seis relaciones y cinco fichas con vídeo.

El workflow de [validación de la PR #15](https://github.com/iskayApp/como-funciona/pull/15/checks) determina el resultado vigente del commit que se vaya a publicar. El despliegue se ejecuta en [GitHub Pages](https://github.com/iskayApp/como-funciona/actions/workflows/pages.yml); se comprueban después las URLs y catálogos públicos. Un resultado técnico anterior no acredita un commit posterior.

## Revisión editorial posterior

Las 40 fichas conservan `editorial_status: pending_review` y `reviewed: false`, con aviso público y seguimiento en mantenimiento. La revisión posterior podrá introducir correcciones de contenido y versiones con su trazabilidad; la publicación actual no anticipa su resultado.

La [clasificación](DONACION_CLASIFICACION_2026-11-06.md), la [organización](DONACION_ORGANIZACION_2026-11-06.md) y la [identificación](DONACION_IDENTIFICACION_2026-11-06.md) conservan sus cortes originales. El primer avance técnico tenía solo PRO-001 y PRO-002; la incorporación de las 40 fichas antes de la autorización de publicación quedó en el commit `9c7b1b5`. Este registro recoge la autorización posterior para publicar y vincular los vídeos existentes.
