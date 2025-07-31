(function () {
  function fetchMonth(gridEl, year, month) {
    const endpoint = `/calendar/month/${year}/${month}/`;
    gridEl.dataset.year = year;
    gridEl.dataset.month = month;
    gridEl.dataset.endpoint = endpoint;
    gridEl.innerHTML = `<div class="text-center py-5 text-muted">불러오는 중…</div>`;
    fetch(endpoint, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(r => r.text())
      .then(html => {
        gridEl.innerHTML = html;
        const titleEl = gridEl.closest(".modal-content").querySelector("[data-bsmc-title]");
        titleEl.textContent = `${year}년 ${month}월`;
      });
  }

  function nextYM(year, month, delta) {
    const d = new Date(year, month - 1 + delta, 1);
    return { y: d.getFullYear(), m: d.getMonth() + 1 };
  }

  function openModal(modalEl) {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  }

  function init(selector, opts) {
    const modalEl = document.querySelector(selector);
    if (!modalEl) return;
    const grid = modalEl.querySelector(".bsmc-grid");
    const y = parseInt(grid.dataset.year, 10);
    const m = parseInt(grid.dataset.month, 10);
    fetchMonth(grid, y, m);

    modalEl.querySelector("[data-bsmc-prev]").addEventListener("click", () => {
      const { y, m } = nextYM(parseInt(grid.dataset.year,10), parseInt(grid.dataset.month,10), -1);
      fetchMonth(grid, y, m);
    });
    modalEl.querySelector("[data-bsmc-next]").addEventListener("click", () => {
      const { y, m } = nextYM(parseInt(grid.dataset.year,10), parseInt(grid.dataset.month,10), +1);
      fetchMonth(grid, y, m);
    });
    modalEl.querySelector("[data-bsmc-today]").addEventListener("click", () => {
      const t = new Date();
      fetchMonth(grid, t.getFullYear(), t.getMonth() + 1);
    });

    // 최초 1회만 자동 오픈 옵션
    if (opts && opts.autoOpen) {
      const key = selector + ":opened";
      if (!localStorage.getItem(key)) {
        openModal(modalEl);
        localStorage.setItem(key, "1");
      }
    }
  }

  window.BSMC = { init, open: (sel) => openModal(document.querySelector(sel)) };
})();