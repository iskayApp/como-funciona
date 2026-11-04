/* Filter the existing canonical links. No duplicate catalog, requests or storage. */
(function () {
  'use strict';
  function normalize(value) {
    return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }
  document.querySelectorAll('.fr-hub').forEach(function (hub) {
    var controls = hub.querySelector('[data-fr-filter]');
    if (!controls) return;
    var query = controls.querySelector('[data-fr-filter-query]');
    var select = controls.querySelector('[data-fr-filter-section]');
    var clear = controls.querySelector('[data-fr-filter-clear]');
    var status = controls.querySelector('[data-fr-filter-status]');
    var empty = controls.querySelector('[data-fr-filter-empty]');
    var isCollaborator = hub.getAttribute('data-fr-role') === 'Colaboradores';
    var groups = Object.create(null);
    var sections = Array.from(hub.querySelectorAll('.fr-section')).map(function (node) {
      var title = node.querySelector('.fr-section-heading strong').textContent.trim();
      var kind = node.getAttribute('data-section-kind');
      var parent = select;
      if (isCollaborator) {
        if (!groups[kind]) {
          groups[kind] = document.createElement('optgroup');
          groups[kind].label = kind === 'area' ? 'Áreas de colaboración' : 'Base común';
          select.appendChild(groups[kind]);
        }
        parent = groups[kind];
      }
      var option = document.createElement('option');
      option.value = node.id;
      option.textContent = title;
      parent.appendChild(option);
      return {
        node: node,
        kind: kind,
        count: node.querySelector('.fr-section-count'),
        previousOpen: node.open,
        topics: Array.from(node.querySelectorAll('[data-fr-topic]')).map(function (link) {
          return {
            node: link.closest('li'),
            text: normalize(link.querySelector('span').textContent + ' ' + link.getAttribute('data-fr-code'))
          };
        })
      };
    });
    var total = sections.reduce(function (sum, section) { return sum + section.topics.length; }, 0);
    var wasFiltering = false;
    function apply() {
      var words = normalize(query.value).split(/\s+/).filter(Boolean);
      var filtering = words.length > 0 || select.value !== '';
      var matches = 0;
      var visibleSections = 0;
      if (filtering && !wasFiltering) {
        sections.forEach(function (section) { section.previousOpen = section.node.open; });
      }
      sections.forEach(function (section) {
        var allowed = !select.value || select.value === section.node.id;
        var count = 0;
        section.topics.forEach(function (topic) {
          var visible = allowed && words.every(function (word) { return topic.text.includes(word); });
          topic.node.hidden = !visible;
          if (visible) count += 1;
        });
        section.node.hidden = count === 0;
        section.count.textContent = filtering
          ? count + ' de ' + section.topics.length
          : count + (count === 1 ? ' ficha' : ' fichas');
        if (count) {
          matches += count;
          visibleSections += 1;
        }
        if (filtering) section.node.open = count > 0;
        else if (wasFiltering) section.node.open = section.previousOpen;
      });
      hub.querySelectorAll('[data-fr-group-heading]').forEach(function (heading) {
        var kind = heading.getAttribute('data-fr-group-heading');
        heading.hidden = !sections.some(function (section) { return section.kind === kind && !section.node.hidden; });
      });
      status.textContent = (filtering ? matches + ' de ' + total : String(total)) +
        ' fichas en ' + visibleSections + (visibleSections === 1 ? ' sección.' : ' secciones.');
      empty.hidden = matches !== 0;
      clear.disabled = !filtering;
      wasFiltering = filtering;
    }
    controls.querySelector('form').addEventListener('submit', function (event) {
      event.preventDefault();
      apply();
    });
    query.addEventListener('input', apply);
    query.addEventListener('search', apply);
    select.addEventListener('change', apply);
    clear.addEventListener('click', function () {
      query.value = '';
      select.value = '';
      apply();
      query.focus();
    });
    apply();
    controls.hidden = false;
  });
}());
