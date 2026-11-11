---
layout: default
title: "Reclama y conoce las posibles reversiones · Precompradores"
description: "Consulta las fichas de Precompradores en esta etapa de Precompra."
permalink: /precompra/precompradores/06-reclama-y-conoce-las-posibles-reversiones/
category: "Precompra"
role: "Precompradores"
stage: "Reclama y conoce las posibles reversiones"
stage_id: "PRE-PRC-E06"
stage_url: /precompra/precompradores/
status: "draft"
publication_status: "not_published"
editorial_status: "pending_review"
published: false
visibility: "private"
reviewed: false
---

# Reclama y conoce las posibles reversiones

> Recorrido preparado para revisión editorial. No publicado.

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
