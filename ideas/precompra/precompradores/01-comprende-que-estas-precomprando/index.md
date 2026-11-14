---
layout: default
title: "Comprende qué estás precomprando · Precompradores"
description: "Consulta las fichas de Precompradores en esta etapa de Precompra."
permalink: /precompra/precompradores/01-comprende-que-estas-precomprando/
category: "Precompra"
role: "Precompradores"
stage: "Comprende qué estás precomprando"
stage_id: "PRE-PRC-E01"
stage_url: /precompra/precompradores/
status: "published"
publication_status: "published"
editorial_status: "pending_review"
published: true
visibility: "public"
reviewed: false
---

# Comprende qué estás precomprando

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
