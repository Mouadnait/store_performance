/**
 * Client Bills Page JavaScript
 * Handles bill management, filtering, sorting, and editing
 */

console.log('client-bills.js loaded');

// ============================================================================
// MODAL MANAGEMENT
// ============================================================================

/**
 * Open edit modal with bill data
 */
function openEditModal(billId, desc, qty, price, amount, total) {
    console.log('Opening edit modal for bill:', billId);
    console.log('Bill data:', { billId, desc, qty, price, amount, total });
    
    document.getElementById('billId').value = billId;
    document.getElementById('editDescription').value = desc || '';
    document.getElementById('editQuantity').value = qty || 1;
    document.getElementById('editPrice').value = price || 0;
    document.getElementById('editAmount').value = parseFloat(amount || 0).toFixed(2);
    document.getElementById('editTotal').value = parseFloat(total || 0).toFixed(2);
    document.getElementById('editModal').classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Auto-focus on description if empty
    if (!desc) {
        setTimeout(() => document.getElementById('editDescription').focus(), 100);
    }
}

/**
 * Close edit modal
 */
function closeEditModal() {
    console.log('Closing edit modal');
    document.getElementById('editModal').classList.remove('show');
    document.body.style.overflow = 'auto';
}

/**
 * Calculate amount when quantity or price changes
 */
function calcAmount() {
    const qty = parseFloat(document.getElementById('editQuantity').value) || 0;
    const price = parseFloat(document.getElementById('editPrice').value) || 0;
    const amount = qty * price;
    
    document.getElementById('editAmount').value = amount.toFixed(2);
    document.getElementById('editTotal').value = amount.toFixed(2);
    
    console.log('Amount calculated:', amount);
}

// ============================================================================
// BILL ACTIONS
// ============================================================================

/**
 * Delete a bill with confirmation
 */
