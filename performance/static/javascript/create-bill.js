// ========================================
// Store Performance - Create Bill JavaScript
// ========================================

// This file is for create-bill specific functionality
// Base functionality is in base.js

'use strict';

let billCounter = 1;
let activeBill = 1;
let billTemplate = null;
let productPickerModal = null;
let productPickerResults = null;
let productPickerSearch = null;
let productCatalog = [];
let pickerBillNumber = null;
let lastProductPickerTrigger = null;

function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }

    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function addNewBill(showToastMessage = true) {
    billCounter += 1;
    const billNumber = billCounter;

    createBillTab(billNumber);
    const billContent = instantiateBillForm(billNumber);

    if (billContent) {
        switchBill(billNumber);
        updateSaveButton();

        if (showToastMessage) {
            showToast(`Bill ${billNumber} added`, 'success');
        }
    }

    return billContent;
}

function createBillTab(billNumber) {
    const billTabs = document.getElementById('billTabs');
    if (!billTabs) {
        return null;
    }

    const tab = document.createElement('div');
    tab.className = 'bill-tab';
    tab.dataset.bill = billNumber;

    const numberBadge = document.createElement('span');
    numberBadge.className = 'tab-number';
    numberBadge.textContent = `#${billNumber}`;

    const label = document.createElement('span');
    label.textContent = `Bill ${billNumber}`;

    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'close-tab';
    closeButton.setAttribute('aria-label', `Close bill ${billNumber}`);
    closeButton.textContent = '×';
    closeButton.addEventListener('click', event => closeBill(billNumber, event));

    tab.append(numberBadge, label, closeButton);
    tab.addEventListener('click', () => switchBill(billNumber));

    billTabs.appendChild(tab);
    return tab;
}

function instantiateBillForm(billNumber) {
    if (!billTemplate) {
        billTemplate = document.getElementById('billFormTemplate');
    }

    if (!billTemplate) {
        console.warn('Bill form template not found');
        return null;
    }

    const formsContainer = document.getElementById('billFormsContainer');
    if (!formsContainer) {
        return null;
    }

    const fragment = billTemplate.content.cloneNode(true);
    const billContent = fragment.querySelector('.bill-content');
    const form = fragment.querySelector('.bill-form');
    const formNumber = fragment.querySelector('.bill-form-number');

    if (!billContent || !form) {
        return null;
    }

    billContent.dataset.bill = billNumber;
    form.setAttribute('data-bill-number', billNumber);

    if (formNumber) {
        formNumber.textContent = `#${billNumber}`;
    }

    formsContainer.appendChild(fragment);

    const appendedContent = formsContainer.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    const clientSelect = appendedContent ? appendedContent.querySelector('.clientSelect') : null;
    if (clientSelect) {
        clientSelect.value = '';
        fillClientData(clientSelect, billNumber);
    }

    insertItemRow(billNumber, null);
    return appendedContent || billContent;
}

function initializeBillBuilder() {
    const billTabs = document.getElementById('billTabs');
    const formsContainer = document.getElementById('billFormsContainer');

    if (billTabs) {
        billTabs.innerHTML = '';
    }

    if (formsContainer) {
        formsContainer.innerHTML = '';
    }

    billCounter = 0;
    activeBill = 0;
    addNewBill(false);
    updateSaveButton();
}

// Switch between bills
function switchBill(billNumber) {
    activeBill = billNumber;
    
    document.querySelectorAll('.bill-tab').forEach(tab => {
        tab.classList.remove('active');
        if (parseInt(tab.getAttribute('data-bill')) === billNumber) {
            tab.classList.add('active');
        }
    });
    
    document.querySelectorAll('.bill-content').forEach(content => {
        content.classList.remove('active');
        if (parseInt(content.getAttribute('data-bill')) === billNumber) {
            content.classList.add('active');
        }
    });
}

// Close bill tab
function closeBill(billNumber, event = null) {
    if (event) {
        event.stopPropagation();
    }

    const allTabs = document.querySelectorAll('.bill-tab');
    if (allTabs.length <= 1) {
        showToast('Cannot close the last bill', 'error');
        return;
    }
    
    const tab = document.querySelector(`.bill-tab[data-bill="${billNumber}"]`);
    let fallbackTab = null;
    if (tab) {
        fallbackTab = tab.nextElementSibling || tab.previousElementSibling;
        tab.remove();
    }
    
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    if (form) {
        form.remove();
    }
    
    if (activeBill === billNumber) {
        const nextTab = fallbackTab || document.querySelector('.bill-tab');
        if (nextTab) {
            const nextBill = parseInt(nextTab.getAttribute('data-bill'));
            switchBill(nextBill);
        }
    }

    updateSaveButton();
    showToast(`Bill ${billNumber} closed`, 'success');
}

