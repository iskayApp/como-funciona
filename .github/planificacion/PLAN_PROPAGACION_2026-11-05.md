# Preparación de la propagación de Cómo funciona

Fecha de consulta y preparación: 5 de noviembre de 2026.

Actualización documental de Donación: 6 de noviembre de 2026. Véanse las [aclaraciones previas a las fichas](ACLARACIONES_DONACION_2026-11-06.md).

## Objetivo y estado

Preparar la ampliación de Cómo funciona a las otras cuatro categorías de Ideas, con recorridos propios para los usuarios objetivo de cada una. Esta preparación identifica fuentes, roles, dependencias editoriales y condiciones de aceptación. No desarrolla fichas nuevas, no concede aprobaciones editoriales ni activa categorías en el sitio público.

La [organización de los tres recorridos de Donación](DONACION_ORGANIZACION_2026-11-06.md) se utiliza como base aceptada para **IDENTIFICAR**, con avance autorizado por el usuario el 6 de noviembre de 2026. El [catálogo de identificación](DONACION_IDENTIFICACION_2026-11-06.md) está preparado para revisión con **40 fichas: 18 de Promotores, 14 de Donantes y 8 de Colaboradores**, conforme a la secuencia del plan `BASE_GENERAL_CATEGORIAS_2026-11-04.md`. Después se propone continuar con Recompensa, Precompra e Inversión en Acciones. El orden posterior a Donación es una propuesta de trabajo, no una aprobación previa de sus contenidos.

El proceso común sigue CF-CORE-001:

**CLASIFICAR → ORGANIZAR → IDENTIFICAR → DESARROLLAR → VALIDAR/APROBAR → PUBLICAR → MANTENER.**

La guía funcional y las decisiones editoriales aprobadas sustentan las fichas. El repositorio representa y publica ese contenido; los componentes compartidos no determinan sus obligaciones ni completan vacíos funcionales.

## Punto de partida comprobado

La revisión parte de `main` en `084bc9b686366f1e15e34e76eaf4786f14df3bcc`:

- Financiamiento Reembolsable tiene 99 fichas: 33 de Promotores, 37 de Inversores y 29 de Colaboradores.
- Promotores tiene seis etapas; Inversores, siete; Colaboradores se organiza en una base común de 11 fichas y cuatro áreas con 18 fichas. Ninguna de esas estructuras obliga a reproducir el mismo número de etapas en otras categorías.
- Siete fichas tienen aprobación editorial explícita, 59 figuran pendientes y las 33 de Promotores no tienen `editorial_status` explícito. Publicación, revisión técnica y aprobación editorial son estados distintos.
- Las cuatro categorías restantes figuran en `_data/categories.yml` con `status: preparation` y sin roles activos. Sus árboles están excluidos de la publicación en `_config.yml`.
- El catálogo compartido sirve a buscador, orientación y mantenimiento. Las relaciones publicitarias y los recursos multimedia conservan identidad propia.

La publicación de prueba de fichas FR pendientes fue autorizada en su fase específica. Esa autorización no se traslada automáticamente a fichas de otras categorías.

## Fuentes consultadas

Se consultaron las guías maestras de categoría, no copias de producción publicitaria. Las fechas siguientes proceden del metadato de modificación en UTC; **no identifican una versión aprobada de la guía ni acreditan una nueva aprobación editorial**. Consulta realizada el 5 de noviembre de 2026.

| Documento | Fecha de modificación UTC | Uso en esta preparación |
| --- | --- | --- |
| 1 Donación.docx | 2026-05-12 | Roles, alcance de la categoría, configuración, colaboración, tarifas, seguimiento y reversión. |
| 1 Recompensa.docx | 2026-06-14 | Roles, recompensa ofrecida, entrega, colaboración y detección del conflicto sobre niveles. |
| 1 Precompra.docx | 2026-08-27 | Roles, oferta anticipada, modalidades, entrega, colaboradores y garantías; se utiliza la copia de categoría. |
| 1 InversiónAcciones.docx | 2026-07-05 | Roles, emisión, derechos, información societaria, áreas técnicas y formalización de acciones. |
| 00 CF-CORE-001 · Documento técnico maestro para propagar Cómo funciona · v1.0 | 2026-11-02 | Secuencia de trabajo, arquitectura compartida y separación de estados. |

