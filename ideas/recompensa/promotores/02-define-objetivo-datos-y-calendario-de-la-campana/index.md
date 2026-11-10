---
layout: default
title: "Define objetivo, datos y calendario de la campaña · Promotores"
description: "Consulta las fichas de Promotores en esta etapa de Recompensa."
permalink: /recompensa/promotores/02-define-objetivo-datos-y-calendario-de-la-campana/
category: "Recompensa"
role: "Promotores"
stage: "Define objetivo, datos y calendario de la campaña"
stage_id: "REC-PRO-E02"
stage_url: /recompensa/promotores/
status: "published"
editorial_status: pending_review
published: true
visibility: "public"
reviewed: false
---

# Define objetivo, datos y calendario de la campaña

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}{% if topic.pending_implementation %} · funcionalidad en desarrollo{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
