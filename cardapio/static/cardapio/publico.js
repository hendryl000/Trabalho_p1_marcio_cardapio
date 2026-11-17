(() => {
  'use strict';
  const catalog = new Map(JSON.parse(document.getElementById('catalog-data').textContent).map(item => [item.key, item]));
  const storageKey = `a-mesa:escolha:${document.body.dataset.organizacao}`;
  let bag = {};
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
    if (saved && typeof saved === 'object') {
      for (const [key, quantity] of Object.entries(saved)) {
        if (catalog.has(key) && Number.isInteger(quantity) && quantity > 0) bag[key] = Math.min(quantity, 99);
      }
    }
  } catch (_) { /* A seleção continua funcionando sem armazenamento. */ }
  const money = cents => new Intl.NumberFormat('pt-BR', {style: 'currency', currency: 'BRL'}).format(cents / 100);
  const dialog = document.getElementById('bag');
  const items = document.getElementById('bag-items');
  const toast = document.getElementById('toast');
  let toastTimer;
  let opener;
  function announce(message) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('visible');
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 2400);
  }
  function updateSummary() {
    const count = Object.values(bag).reduce((sum, value) => sum + value, 0);
    const total = Object.entries(bag).reduce((sum, [key, quantity]) => sum + catalog.get(key).centavos * quantity, 0);
    document.querySelectorAll('[data-count]').forEach(el => { el.textContent = count; });
    document.querySelectorAll('[data-total]').forEach(el => { el.textContent = money(total); });
    try { localStorage.setItem(storageKey, JSON.stringify(bag)); } catch (_) {}
  }
  function renderBag() {
    items.replaceChildren();
    if (!Object.keys(bag).length) {
      const empty = document.createElement('p');
      empty.className = 'bag-empty';
      empty.textContent = 'Sua escolha começa com um sabor. Toque em “Escolher” no cardápio.';
      items.append(empty);
    }
    for (const [key, quantity] of Object.entries(bag)) {
      const item = catalog.get(key);
      const row = document.createElement('div'); row.className = 'bag-row';
      const text = document.createElement('div');
      const title = document.createElement('h3'); title.textContent = item.nome;
      const price = document.createElement('p'); price.textContent = money(item.centavos * quantity);
      text.append(title, price);
      const control = document.createElement('div'); control.className = 'quantity';
      for (const action of [-1, 0, 1]) {
        const el = document.createElement(action ? 'button' : 'span');
        el.textContent = action === -1 ? '−' : action === 1 ? '+' : quantity;
        if (action) {
          el.type = 'button'; el.dataset.key = key; el.dataset.delta = action;
          el.setAttribute('aria-label', `${action > 0 ? 'Aumentar' : 'Diminuir'} quantidade de ${item.nome}`);
          if (action > 0 && quantity === 99) el.disabled = true;
        } else { el.setAttribute('aria-label', `${quantity} unidades`); }
        control.append(el);
      }
      row.append(text, control); items.append(row);
    }
    updateSummary();
  }
  document.querySelectorAll('[data-add]').forEach(button => button.addEventListener('click', () => {
    const key = button.dataset.add;
    if ((bag[key] || 0) >= 99) { announce('Limite de 99 unidades por item.'); return; }
    bag[key] = (bag[key] || 0) + 1;
    updateSummary();
    announce(`${catalog.get(key).nome} na sua escolha.`);
  }));
  items.addEventListener('click', event => {
    const button = event.target.closest('[data-delta]');
    if (!button) return;
    const key = button.dataset.key;
    const delta = Number(button.dataset.delta);
    bag[key] = Math.max(0, Math.min(99, bag[key] + delta));
    if (!bag[key]) delete bag[key];
    renderBag();
    const next = Array.from(items.querySelectorAll('[data-delta]')).find(el => el.dataset.key === key && Number(el.dataset.delta) === delta);
    (next || document.getElementById('close-bag')).focus();
  });
  document.querySelectorAll('[data-open-bag]').forEach(button => button.addEventListener('click', () => {
    opener = button; renderBag(); dialog.showModal();
  }));
  document.getElementById('close-bag').addEventListener('click', () => dialog.close());
  document.getElementById('keep-browsing').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { if (opener) opener.focus(); });
  dialog.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });
  const search = document.getElementById('search');
  const categoryButtons = [...document.querySelectorAll('.category')];
  const cards = [...document.querySelectorAll('.product')];
  let category = categoryButtons.find(button => button.classList.contains('active'))?.value || '';
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
  const searchable = new Map(cards.map(card => [card, normalize(card.querySelector('.product-copy').textContent)]));
  function filter() {
    const query = normalize(search.value.trim());
    let count = 0;
    for (const card of cards) {
      card.hidden = Boolean((category && card.dataset.category !== category) || !searchable.get(card).includes(query));
      if (!card.hidden) count++;
    }
    categoryButtons.forEach(button => {
      const active = button.value === category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    document.getElementById('empty').hidden = count > 0;
    document.getElementById('result-count').textContent = `${count} ${count === 1 ? 'opção' : 'opções'} para aproveitar`;
    const url = new URL(location.href);
    if (search.value.trim()) url.searchParams.set('q', search.value.trim()); else url.searchParams.delete('q');
    if (category) url.searchParams.set('categoria', category); else url.searchParams.delete('categoria');
    history.replaceState(null, '', url);
  }
  categoryButtons.forEach(button => button.addEventListener('click', event => { event.preventDefault(); category = button.value; filter(); }));
  search.addEventListener('input', filter);
  document.getElementById('filter-form').addEventListener('submit', event => { event.preventDefault(); filter(); });
  document.getElementById('clear-search')?.addEventListener('click', event => { event.preventDefault(); search.value = ''; category = ''; filter(); search.focus(); });
  document.documentElement.classList.add('js');
  updateSummary();
})();
