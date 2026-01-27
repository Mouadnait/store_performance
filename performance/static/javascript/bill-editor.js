/**
 * Professional Bill Editor
 * Allows editing bill items and adding products from catalog
 */

console.log('Bill editor loaded');

let currentBillData = {
    id: null,
    client: null,
    date: null,
    items: [],
    availableProducts: []
};

/**
 * Open the professional bill editor
 */
async function openBillEditor(billId) {
    console.log('Opening bill editor for bill:', billId);
    
    try {
        // Fetch bill data
        const response = await fetch(`/bill/${billId}/data/`);
        if (!response.ok) {
            alert('Failed to load bill data');
            return;
        }
        
        const data = await response.json();
        currentBillData = data;
        
        // Populate bill info
        document.getElementById('editBillId').textContent = `#${data.id}`;
        document.getElementById('editClientName').textContent = data.client_name || 'Unknown Client';
        document.getElementById('editBillDate').textContent = data.date || '-';
        
        // Load items
        loadBillItems();
        
        // Load available products
        loadAvailableProducts();
        
        // Show modal
        document.getElementById('editModal').style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Show items tab by default
        switchTab('items');
        
    } catch (error) {
        console.error('Error opening bill editor:', error);
        alert('Error loading bill data');
    }
}

/**
 * Close the bill editor
 */
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    currentBillData = { id: null, client: null, date: null, items: [], availableProducts: [] };
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    if (tabName === 'items') {
        document.getElementById('itemsTab').style.display = 'block';
    } else if (tabName === 'add') {
        document.getElementById('addTab').style.display = 'block';
    }
    
    // Add active class to clicked button
    const activeBtn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

/**
 * Load bill items into the table
 */
