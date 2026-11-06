---
layout: default
title: Conocer la iniciativa y a su equipo · Donantes
description: Consulta las fichas de Donantes en esta etapa de Donación.
permalink: /donacion/donantes/02-conocer-la-iniciativa-y-a-su-equipo/
category: Donación
role: Donantes
stage: Conocer la iniciativa y a su equipo
stage_id: ORG-DON-DON-02
stage_url: /donacion/donantes/
status: draft
editorial_status: pending_review
published: false
visibility: private
reviewed: false
---

# Conocer la iniciativa y a su equipo

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de Donantes]({{ '/donacion/donantes/' | relative_url }}).