Para la clasificación de Donación se utiliza **1 Donación.docx**, original restaurado con el único reemplazo autorizado por «Sin comisión para el donante» y su párrafo sobre cargos bancarios, respaldados por el apartado 4.2 «Comisión al donante». El archivo informa como fecha de última modificación el 6 de noviembre de 2026 a las 11:00:41 UTC. Las [referencias de Donación](ACLARACIONES_DONACION_2026-11-06.md) distinguen la guía vigente, las aclaraciones del usuario y la documentación operativa externa de precampaña e identidad pública. La tabla anterior conserva los metadatos de la consulta inicial del 5 de noviembre; la fecha de modificación no asigna una nueva versión editorial.

Las referencias de apartados se conservarán en las matrices de clasificación. Los enlaces de acceso y documentos privados permanecen en la gestión editorial; este plan público solo identifica títulos, fechas y secciones pertinentes.

## Usuarios objetivo y ámbitos a clasificar

Los nombres de los roles se han comprobado en «Dirigido a» o «Dirigido» de cada guía. La tabla recoge los ámbitos iniciales de clasificación. Donación ya dispone de una [organización por rol](DONACION_ORGANIZACION_2026-11-06.md); las otras categorías conservan pendiente esta fase. La tabla inicial no fija cantidad de fichas, códigos ni URL nuevas.

| Categoría | Rol confirmado | Intención principal | Preguntas y ámbitos para CLASIFICAR |
| --- | --- | --- | --- |
| Donación | Promotores | Presentar una causa y reunir apoyo. | Qué iniciativas pueden presentarse; finalidad y uso de fondos; configuración y precampaña; colaboración opcional y costos; cierre; actualizaciones, reclamaciones y reversión. |
| Donación | Donantes | Apoyar voluntariamente una causa. | Qué significa donar; información que revisar; participación y costos bancarios; seguimiento del destino de los fondos; reclamaciones y reversión cuando proceda. |
| Donación | Colaboradores | Aportar trabajo o conocimientos a la causa. | Alcance de la colaboración; funciones posibles; acuerdo con el promotor; participación durante la campaña o ejecución; documentación y transparencia. |
| Recompensa | Promotores | Financiar una iniciativa ofreciendo una recompensa definida. | Propuesta y recompensa; condiciones y plazos de entrega; campaña flexible; colaboradores y costos; ejecución, información y atención de incidencias. |
| Recompensa | Contribuyentes | Apoyar una iniciativa y recibir la recompensa ofrecida. | Qué se recibe; condiciones de la contribución; entrega; seguimiento; riesgos de incumplimiento, reclamaciones y reversión. |
| Recompensa | Colaboradores | Apoyar el desarrollo y el cumplimiento de la recompensa. | Producción; gestión presupuestaria; entregas y logística; comunicación; alcance y condiciones acordadas con el promotor. |
| Precompra | Promotores | Anticipar ingresos para producir un bien o prestar un servicio. | Unidades, precio y monto; modalidad de campaña; características y condiciones de entrega; colaboradores; formalización y garantías propias; cumplimiento e incidencias. |
| Precompra | Precompradores | Adquirir anticipadamente un producto o servicio. | Qué se adquiere; cantidad y precio; modalidad; entrega y condiciones especiales; seguimiento; cancelación, reembolso y reclamaciones. |
| Precompra | Colaboradores | Participar en la producción, atención o entrega. | Funciones y responsabilidades; momento de incorporación; acuerdos con el promotor; colaboración y descuentos; alcance de la intervención ante incidencias. Las listas de funciones requieren conciliación previa. |
| Inversión en Acciones | Promotores | Obtener capital mediante una emisión de acciones. | Empresa emisora; condiciones de la oferta; capital y precio de emisión; documentación e informes; campaña; suscripción, registro y acreditación; información posterior. |
| Inversión en Acciones | Inversionistas | Adquirir participación accionaria. | Empresa y oferta; derechos y riesgos; información societaria y técnica; participación; acreditación como accionista; resultados, transferibilidad e incidencias. |
| Inversión en Acciones | Colaboradores | Aportar criterios técnicos sobre la emisión. | Estados financieros y auditoría; valoración y viabilidad económica; riesgos financieros y de inversión; cumplimiento normativo y legal; límites de los criterios emitidos. |

