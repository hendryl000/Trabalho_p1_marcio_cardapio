(() => {
  'use strict';
  const canvas = document.getElementById('vendas-grafico');
  if (!canvas || typeof Chart === 'undefined') return;
  const dados = JSON.parse(document.getElementById('dados-vendas').textContent);
  const moeda = valor => new Intl.NumberFormat('pt-BR', {style: 'currency', currency: 'BRL'}).format(valor);
  new Chart(canvas, {
    type: 'line',
    data: {
      labels: dados.map(item => item.mes),
      datasets: [{label: 'Faturamento', data: dados.map(item => Number(item.faturamento)),
        borderColor: '#365f45', backgroundColor: '#6f8f5420', fill: true,
        tension: 0.2, pointRadius: 4, pointHoverRadius: 7, pointBackgroundColor: '#365f45', borderWidth: 2}],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: matchMedia('(prefers-reduced-motion: reduce)').matches ? false : {duration: 350},
      plugins: {legend: {display: false}, tooltip: {callbacks: {label: ctx => moeda(ctx.parsed.y)}}},
      scales: {
        x: {grid: {display: false}, ticks: {color: '#76816d'}},
        y: {beginAtZero: true, grid: {color: '#e9eddf'}, ticks: {color: '#76816d', callback: value => moeda(value)}},
      },
    },
  });
})();