// Fill client data from select
function fillClientData(select, billNumber) {
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"] .bill-form`);
    if (!form) return;
    
    const selectedOption = select.options[select.selectedIndex];
    if (!selectedOption.value) {
        form.querySelector('.clientName').value = '';
        form.querySelector('.phone').value = '';
        form.querySelector('.email').value = '';
        form.querySelector('.address').value = '';
        form.querySelector('.city').value = '';
        form.querySelector('.country').value = '';
        const postalField = form.querySelector('.postal');
        if (postalField) {
            postalField.value = '';
        }
        return;
    }
    
    form.querySelector('.clientName').value = selectedOption.getAttribute('data-name') || '';
    form.querySelector('.phone').value = selectedOption.getAttribute('data-phone') || '';
    form.querySelector('.email').value = selectedOption.getAttribute('data-email') || '';
    form.querySelector('.address').value = selectedOption.getAttribute('data-address') || '';
    form.querySelector('.city').value = selectedOption.getAttribute('data-city') || '';
    form.querySelector('.country').value = selectedOption.getAttribute('data-country') || '';
    const postalField = form.querySelector('.postal');
    if (postalField) {
        postalField.value = selectedOption.getAttribute('data-postal') || '';
    }
}

// Add item row
function addItem(billNumber) {
    lastProductPickerTrigger = document.activeElement;
    pickerBillNumber = billNumber;
    openProductPicker();
}

function insertItemRow(billNumber, product) {
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    if (!form) {
        return;
    }

    const tbody = form.querySelector('.items-body');
    const rows = tbody.querySelectorAll('.item-row');
    const rowNumber = rows.length + 1;
    const priceValue = product ? parseFloat(product.price) || 0 : 0;
    const quantityValue = 1;
    const amountValue = priceValue * quantityValue;
    const titleValue = product ? escapeHtml(product.title) : '';

    const newRow = document.createElement('tr');
    newRow.className = 'item-row';
    newRow.innerHTML = `
        <td>${rowNumber}</td>
        <td><input type="text" class="item-title" placeholder="Item description" value="${titleValue}" required></td>
        <td><input type="number" class="item-price" placeholder="0.00" step="0.01" min="0" value="${priceValue.toFixed(2)}" oninput="calculateRowTotal(this)"></td>
        <td><input type="number" class="item-quantity" placeholder="1" min="1" value="${quantityValue}" oninput="calculateRowTotal(this)"></td>
        <td><input type="number" class="item-amount item-amount-readonly" placeholder="0.00" readonly value="${amountValue.toFixed(2)}"></td>
        <td>
            <button type="button" class="remove-item-btn">
                <span class="material-icons-sharp" style="font-size: 16px;">delete</span>
                Remove
            </button>
        </td>
    `;

    tbody.appendChild(newRow);
    updateBillSummary(billNumber);
}

// Remove item row
function removeItem(button, billNumber) {
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    const tbody = form.querySelector('.items-body');
    const rows = tbody.querySelectorAll('.item-row');
    
    if (rows.length <= 1) {
        showToast('At least one item is required', 'error');
        return;
    }
    
    button.closest('tr').remove();
    
    tbody.querySelectorAll('.item-row').forEach((row, index) => {
        row.querySelector('td:first-child').textContent = index + 1;
    });
    
    updateBillSummary(billNumber);
    showToast('Item removed', 'success');
}

// Calculate row total
function calculateRowTotal(input) {
    const row = input.closest('tr');
    const price = parseFloat(row.querySelector('.item-price').value) || 0;
    const quantity = parseFloat(row.querySelector('.item-quantity').value) || 0;
    const amount = price * quantity;
    
    row.querySelector('.item-amount').value = amount.toFixed(2);
    
    const billNumber = parseInt(input.closest('.bill-content').getAttribute('data-bill'));
    updateBillSummary(billNumber);
}

