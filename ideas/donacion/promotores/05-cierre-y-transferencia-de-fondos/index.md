---
layout: default
title: Cierre y transferencia de fondos · Promotores
description: Consulta las fichas de Promotores en esta etapa de Donación.
permalink: /donacion/promotores/05-cierre-y-transferencia-de-fondos/
category: Donación
role: Promotores
stage: Cierre y transferencia de fondos
stage_id: ORG-DON-PRO-05
stage_url: /donacion/promotores/
status: "published"
editorial_status: pending_review
published: true
visibility: "public"
reviewed: false
---

# Cierre y transferencia de fondos

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de Promotores]({{ '/donacion/promotores/' | relative_url }}).
