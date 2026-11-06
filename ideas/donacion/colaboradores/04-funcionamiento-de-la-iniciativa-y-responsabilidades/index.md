---
layout: default
title: Funcionamiento de la iniciativa y responsabilidades · Colaboradores
description: Consulta las fichas de Colaboradores en esta etapa de Donación.
permalink: /donacion/colaboradores/04-funcionamiento-de-la-iniciativa-y-responsabilidades/
category: Donación
role: Colaboradores
stage: Funcionamiento de la iniciativa y responsabilidades
stage_id: ORG-DON-COL-04
stage_url: /donacion/colaboradores/
status: draft
editorial_status: pending_review
published: false
visibility: private
reviewed: false
---

# Funcionamiento de la iniciativa y responsabilidades

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de Colaboradores]({{ '/donacion/colaboradores/' | relative_url }}).