// Update bill summary
function updateBillSummary(billNumber) {
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    if (!form) return;
    
    const rows = form.querySelectorAll('.item-row');
    
    let totalItems = rows.length;
    let totalQuantity = 0;
    let totalAmount = 0;
    
    rows.forEach(row => {
        const quantity = parseFloat(row.querySelector('.item-quantity').value) || 0;
        const amount = parseFloat(row.querySelector('.item-amount').value) || 0;
        totalQuantity += quantity;
        totalAmount += amount;
    });
    
    form.querySelector('.total-items').textContent = totalItems;
    form.querySelector('.total-quantity').textContent = totalQuantity;
    form.querySelector('.total-amount').textContent = `$${totalAmount.toFixed(2)}`;
}

// Update save button text
function updateSaveButton() {
    const billCount = document.querySelectorAll('.bill-tab').length;
    const saveBtn = document.querySelector('.save-all-btn');
    if (saveBtn) {
        saveBtn.innerHTML = `
            <span class="material-icons-sharp">save</span>
            Save All Bills (${billCount})
        `;
    }
}

// Save all bills
async function saveAllBills() {
    const billForms = document.querySelectorAll('.bill-form');
    const billsData = [];
    
    for (let form of billForms) {
        const clientName = form.querySelector('.clientName').value.trim();
        const billDate = form.querySelector('.billDate').value;
        const postalInput = form.querySelector('.postal');
        const postalCode = postalInput ? postalInput.value.trim() : '';
        
        if (!clientName) {
            showToast('Please fill client name in all bills', 'error');
            return;
        }
        
        const items = [];
        const rows = form.querySelectorAll('.item-row');
        
        for (let row of rows) {
            const title = row.querySelector('.item-title').value.trim();
            const price = parseFloat(row.querySelector('.item-price').value) || 0;
            const quantity = parseFloat(row.querySelector('.item-quantity').value) || 0;
            
            if (title && price >= 0 && quantity > 0) {
                items.push({ title, price, quantity });
            }
        }
        
        if (items.length === 0) {
            showToast('Each bill must have at least one item', 'error');
            return;
        }
        
        billsData.push({
            clientName,
            phone: form.querySelector('.phone').value.trim(),
            email: form.querySelector('.email').value.trim(),
            address: form.querySelector('.address').value.trim(),
            city: form.querySelector('.city').value.trim(),
            country: form.querySelector('.country').value.trim(),
            postal: postalCode,
            billDate,
            items
        });
    }
    
    const progressIndicator = document.getElementById('progressIndicator');
    progressIndicator.classList.add('active');
    
    let successCount = 0;
    const failedBills = [];
    
    for (let i = 0; i < billsData.length; i++) {
        const formData = new FormData();
        
        // Get CSRF token from multiple possible locations
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]');
        }
        
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }
        
        formData.append('clientName', billsData[i].clientName);
        formData.append('phone', billsData[i].phone);
        formData.append('email', billsData[i].email);
        formData.append('address', billsData[i].address);
        formData.append('city', billsData[i].city);
        formData.append('country', billsData[i].country);
        formData.append('postal_code', billsData[i].postal);
        formData.append('billDate', billsData[i].billDate);
        formData.append('items_json', JSON.stringify(billsData[i].items));
        
        try {
            const response = await fetch('/create-bill/', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data && data.success) {
                    successCount++;
                } else {
                    failedBills.push({ num: i + 1, error: data.error || 'Unknown error' });
                }
            } else {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                failedBills.push({ num: i + 1, error: errorData.error || response.statusText });
            }
        } catch (error) {
            console.error('Error saving bill:', error);
            failedBills.push({ num: i + 1, error: error.message });
        }
    }
    
    progressIndicator.classList.remove('active');
    
    if (successCount === billsData.length) {
        showToast(`Successfully saved all ${successCount} bills!`, 'success');
        setTimeout(() => { window.location.reload(); }, 1500);
    } else if (successCount > 0) {
        const failedNums = failedBills.map(b => `#${b.num}`).join(', ');
        showToast(`Saved ${successCount}/${billsData.length} bills. Failed: ${failedNums}`, 'error');
    } else {
        showToast(`All bills failed to save. Please check and try again.`, 'error');
    }
}

function parseProductCatalog() {
    const script = document.getElementById('product-options-data');
    if (!script) {
        return [];
    }

    try {
        return JSON.parse(script.textContent || '[]');
    } catch (error) {
        console.error('Failed to parse product data', error);
        return [];
    }
}

function openProductPicker() {
    if (!productPickerModal) {
        return;
    }

    productPickerModal.classList.add('open');
    productPickerModal.setAttribute('aria-hidden', 'false');

    if (productPickerResults) {
        renderProductResults(productCatalog);
    }

    if (productPickerSearch) {
        productPickerSearch.value = '';
        setTimeout(() => productPickerSearch.focus(), 100);
    }
}

