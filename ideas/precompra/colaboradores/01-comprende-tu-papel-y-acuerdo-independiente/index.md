---
layout: default
title: "Comprende tu papel y acuerdo independiente · Colaboradores"
description: "Consulta las fichas de Colaboradores en esta etapa de Precompra."
permalink: /precompra/colaboradores/01-comprende-tu-papel-y-acuerdo-independiente/
category: "Precompra"
role: "Colaboradores"
stage: "Comprende tu papel y acuerdo independiente"
stage_id: "PRE-COL-E01"
stage_url: /precompra/colaboradores/
status: "published"
publication_status: "published"
editorial_status: "pending_review"
published: true
visibility: "public"
reviewed: false
---

# Comprende tu papel y acuerdo independiente

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
