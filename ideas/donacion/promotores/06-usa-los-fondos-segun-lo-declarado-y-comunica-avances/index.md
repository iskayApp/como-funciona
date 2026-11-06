---
layout: default
title: Usa los fondos según lo declarado y comunica avances · Promotores
description: Consulta las fichas de Promotores en esta etapa de Donación.
permalink: /donacion/promotores/06-usa-los-fondos-segun-lo-declarado-y-comunica-avances/
category: Donación
role: Promotores
stage: Usa los fondos según lo declarado y comunica avances
stage_id: ORG-DON-PRO-06
stage_url: /donacion/promotores/
status: "published"
editorial_status: pending_review
published: true
visibility: "public"
reviewed: false
---

# Usa los fondos según lo declarado y comunica avances

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de Promotores]({{ '/donacion/promotores/' | relative_url }}).