function closeProductPicker() {
    if (!productPickerModal) {
        return;
    }

    if (document.activeElement && productPickerModal.contains(document.activeElement)) {
        document.activeElement.blur();
    }

    if (lastProductPickerTrigger && typeof lastProductPickerTrigger.focus === 'function') {
        lastProductPickerTrigger.focus();
    }

    productPickerModal.classList.remove('open');
    productPickerModal.setAttribute('aria-hidden', 'true');
    pickerBillNumber = null;
    lastProductPickerTrigger = null;
}

function renderProductResults(products) {
    if (!productPickerResults) {
        return;
    }

    productPickerResults.innerHTML = '';

    if (!products || products.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'product-card-empty';
        const fallback = productPickerResults.getAttribute('data-empty-message') || 'No products available.';
        emptyMessage.textContent = fallback;
        productPickerResults.appendChild(emptyMessage);
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'product-grid';

    products.forEach(product => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'product-card';
        const priceNumber = parseFloat(product.price) || 0;
        const price = priceNumber.toFixed(2);
        const category = product.category ? escapeHtml(product.category) : 'Uncategorized';
        const sku = product.sku ? escapeHtml(product.sku) : 'N/A';

        button.innerHTML = `
            <div>
                <h3>${escapeHtml(product.title)}</h3>
                <div class="product-code">SKU: ${sku}</div>
            </div>
            <div class="product-meta">
                <span class="product-price">$${price}</span>
                <span class="product-category">${category}</span>
            </div>
        `;

        button.addEventListener('click', () => handleProductSelection(product));
        grid.appendChild(button);
    });

    productPickerResults.appendChild(grid);
}

function handleProductSelection(product) {
    if (!pickerBillNumber) {
        return;
    }
    insertItemRow(pickerBillNumber, product);
    showToast(`${product.title} added to bill`, 'success');
    closeProductPicker();
}

function addManualItem() {
    if (!pickerBillNumber) {
        return;
    }
    insertItemRow(pickerBillNumber, null);
    showToast('Manual item added', 'success');
    closeProductPicker();
}

function filterProducts(query) {
    if (!query) {
        return productCatalog;
    }

    const term = query.toLowerCase();
    return productCatalog.filter(product => {
        const haystack = [
            product.title,
            product.description,
            product.category,
            product.sku
        ].filter(value => value !== null && value !== undefined)
            .map(value => String(value).toLowerCase())
            .join(' ');
        return haystack.includes(term);
    });
}

function setupProductPicker() {
    productPickerModal = document.getElementById('productPickerModal');
    productPickerResults = document.getElementById('productPickerResults');
    productPickerSearch = document.getElementById('productPickerSearch');
    productCatalog = parseProductCatalog();

    if (productPickerSearch) {
        productPickerSearch.addEventListener('input', event => {
            const results = filterProducts(event.target.value.trim());
            renderProductResults(results);
        });
    }

    if (productPickerModal) {
        productPickerModal.addEventListener('keydown', event => {
            if (event.key === 'Escape') {
                closeProductPicker();
            }
        });
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = toast.querySelector('.material-icons-sharp');
    const messageEl = toast.querySelector('.toast-message');
    
    toast.className = `toast ${type}`;
    messageEl.textContent = message;
    
    if (type === 'success') {
        icon.textContent = 'check_circle';
    } else {
        icon.textContent = 'error';
    }
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('billFormTemplate')) {
        return;
    }

    setupProductPicker();
    initializeBillBuilder();
});

document.addEventListener('click', event => {
    const addButton = event.target.closest('.add-item-btn');
    if (addButton) {
        const container = addButton.closest('.bill-content');
        if (container) {
            const billNumber = parseInt(container.getAttribute('data-bill'));
            addItem(billNumber);
        }
        return;
    }

    const removeButton = event.target.closest('.remove-item-btn');
    if (removeButton) {
        const container = removeButton.closest('.bill-content');
        if (container) {
            const billNumber = parseInt(container.getAttribute('data-bill'));
            removeItem(removeButton, billNumber);
        }
    }
});

document.addEventListener('change', event => {
    if (!(event.target instanceof HTMLSelectElement)) {
        return;
    }

    if (!event.target.classList.contains('clientSelect')) {
        return;
    }

    const container = event.target.closest('.bill-content');
    if (!container) {
        return;
    }

    const billNumber = parseInt(container.getAttribute('data-bill'));
    fillClientData(event.target, billNumber);
});