function deleteBill(billId) {
    if (!confirm('Are you sure you want to delete this bill? This action cannot be undone.')) {
        return;
    }
    
    console.log('Deleting bill:', billId);
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/core/bill/${billId}/delete/`;
    form.style.display = 'none';
    
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = token.value;
        form.appendChild(input);
    } else {
        console.warn('CSRF token not found');
    }
    
    document.body.appendChild(form);
    form.submit();
}

/**
 * Print a bill
 */
function printBill(billId) {
    if (!billId) {
        console.error('No bill ID provided');
        return;
    }
    console.log('Printing bill:', billId);
    window.location.href = `/core/bill/${billId}/print/`;
}

/**
 * Duplicate a bill
 */
function duplicateBill(billId) {
    if (!billId) {
        console.error('No bill ID provided');
        return;
    }
    
    if (!confirm('Duplicate this bill? A copy will be created with today\'s date.')) {
        return;
    }
    
    console.log('Duplicating bill:', billId);
    window.location.href = `/core/bill/${billId}/duplicate/`;
}

// ============================================================================
// FILTERING AND SORTING
// ============================================================================

/**
 * Filter and sort bills based on user inputs
 */
function filterAndSortBills() {
    const searchInput = document.getElementById('searchBills');
    const startInput = document.getElementById('startDate');
    const endInput = document.getElementById('endDate');
    const sortSelect = document.getElementById('sortBills');
    const resultsCount = document.getElementById('resultsCount');
    const filterState = document.getElementById('filterState');
    const filteredEmpty = document.getElementById('filteredEmpty');
    
    if (!searchInput || !sortSelect) return;
    
    const cards = Array.from(document.querySelectorAll('.bill-card'));
    const term = (searchInput.value || '').toLowerCase().trim();
    const start = startInput?.value ? new Date(startInput.value) : null;
    const end = endInput?.value ? new Date(endInput.value) : null;
    
    let visibleCards = [];

    cards.forEach(card => {
        const desc = (card.dataset.description || '').toLowerCase();
        const dateStr = card.dataset.date;
        const total = parseFloat(card.dataset.total || '0');
        const date = dateStr ? new Date(dateStr) : null;

        let isVisible = true;
        
        // Apply search filter
        if (term && !desc.includes(term)) {
            isVisible = false;
        }
        
        // Apply date range filters
        if (start && date && date < start) {
            isVisible = false;
        }
        if (end && date && date > end) {
            isVisible = false;
        }

        card.classList.toggle('hidden', !isVisible);
        if (isVisible) {
            visibleCards.push({ card, date, total });
        }
    });

    // Sort visible cards
    const sortMode = sortSelect.value || 'newest';
    const sorters = {
        newest: (a, b) => (b.date || 0) - (a.date || 0),
        oldest: (a, b) => (a.date || 0) - (b.date || 0),
        total_high: (a, b) => (b.total || 0) - (a.total || 0),
        total_low: (a, b) => (a.total || 0) - (b.total || 0),
    };
    
    visibleCards.sort(sorters[sortMode] || sorters.newest);
    visibleCards.forEach((item, idx) => {
        item.card.style.order = idx;
    });

    // Update UI with results
    const count = visibleCards.length;
    if (resultsCount) {
        resultsCount.textContent = `Showing ${count} bill${count === 1 ? '' : 's'}`;
    }
    
    if (filterState) {
        const active = [];
        if (term) active.push(`Search: "${term}"`);
        if (start) active.push(`From ${startInput.value}`);
        if (end) active.push(`To ${endInput.value}`);
        filterState.textContent = active.length ? active.join(' | ') : 'No filters';
    }
    
    if (filteredEmpty) {
        filteredEmpty.classList.toggle('hidden', count !== 0);
    }
    
    console.log(`Filtered: ${count} bills visible`);
}

/**
 * Clear all filters
 */
function clearFilters() {
    const searchInput = document.getElementById('searchBills');
    const startInput = document.getElementById('startDate');
    const endInput = document.getElementById('endDate');
    const sortSelect = document.getElementById('sortBills');
    
    if (searchInput) searchInput.value = '';
    if (startInput) startInput.value = '';
    if (endInput) endInput.value = '';
    if (sortSelect) sortSelect.value = 'newest';
    
    filterAndSortBills();
    console.log('Filters cleared');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Client bills page initialized');
    
    // Edit form quantity/price change listeners
    const qtyInput = document.getElementById('editQuantity');
    const priceInput = document.getElementById('editPrice');
    
    if (qtyInput) qtyInput.addEventListener('input', calcAmount);
    if (priceInput) priceInput.addEventListener('input', calcAmount);
    
    // Edit form submit
    const editForm = document.getElementById('editForm');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const billId = document.getElementById('billId').value;
            if (!billId) {
                e.preventDefault();
                console.error('No bill ID found');
                return;
            }
            this.action = `/core/bill/${billId}/edit/`;
            console.log('Submitting edit form for bill:', billId, 'to action:', this.action);
        });
    }
    
    // Filter and sort listeners
    const searchInput = document.getElementById('searchBills');
    const startInput = document.getElementById('startDate');
    const endInput = document.getElementById('endDate');
    const sortSelect = document.getElementById('sortBills');
    const clearBtn = document.getElementById('clearFilters');
    
    if (searchInput) searchInput.addEventListener('input', filterAndSortBills);
    if (startInput) startInput.addEventListener('change', filterAndSortBills);
    if (endInput) endInput.addEventListener('change', filterAndSortBills);
    if (sortSelect) sortSelect.addEventListener('change', filterAndSortBills);
    if (clearBtn) clearBtn.addEventListener('click', clearFilters);
    
    // Modal close on outside click
    const editModal = document.getElementById('editModal');
    window.addEventListener('click', function(e) {
        if (e.target === editModal) {
            closeEditModal();
        }
    });
    
    // Initial filter/sort
    filterAndSortBills();
    
    console.log('All event listeners registered');
});
