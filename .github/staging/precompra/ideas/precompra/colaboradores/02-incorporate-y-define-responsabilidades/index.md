---
layout: default
title: "Incorpórate y define responsabilidades · Colaboradores"
description: "Consulta las fichas de Colaboradores en esta etapa de Precompra."
permalink: /precompra/colaboradores/02-incorporate-y-define-responsabilidades/
category: "Precompra"
role: "Colaboradores"
stage: "Incorpórate y define responsabilidades"
stage_id: "PRE-COL-E02"
stage_url: /precompra/colaboradores/
status: "draft"
publication_status: "not_published"
editorial_status: "pending_review"
published: false
visibility: "private"
reviewed: false
---

# Incorpórate y define responsabilidades

> Recorrido contrastado con la guía vigente. Revisión editorial del propietario pendiente. No publicado.

{% assign stage_topics = site.pages | where: 'category', page.category | where: 'role', page.role | where: 'stage_id', page.stage_id | where_exp: 'entry', 'entry.code != nil' | where_exp: 'entry', 'entry.published != false' | where_exp: 'entry', 'entry.visibility != "private"' | where_exp: 'entry', 'entry.status != "draft"' | where_exp: 'entry', 'entry.status != "review"' | where_exp: 'entry', 'entry.status != "archived"' | sort: 'code' %}
{% for topic in stage_topics %}
- [{{ topic.title }}]({{ topic.url | relative_url }}){% if topic.editorial_status == 'pending_review' %} · pendiente de revisión editorial{% endif %}
{% endfor %}

[Volver al recorrido de {{ page.role }}]({{ page.stage_url | relative_url }}).