### Nombres que deben conservarse

Recompensa utiliza **Contribuyentes** y Precompra utiliza **Precompradores**. No se sustituirán por «Participantes» o «Compradores» como nombre principal del recorrido. Esos términos pueden valorarse como alias de búsqueda si ayudan a encontrar el contenido sin alterar su identidad.

La guía de Acciones utiliza **Inversionistas**, mientras FR mantiene el recorrido **Inversores**. La identidad de un recorrido debe incluir categoría y rol; compartir un alias no permite mezclar sus resultados, etapas ni fichas.

En Acciones, la guía describe a los promotores como sociedades anónimas. Esta delimitación requiere su propio tratamiento editorial; no se trasladará la definición amplia de promotor de FR a esa categoría.

Los colaboradores de Donación, Recompensa y Precompra no deben heredar las cuatro áreas profesionales obligatorias de FR. Acciones define cuatro áreas propias, diferentes de las de FR.

## Diferencias que debe respetar el componente común

| Aspecto | Criterio de preparación |
| --- | --- |
| Organización | Cada rol tendrá su recorrido después de clasificar su guía. El componente admitirá etapas, áreas o base común según el caso. |
| Expectativa del aportante | Donación, recompensa, precompra y participación accionaria responden a expectativas distintas. Sus derechos, obligaciones y riesgos se extraerán individualmente. |
| Colaboración | Diferenciar apoyo operativo, acuerdos voluntarios y criterios técnicos profesionales. No equiparar colaboración a garantía de cumplimiento. |
| Modalidad de campaña | Las guías consultadas de Donación y Recompensa contemplan flexible; Precompra y Acciones contemplan fija y flexible. Las fichas de cada una se validarán contra su fuente y decisiones aprobadas. |
| Ubicación | Donación, Recompensa y Precompra describen ubicación de la iniciativa; Acciones describe ubicación de la empresa. No reutilizar automáticamente el campo FR de ubicación del promotor. |
| Documentación | Los permisos, actos y documentos exigidos dependen de la categoría. No incorporar garantías de deuda, tabla de amortización o NDA por simple reutilización de una plantilla. |
| Identidad editorial | Una ficha, un archivo y una URL estable. Los códigos de fichas, piezas publicitarias y recursos multimedia permanecen separados. |
| Estados | Distinguir preparación, revisión, aprobación editorial, publicación de prueba, publicación técnica y verificación de recursos. |

## Registro de discrepancias y aclaraciones

Este registro conserva los pendientes y las aclaraciones resueltas con su alcance por categoría. Las fichas afectadas por un pendiente no deben presentarse como definitivas hasta resolverlo en la fuente o mediante una aclaración editorial expresamente aprobada.

