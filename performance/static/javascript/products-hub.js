(function() {
    const qs = (sel, ctx=document) => ctx.querySelector(sel);
    const qsa = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

    const modal = qs('#productModal');
    const openBtn = qs('#openProductModal');
    const closeBtn = qs('#closeProductModal');
    const cancelBtn = qs('#cancelProductModal');
    const form = qs('#productFormModal-form');
    const statusEl = qs('#productFormStatus');

    const searchInput = qs('#productSearch');
    const categoryChips = qsa('#categoryChips .chip');
    const flagChips = qsa('#statusChips .chip');
    const tableRows = qsa('#productsTable tbody tr.product-row');
    const gridCards = qsa('#productsGrid .product-card');

    function setModal(open) {
        if (!modal) return;
        modal.setAttribute('aria-hidden', open ? 'false' : 'true');
    }

    function resetForm() {
        if (!form) return;
        form.reset();
        const title = qs('#productModalTitle');
        if (title) title.textContent = 'New Product';
        if (statusEl) statusEl.textContent = '';
    }

    function activeCategory() {
        const active = categoryChips.find(c => c.getAttribute('aria-pressed') === 'true');
        return active ? active.dataset.category || '' : '';
    }

    function activeFlag() {
        const active = flagChips.find(c => c.getAttribute('aria-pressed') === 'true');
        return active ? active.dataset.flag : 'all';
    }

    function matchFilters(el, query, category, flag) {
        const title = (el.dataset.title || '').toLowerCase();
        const sku = (el.dataset.sku || '').toLowerCase();
        const desc = (el.dataset.desc || '').toLowerCase();
        const cat = (el.dataset.category || '').toLowerCase();
        const featured = el.dataset.featured === 'true';
        const digital = el.dataset.digital === 'true';
        const discount = el.dataset.discount === 'true';

        const textMatch = !query || title.includes(query) || sku.includes(query) || desc.includes(query);
        const catMatch = !category || cat === category.toLowerCase();

        let flagMatch = true;
        if (flag === 'featured') flagMatch = featured;
        else if (flag === 'digital') flagMatch = digital;
        else if (flag === 'discount') flagMatch = discount;

        return textMatch && catMatch && flagMatch;
    }

    function applyFilters() {
        const query = (searchInput?.value || '').trim().toLowerCase();
        const category = activeCategory();
        const flag = activeFlag();

        const toggleVisibility = (node, show) => {
            if (!node) return;
            node.style.display = show ? '' : 'none';
        };

        tableRows.forEach(row => {
            const show = matchFilters(row, query, category, flag);
            toggleVisibility(row, show);
        });

        gridCards.forEach(card => {
            const show = matchFilters(card, query, category, flag);
            toggleVisibility(card, show);
        });
    }

    function wireChips(chips, callback) {
        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                chips.forEach(c => c.setAttribute('aria-pressed', 'false'));
                chip.setAttribute('aria-pressed', 'true');
                callback();
            });
        });
    }

    function wireAddToBill() {
        const buttons = qsa('.add-to-bill');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const title = btn.dataset.title;
                const price = btn.dataset.price;
                if (typeof addToBill === 'function') {
                    addToBill(title, price);
                }
            });
        });
    }

    function init() {
        if (openBtn) openBtn.addEventListener('click', () => { resetForm(); setModal(true); });
        if (closeBtn) closeBtn.addEventListener('click', () => setModal(false));
        if (cancelBtn) cancelBtn.addEventListener('click', () => setModal(false));
        if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) setModal(false); });

        if (searchInput) searchInput.addEventListener('input', applyFilters);
        wireChips(categoryChips, applyFilters);
        wireChips(flagChips, applyFilters);
        applyFilters();
        wireAddToBill();

        if (form) {
            form.addEventListener('submit', () => {
                if (statusEl) statusEl.textContent = 'Saving product...';
            });
        }

        // Automatically show the modal when server-side validation errors are present
        if (modal && modal.dataset.hasErrors === 'true') {
            setModal(true);
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
