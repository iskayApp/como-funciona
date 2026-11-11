---
layout: default
title: "Prepara la cuenta y recibe los fondos · Promotores"
description: "Consulta las fichas de Promotores en esta etapa de Precompra."
permalink: /precompra/promotores/07-prepara-la-cuenta-y-recibe-los-fondos/
category: "Precompra"
role: "Promotores"
stage: "Prepara la cuenta y recibe los fondos"
stage_id: "PRE-PRO-E07"
stage_url: /precompra/promotores/
status: "draft"
publication_status: "not_published"
editorial_status: "pending_review"
published: false
visibility: "private"
reviewed: false
---

# Prepara la cuenta y recibe los fondos

> Recorrido preparado para revisión editorial. No publicado.

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