function loadBillItems() {
    const tbody = document.getElementById('editItemsBody');
    tbody.innerHTML = '';
    
    if (!currentBillData.items || currentBillData.items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center; padding:40px; color:#6c757d;">
                    <div style="font-size:3em; margin-bottom:12px;">📦</div>
                    <div style="font-size:1.1em; font-weight:600;">No items in this bill</div>
                    <div style="margin-top:8px; font-size:0.9em;">Click "Add Products" to get started</div>
                </td>
            </tr>
        `;
        updateTotal();
        return;
    }
    
    currentBillData.items.forEach((item, index) => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #e9ecef';
        row.innerHTML = `
            <td style="padding:12px;">
                <input type="text" value="${escapeHtml(item.description)}" 
                    onchange="updateItemField(${index}, 'description', this.value)"
                    style="width:100%; padding:8px; border:1px solid #e9ecef; border-radius:4px; font-size:0.95em;">
            </td>
            <td style="padding:12px;">
                <input type="number" value="${item.quantity}" step="0.01" min="0.01"
                    onchange="updateItemField(${index}, 'quantity', this.value)"
                    style="width:100%; padding:8px; border:1px solid #e9ecef; border-radius:4px; text-align:right; font-weight:600;">
            </td>
            <td style="padding:12px;">
                <input type="number" value="${item.price}" step="0.01" min="0"
                    onchange="updateItemField(${index}, 'price', this.value)"
                    style="width:100%; padding:8px; border:1px solid #e9ecef; border-radius:4px; text-align:right; font-weight:600;">
            </td>
            <td style="padding:12px; text-align:right; font-weight:700; color:#212529; font-size:1.05em;">
                $${(parseFloat(item.quantity) * parseFloat(item.price)).toFixed(2)}
            </td>
            <td style="padding:12px; text-align:center;">
                <button onclick="removeItem(${index})" 
                    style="background:#ef4444; color:white; border:none; padding:8px; border-radius:4px; cursor:pointer; transition:background 0.2s;"
                    title="Remove item">
                    <span class="material-icons-sharp" style="font-size:18px;">delete</span>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    updateTotal();
}

/**
 * Update a specific field of an item
 */
function updateItemField(index, field, value) {
    if (currentBillData.items[index]) {
        if (field === 'quantity' || field === 'price') {
            currentBillData.items[index][field] = parseFloat(value) || 0;
        } else {
            currentBillData.items[index][field] = value;
        }
        loadBillItems();
    }
}

/**
 * Remove an item from the bill
 */
function removeItem(index) {
    if (confirm('Remove this item from the bill?')) {
        currentBillData.items.splice(index, 1);
        loadBillItems();
    }
}

/**
 * Update the total display
 */
function updateTotal() {
    const total = currentBillData.items.reduce((sum, item) => {
        return sum + (parseFloat(item.quantity) * parseFloat(item.price));
    }, 0);
    
    document.getElementById('editTotalDisplay').textContent = `$${total.toFixed(2)}`;
}

/**
 * Load available products
 */
async function loadAvailableProducts() {
    try {
        const response = await fetch('/products/api/');
        if (!response.ok) {
            console.error('Failed to load products');
            return;
        }
        
        const data = await response.json();
        currentBillData.availableProducts = data.products || [];
        displayAvailableProducts();
        
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

/**
 * Display available products
 */
function displayAvailableProducts() {
    const container = document.getElementById('availableProductsList');
    
    if (!currentBillData.availableProducts || currentBillData.availableProducts.length === 0) {
        container.innerHTML = `
            <div style="grid-column:1/-1; text-align:center; padding:40px; color:#6c757d;">
                <div style="font-size:3em; margin-bottom:12px;">🏪</div>
                <div style="font-size:1.1em; font-weight:600;">No products available</div>
                <div style="margin-top:8px; font-size:0.9em;">Add products to your catalog first</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    currentBillData.availableProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card-mini';
        card.setAttribute('data-title', product.title.toLowerCase());
        card.innerHTML = `
            <img src="${product.image}" alt="${escapeHtml(product.title)}">
            <h4 title="${escapeHtml(product.title)}">${escapeHtml(truncate(product.title, 40))}</h4>
            <div class="price">$${parseFloat(product.price).toFixed(2)}</div>
            <button onclick="addProductToBill('${escapeHtml(product.title)}', ${product.price})">
                <span class="material-icons-sharp" style="font-size:18px; vertical-align:middle; margin-right:4px;">add</span>
                Add to Bill
            </button>
        `;
        container.appendChild(card);
    });
}

/**
 * Filter available products by search
 */
function filterAvailableProducts() {
    const search = document.getElementById('productSearch').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.product-card-mini');
    
    cards.forEach(card => {
        const title = card.getAttribute('data-title') || '';
        if (title.includes(search)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Add a product to the bill
 */
function addProductToBill(title, price) {
    // Check if product already exists
    const existing = currentBillData.items.find(item => item.description === title);
    
    if (existing) {
        // Increment quantity
        existing.quantity = parseFloat(existing.quantity) + 1;
    } else {
        // Add new item
        currentBillData.items.push({
            description: title,
            quantity: 1,
            price: parseFloat(price),
            isNew: true
        });
    }
    
    // Switch to items tab and refresh
    switchTab('items');
    loadBillItems();
    
    // Show feedback
    showToast(`${title} added to bill`);
}

/**
 * Save bill changes
 */
async function saveBillChanges() {
    if (!currentBillData.id) {
        alert('No bill selected');
        return;
    }
    
    if (currentBillData.items.length === 0) {
        alert('Bill must have at least one item');
        return;
    }
    
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch(`/bill/${currentBillData.id}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                items: currentBillData.items
            })
        });
        
        if (response.ok) {
            showToast('Bill updated successfully');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            const error = await response.text();
            alert('Failed to save changes: ' + error);
        }
        
    } catch (error) {
        console.error('Error saving bill:', error);
        alert('Error saving changes');
    }
}

/**
 * Utility: Show toast notification
 */
function showToast(message) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #10b981;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Utility: Truncate text
 */
function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100px); opacity: 0; }
    }
`;
document.head.appendChild(style);
