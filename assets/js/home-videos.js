/* Filtros progresivos de la galería: no guardan respuestas ni solicitan datos. */
(() => {
  const gallery = document.getElementById('videos');
  if (!gallery) return;

  const cards = Array.from(gallery.querySelectorAll('.home-video-card'));
  const filters = document.getElementById('home-video-filters');
  const category = document.getElementById('home-video-category');
  const role = document.getElementById('home-video-role');
  const stage = document.getElementById('home-video-stage');
  const reset = document.getElementById('home-video-reset');
  const count = document.getElementById('home-video-count');
  const empty = document.getElementById('home-video-empty');
  if (!cards.length || !filters || !category || !role || !stage || !reset || !count || !empty) return;

  const parts = (value) => (value || '').split('|').filter(Boolean);
  const normalized = (list) => [...new Set(list.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));

  function setOptions(select, values) {
    const previous = select.value;
    const initial = select.options[0].textContent;
    const allowed = normalized(values);
    select.replaceChildren(new Option(initial, ''));
    allowed.forEach((value) => select.add(new Option(value, value)));
    select.value = allowed.includes(previous) ? previous : '';
  }

  function render() {
    setOptions(category, cards.map((card) => card.dataset.category));
    const categoryValue = category.value;
    const categoryCards = cards.filter((card) => !categoryValue || card.dataset.category === categoryValue);

    setOptions(role, categoryCards.flatMap((card) => parts(card.dataset.roles)));
    const roleValue = role.value;
    const roleCards = categoryCards.filter((card) => !roleValue || parts(card.dataset.roles).includes(roleValue));

    setOptions(stage, roleCards.flatMap((card) => parts(card.dataset.stages)));
    const stageValue = stage.value;
    let visible = 0;
    cards.forEach((card) => {
      const matches = (!categoryValue || card.dataset.category === categoryValue)
        && (!roleValue || parts(card.dataset.roles).includes(roleValue))
        && (!stageValue || parts(card.dataset.stages).includes(stageValue));
      card.hidden = !matches;
      if (matches) visible += 1;
    });

    count.textContent = visible === 1 ? '1 vídeo disponible' : visible + ' vídeos disponibles';
    empty.hidden = visible !== 0;
    reset.hidden = !(categoryValue || roleValue || stageValue);
  }

  category.addEventListener('change', () => { role.value = ''; stage.value = ''; render(); });
  role.addEventListener('change', () => { stage.value = ''; render(); });
  stage.addEventListener('change', render);
  reset.addEventListener('click', () => {
    category.value = '';
    role.value = '';
    stage.value = '';
    render();
  });
  filters.hidden = false;
  render();
})();
