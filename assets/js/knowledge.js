/* Presentación progresiva sobre el contenido canónico. Sin red ni almacenamiento. */
(() => {
  'use strict';
  const mobile = window.matchMedia('(max-width: 760px)');
  document.querySelectorAll('.home-routes, .hub-index details, .topic-index details').forEach(node => {
    node.open = !mobile.matches;
  });
  document.querySelectorAll('[data-hub-target]').forEach(link => {
    link.addEventListener('click', event => {
      const section = document.getElementById(link.dataset.hubTarget);
      if (!section || section.hidden) return;
      event.preventDefault();
      section.open = true;
      section.querySelector('summary').focus();
      section.scrollIntoView({block: 'start', behavior: 'auto'});
      document.querySelectorAll('[data-hub-target]').forEach(item => item.removeAttribute('aria-current'));
      link.setAttribute('aria-current', 'true');
    });
  });
  const article = document.querySelector('.page-topic article.content');
  const index = document.querySelector('.topic-index');
  if (!article || !index) return;
  function placeIndex() {
    index.querySelector('details').open = !mobile.matches;
    if (mobile.matches) article.querySelector('h1')?.after(index);
    else article.after(index);
  }
  placeIndex();
  mobile.addEventListener('change', placeIndex);
  const nav = index.querySelector('nav');
  article.querySelectorAll('h2[id]').forEach(heading => {
    const link = document.createElement('a');
    link.href = '#' + heading.id;
    link.textContent = heading.textContent;
    nav.appendChild(link);
  });
  index.hidden = !nav.children.length;
  const summary = article.querySelector('#respuesta-breve');
  if (summary) {
    const panel = document.createElement('section');
    panel.className = 'answer-summary';
    panel.setAttribute('aria-labelledby', summary.id);
    summary.before(panel);
    panel.appendChild(summary);
    while (panel.nextElementSibling?.tagName === 'P') panel.appendChild(panel.nextElementSibling);
  }
  article.querySelectorAll('.media-block img').forEach(image => {
    const link = document.createElement('a');
    link.className = 'media-open-link';
    link.href = image.src;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Ver recurso a tamaño completo ↗';
    image.closest('.media-block').appendChild(link);
  });
  article.querySelectorAll('table').forEach((table, number) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', 'Tabla de la ficha. Desplázala horizontalmente si es necesario.');
    const hint = document.createElement('p');
    hint.className = 'table-scroll-hint';
    hint.id = 'table-help-' + number;
    hint.textContent = 'Desliza la tabla para consultar todas las columnas.';
    wrapper.setAttribute('aria-describedby', hint.id);
    table.before(hint);
    table.before(wrapper);
    wrapper.appendChild(table);
  });
})();
