/**
 * ============================================================
 * CREATE BILL - Multi-Bill Management
 * ============================================================
 * 
 * Handles multiple bill creation with dynamic tabs and AJAX saving
 */

'use strict';

let billCounter = 1;
let activeBill = 1;

// XSS Prevention
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add new bill tab
function addNewBill() {
    billCounter++;
    const billTabs = document.getElementById('billTabs');
    const formsContainer = document.getElementById('billFormsContainer');
    
    // Create new tab
    const newTab = document.createElement('div');
    newTab.className = 'bill-tab';
    newTab.setAttribute('data-bill', billCounter);
    newTab.onclick = () => switchBill(billCounter);
    newTab.innerHTML = `
        <span class="tab-number">#${billCounter}</span>
        <span>Bill ${billCounter}</span>
        <span class="close-tab" onclick="closeBill(event, ${billCounter})">×</span>
    `;
    billTabs.appendChild(newTab);
    
    // Clone first bill form
    const firstForm = document.querySelector('.bill-content[data-bill="1"]');
    const newForm = firstForm.cloneNode(true);
    newForm.setAttribute('data-bill', billCounter);
    newForm.classList.remove('active');
    
    // Reset form values
    const inputs = newForm.querySelectorAll('input:not([type="date"]), select');
    inputs.forEach(input => {
        if (input.type !== 'date') {
            input.value = '';
        }
    });
    
    // Keep only one item row
    const tbody = newForm.querySelector('.items-body');
    tbody.innerHTML = `
        <tr class="item-row">
            <td>1</td>
            <td><input type="text" class="item-title" placeholder="Item description" required></td>
            <td><input type="number" class="item-price" placeholder="0.00" step="0.01" min="0" value="0" oninput="calculateRowTotal(this)"></td>
            <td><input type="number" class="item-quantity" placeholder="1" min="1" value="1" oninput="calculateRowTotal(this)"></td>
            <td><input type="number" class="item-amount" placeholder="0.00" readonly style="background: #f1f5f9; font-weight: 600;"></td>
            <td>
                <button type="button" class="remove-item-btn" onclick="removeItem(this, ${billCounter})">
                    <span class="material-icons-sharp" style="font-size: 16px;">delete</span>
                    Remove
                </button>
            </td>
        </tr>
    `;
    
    newForm.querySelector('.bill-form').setAttribute('data-bill-number', billCounter);
    formsContainer.appendChild(newForm);
    
    switchBill(billCounter);
    updateSaveButton();
    showToast(`Bill ${billCounter} added`, 'success');
}

// Switch between bills
function switchBill(billNumber) {
    activeBill = billNumber;
    
    // Update tabs
    document.querySelectorAll('.bill-tab').forEach(tab => {
        tab.classList.remove('active');
        if (parseInt(tab.getAttribute('data-bill')) === billNumber) {
            tab.classList.add('active');
        }
    });
    
    // Update forms
    document.querySelectorAll('.bill-content').forEach(content => {
        content.classList.remove('active');
        if (parseInt(content.getAttribute('data-bill')) === billNumber) {
            content.classList.add('active');
        }
    });
}

// Close bill tab
function closeBill(event, billNumber) {
    event.stopPropagation();
    
    const allTabs = document.querySelectorAll('.bill-tab');
    if (allTabs.length <= 1) {
        showToast('Cannot close the last bill', 'error');
        return;
    }
    
    // Remove tab
    const tab = document.querySelector(`.bill-tab[data-bill="${billNumber}"]`);
    if (tab) tab.remove();
    
    // Remove form
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    if (form) form.remove();
    
    // Switch to first available bill if closed bill was active
    if (activeBill === billNumber) {
        const firstTab = document.querySelector('.bill-tab');
        if (firstTab) {
            switchBill(parseInt(firstTab.getAttribute('data-bill')));
        }
    }
    
    updateSaveButton();
    showToast(`Bill ${billNumber} removed`, 'success');
}

// Fill client data from select
function fillClientData(select, billNumber) {
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"] .bill-form`);
    if (!form) return;
    
    const selectedOption = select.options[select.selectedIndex];
    if (!selectedOption.value) {
        // Clear form if "New Client" selected
        form.querySelector('.clientName').value = '';
        form.querySelector('.phone').value = '';
        form.querySelector('.email').value = '';
        form.querySelector('.address').value = '';
        form.querySelector('.city').value = '';
        form.querySelector('.country').value = '';
        return;
    }
    
    form.querySelector('.clientName').value = selectedOption.getAttribute('data-name') || '';
    form.querySelector('.phone').value = selectedOption.getAttribute('data-phone') || '';
    form.querySelector('.email').value = selectedOption.getAttribute('data-email') || '';
    form.querySelector('.address').value = selectedOption.getAttribute('data-address') || '';
    form.querySelector('.city').value = selectedOption.getAttribute('data-city') || '';
    form.querySelector('.country').value = selectedOption.getAttribute('data-country') || '';
}

// Add item row
function addItem(billNumber) {
    const form = document.querySelector(`.bill-content[data-bill="${billNumber}"]`);
    const tbody = form.querySelector('.items-body');
    const rows = tbody.querySelectorAll('.item-row');
    const rowNumber = rows.length + 1;
    
    const newRow = document.createElement('tr');
    newRow.className = 'item-row';
    newRow.innerHTML = `
        <td>${rowNumber}</td>
        <td><input type="text" class="item-title" placeholder="Item description" required></td>
        <td><input type="number" class="item-price" placeholder="0.00" step="0.01" min="0" value="0" oninput="calculateRowTotal(this)"></td>
        <td><input type="number" class="item-quantity" placeholder="1" min="1" value="1" oninput="calculateRowTotal(this)"></td>
        <td><input type="number" class="item-amount" placeholder="0.00" readonly style="background: #f1f5f9; font-weight: 600;"></td>
        <td>
            <button type="button" class="remove-item-btn" onclick="removeItem(this, ${billNumber})">
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
    
    // Renumber rows
    tbody.querySelectorAll('.item-row').forEach((row, index) => {
        row.querySelector('td:first-child').textContent = index + 1;
    });
    
    updateBillSummary(billNumber);
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
    
    // Validate and collect all bills data
    for (let form of billForms) {
        const clientName = form.querySelector('.clientName').value.trim();
        const billDate = form.querySelector('.billDate').value;
        
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
            billDate,
            items
        });
    }
    
    // Show progress
    const progressIndicator = document.getElementById('progressIndicator');
    progressIndicator.classList.add('active');
    
    // Save bills sequentially
    let successCount = 0;
    const failedBills = [];
    
    for (let i = 0; i < billsData.length; i++) {
        const formData = new FormData();
        
        // Get CSRF token from multiple possible locations
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]');
        }
        const tokenValue = (csrfToken) ? csrfToken.value : window.CSRF_TOKEN;
        
        if (tokenValue) {
            formData.append('csrfmiddlewaretoken', tokenValue);
        }
        
        formData.append('clientName', billsData[i].clientName);
        formData.append('phone', billsData[i].phone);
        formData.append('email', billsData[i].email);
        formData.append('address', billsData[i].address);
        formData.append('city', billsData[i].city);
        formData.append('country', billsData[i].country);
        formData.append('billDate', billsData[i].billDate);
        formData.append('items_json', JSON.stringify(billsData[i].items));
        
        try {
            const response = await fetch(window.CREATE_BILL_URL, {
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
    // Calculate initial totals
    updateBillSummary(1);
    updateSaveButton();
});