| ID de preparación | Fuente y apartado | Evidencia encontrada | Estado y acción para la ficha afectada |
| --- | --- | --- | --- |
| PROP-REC-01 | Recompensa · Dirigido a; Promotores; Inicio de campaña | La guía conserva niveles de contribución y recompensas por rango, mientras la decisión aprobada del proyecto elimina los niveles. | Conciliar la guía con la decisión aprobada. Conservar la modalidad flexible; no volver a introducir niveles en fichas o interfaces. |
| PROP-PRE-01 | Precompra · Descuentos; Inicio de campaña; tabla de descuentos | Descuentos enumera producción, presupuesto, postventa y comunicación. Campaña y tabla enumeran producción, postventa, calidad y logística. | Precisar funciones, elegibilidad para el descuento y relación entre ambas listas. No escoger una silenciosamente. |
| PROP-PRE-02 | Precompra · Dirigido a; Descuentos; Inicio de campaña | Unas descripciones presentan colaboradores en toda iniciativa y participación necesaria; otras los califican como opcionales. | Unificar el carácter de la colaboración y sus condiciones antes de redactar obligaciones de promotores o colaboradores. |
| PROP-PRE-03 | Precompra · Transferencia de fondos · garantías | La guía enumera seguro de cumplimiento y prenda sobre activos, además de representación de precompradores, sin explicar de forma inequívoca si las garantías son alternativas o acumulativas. | Aclarar la regla y los documentos correspondientes. No sustituirla por pagaré o hipoteca de FR. |
| PROP-ACC-01 | Inversión en Acciones · Procedimiento para reclamaciones y riesgo de pérdida | Un párrafo incorpora mora, cobro, ejecución de garantías y Representante Legal de los Inversionistas, términos que no se desarrollan como obligaciones de deuda en el resto del modelo accionario. | Revisar si existe arrastre de FR y precisar incumplimientos societarios, derechos y mecanismos aplicables. No prometer cuotas, intereses ni reembolso obligatorio del capital accionario. |
| PROP-COM-01 | Donación, Recompensa y Precompra · Descuentos y tablas de tarifas | Donación: el usuario aclaró 0,50% por colaborador hasta 2,00% en total, restados directamente de la tasa de comisión, conservando la notación %. En Recompensa y Precompra sigue registrada la diferencia entre el texto «sobre la comisión» y los extremos de las tablas. | Cerrado en Donación por aclaración del usuario. Recompensa y Precompra mantienen pendiente definir la base y forma de cálculo en sus propias fuentes antes de publicar ejemplos numéricos o una calculadora. |
| PROP-DON-01 | Donación · Decisión editorial del 6 de noviembre; [referencias](ACLARACIONES_DONACION_2026-11-06.md) | Beneficio tributario retirado por decisión del usuario del 6 de noviembre de 2026. | Cerrado por retirada editorial. No se desarrolla ficha sobre ese beneficio. La guía lo sustituye por «Sin comisión para el donante», con respaldo en su apartado 4.2. |
| PROP-DON-02 | Donación · Inicio de campaña · Período; manual de precampaña y referencias del calendario | El detalle operativo procede del manual del 10 de agosto de 2026 y de los registros DON-EDU-02/DON-INS-02 con estado Aprobada en sus hojas; DON-VEN-02 es referencia complementaria. | Referencias operativas verificadas para IDENTIFICAR; detalle en las [referencias de Donación](ACLARACIONES_DONACION_2026-11-06.md). Tratar precampaña e identidad en manuales y fichas, con sus fuentes separadas de la guía; no requiere ampliar el documento de categoría. |
| PROP-COM-02 | Donación · apartado 7 «Transferencia de fondos»; demás guías · Transferencia y notificaciones | El usuario confirmó que la notificación a los donantes bajo el apartado 7 de Donación se refiere a la transferencia de fondos. | Cerrado en Donación. Clasificar el aviso dentro del procedimiento de transferencia. Las demás categorías conservan su aclaración independiente; la decisión de FR no se traslada automáticamente. |

Este registro describe discrepancias documentales. No sustituye la revisión jurídica aplicable ni formula requisitos nuevos para los usuarios.

## Lista de trabajo de los doce recorridos

«Identificados» significa que se han localizado la fuente y el nombre del rol. El usuario autorizó avanzar desde la [organización de Donación](DONACION_ORGANIZACION_2026-11-06.md) a **IDENTIFICAR**. El [catálogo de sus tres roles](DONACION_IDENTIFICACION_2026-11-06.md) está preparado para revisión. La clasificación de los otros nueve recorridos continúa pendiente.

| Categoría | Rol | Fuente y rol | Clasificar | Organizar | Identificar fichas | Desarrollar | Validar y aprobar | Publicar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Donación | Promotores | Identificados | Base aceptada para organizar | Base aceptada para identificar | Preparada para revisión | Pendiente | Pendiente | Pendiente |
| Donación | Donantes | Identificados | Base aceptada para organizar | Base aceptada para identificar | Preparada para revisión | Pendiente | Pendiente | Pendiente |
| Donación | Colaboradores | Identificados | Base aceptada para organizar | Base aceptada para identificar | Preparada para revisión | Pendiente | Pendiente | Pendiente |
| Recompensa | Promotores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Recompensa | Contribuyentes | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Recompensa | Colaboradores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Precompra | Promotores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Precompra | Precompradores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Precompra | Colaboradores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Inversión en Acciones | Promotores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Inversión en Acciones | Inversionistas | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Inversión en Acciones | Colaboradores | Identificados | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |

