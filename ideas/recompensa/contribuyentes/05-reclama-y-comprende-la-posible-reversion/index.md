---
layout: default
title: "Reclama y comprende la posible reversión · Contribuyentes"
description: "Consulta las fichas de Contribuyentes en esta etapa de Recompensa."
permalink: /recompensa/contribuyentes/05-reclama-y-comprende-la-posible-reversion/
category: "Recompensa"
role: "Contribuyentes"
stage: "Reclama y comprende la posible reversión"
stage_id: "REC-CON-E05"
stage_url: /recompensa/contribuyentes/
status: "published"
editorial_status: pending_review
published: true
visibility: "public"
reviewed: false
---

# Reclama y comprende la posible reversión

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}{% if topic.pending_implementation %} · funcionalidad en desarrollo{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