### Identificación de las fichas y siguiente bloque

El [catálogo de identificación de Donación](DONACION_IDENTIFICACION_2026-11-06.md) está **preparado para revisión** con **40 fichas: 18 de Promotores, 14 de Donantes y 8 de Colaboradores**. Incluye 39 fichas vinculadas a los 136 registros CL y una de identidad pública del donante sustentada en referencias operativas, sin registro CL. La clasificación y los destinos principales de la organización se conservan.

El siguiente bloque es **DESARROLLAR** las fichas identificadas. La organización responde a cada rol y admite consulta de seguimiento e incidencias cuando corresponda; no traslada automáticamente la estructura de Promotores FR ni da por terminada una categoría con un único rol.

## Entregables y condiciones por fase

| Fase | Resultado verificable | Condición para continuar |
| --- | --- | --- |
| CLASIFICAR | Matriz de elementos individuales por categoría y rol, con fuente y discrepancias. | Cobertura contrastada con la guía; vacíos y contradicciones visibles. |
| ORGANIZAR | Recorrido propio por rol, con etapas o áreas justificadas. | Cada elemento de la clasificación tiene destino; se evita trasladar obligaciones entre roles. |
| IDENTIFICAR | Inventario de fichas, preguntas, códigos propios y referencias a la clasificación. | No hay colisiones con otras fichas, piezas o recursos; los códigos no se deducen del calendario publicitario. |
| DESARROLLAR | Fichas con respuesta breve, explicación y acción pertinente al rol. | Contenido contrastado, sin requisitos inventados; identidad y trazabilidad completas. |
| VALIDAR/APROBAR | Revisión funcional, editorial y de presentación registrada. | La aprobación pertenece a la versión revisada; las discrepancias que afecten a la ficha están resueltas. |
| PUBLICAR | Archivo y URL canónica accesibles, recorrido y catálogo actualizados. | Verificación del sitio generado y desplegado; nueva disponibilidad respaldada por fichas reales. |
| MANTENER | Control de versiones, impacto de cambios, recursos y relaciones publicitarias. | Cambios de guía o ficha identifican recursos derivados que requieren revisión; la comprobación técnica no altera la aprobación editorial. |

## Preparación técnica común

1. Mantener un registro de categorías y roles y un catálogo compartido. La preparación editorial se documenta en planificación; no se introducen fichas ficticias en el catálogo público.
2. Activar cada recorrido cuando tenga página real y fichas publicables conforme a su estado. La categoría puede avanzar por roles; los que aún no estén disponibles deben indicarlo sin llevar al usuario a otro rol como sustituto.
3. Usar identificadores compuestos de categoría, rol y sección. Secciones con el mismo nombre no deben mezclarse entre categorías ni roles.
4. Mantener las URL y códigos existentes de FR. Cualquier futura unificación de nomenclatura requerirá conservar identidad y enlaces ya compartidos.
5. Registrar `content_version`, fuente, estado editorial y fecha de revisión de manera explícita en las nuevas fichas. La falta de versión identificada de una guía debe declararse, sin convertir fecha o nombre de archivo en versión aprobada.
6. Vincular piezas publicitarias mediante correspondencia editorial comprobada y recursos mediante IDs reales. Una ficha puede existir sin multimedia o sin pieza de publicidad asociada.
7. Conservar la distinción entre enlace canónico, ancla del recurso dentro de la ficha y original de la publicación. No crear anclas para piezas que no están insertadas.
8. Mantener el carácter público de consulta del Centro de mantenimiento. No introducir datos personales, documentos privados, credenciales ni controles que simulen aprobación o edición autenticada.
9. Actualizar deliberadamente las pruebas que protegen el alcance FR cuando se autorice una ampliación. Los totales históricos de 99 fichas sirven como referencia, no como límite permanente de la arquitectura.

## Casos de aceptación antes de activar un recorrido

| Área | Comprobación |
| --- | --- |
| Navegación | Portada, menú, categoría, rol, sección, ficha y regreso conducen a páginas reales. No hay enlaces públicos a categorías o roles vacíos. |
| Identidad | Cada ficha tiene un código y una URL únicos. Su categoría, rol y sección coinciden en página, catálogo, buscador, orientación y mantenimiento. |
| Búsqueda | Consulta por pregunta, concepto, título y código; manejo de tildes; filtros combinados y limpieza; cero resultados comprensibles; ausencia de cruces de rol o categoría. |
| Orientación | Preguntas breves con opciones, sin registro ni datos personales; sin almacenar o enviar respuestas. La salida enlaza fichas canónicas disponibles de la categoría y rol elegidos. |
| Recorridos incompletos | Se informa qué falta y se permite volver o usar búsqueda. No se recomienda una ficha de Promotores como equivalente de Donantes, Contribuyentes, Precompradores o Inversionistas. |
| Fichas | Lectura comprensible por sí misma, encabezados correctos, acción correspondiente al rol y enlaces anterior/siguiente válidos cuando existan. |
| Multimedia | Texto alternativo y alternativa funcional; reproducción voluntaria cuando corresponda; enlace original; fallo externo sin impedir leer la ficha. |
| Compartición | Los tres enlaces disponibles se generan desde metadatos y conducen al destino correcto. Se ocultan opciones que no tienen recurso o ancla real. |
| Mantenimiento | Jerarquía y filtros coherentes; aprobación, publicación y verificación técnica diferenciadas; pendientes y recursos desactualizados visibles. |
| Presentación | Comprobación a 1280, 390 y 320 píxeles; teclado, foco, Escape y navegación básica sin JavaScript; ausencia de desbordamientos que impidan usar la página. |
| Publicación | Rutas y recursos internos comprobados en el sitio generado; despliegue asociado al cambio; acceso real a las URL publicadas y comprobación de sus catálogos. |

La comprobación de enlaces o la respuesta HTTP de un proveedor externo no certifican por sí solas la reproducción completa de su contenido. Los fallos y las limitaciones de acceso se registrarán con su alcance real.

## Tienda Productos y servicios

Tienda se prepara como una **extensión separada de Ideas**, con Vendedores, Compradores y Colaboradores. No se añade como una sexta categoría de financiamiento colaborativo.

Su preparación requerirá localizar y revisar su propia guía para pedidos, evidencias de entrega o prestación, liberación de importes, reclamaciones, devoluciones y acuerdos de colaboración. Los componentes de navegación y consulta podrán reutilizarse cuando el dominio y sus fuentes estén definidos. Este plan no desarrolla ni activa ese módulo.

## Seguimiento del trabajo

### Actualización documental del 6 de noviembre de 2026

PROP-DON-01 está cerrado por retirada editorial. PROP-DON-02 cuenta con referencias operativas verificadas para IDENTIFICAR, separadas de la guía. PROP-COM-01 y PROP-COM-02 están cerrados para Donación conforme a las aclaraciones del usuario sobre descuentos y notificación de transferencia; las demás categorías conservan su revisión independiente. El detalle está en [ACLARACIONES_DONACION_2026-11-06.md](ACLARACIONES_DONACION_2026-11-06.md).

El usuario autorizó avanzar desde la [organización de los tres recorridos](DONACION_ORGANIZACION_2026-11-06.md) a **IDENTIFICAR**. El [catálogo de identificación](DONACION_IDENTIFICACION_2026-11-06.md) está preparado para revisión con 40 fichas: 18 de Promotores, 14 de Donantes y 8 de Colaboradores. Son 39 fichas con registros CL y una de identidad pública del donante sustentada en referencias operativas, sin registro CL. El siguiente entregable será **DESARROLLAR** sus contenidos; la aprobación editorial y la publicación continúan pendientes. Las otras categorías pueden avanzar en la conciliación de sus fuentes mientras se consolida este bloque.

Las ampliaciones mantendrán la cadena **guía y decisiones aprobadas → ficha canónica → multimedia → piezas y canales**, con registros distintos de aprobación editorial, publicación y comprobación técnica.



