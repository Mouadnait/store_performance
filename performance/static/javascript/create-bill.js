console.log('create-bill.js file loaded successfully');

/**
 * Load and display bill items from localStorage
 * @function
 */
function loadBillItems() {
    try {
        const products = JSON.parse(localStorage.getItem('billProducts')) || [];
        const billBody = document.querySelector('.bill-table tbody');

        if (!billBody) {
            console.warn('Bill table body not found in DOM');
            return;
        }

        // Rebuild tbody each time to avoid stale DOM and force live updates
        billBody.innerHTML = '';

        let grandTotal = 0;

        if (!products || products.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.classList.add('bill-empty-row');
            emptyRow.innerHTML = '<td colspan="5" class="bill-empty-message">No products added yet. Click "Add to Bill" on any product above.</td>';
            billBody.appendChild(emptyRow);
        } else {
            products.forEach((product, index) => {
                const row = document.createElement('tr');
                const quantity = parseFloat(product.quantity) || 0;
                const price = parseFloat(product.price) || 0;
                const amount = (price * quantity).toFixed(2);
                
                row.innerHTML = `
                    <td><input type="number" class="quantity-input" data-index="${index}" value="${quantity}" step="0.01" min="0.01" required></td>
                    <td><input type="text" class="description-input" data-index="${index}" value="${escapeHtml(product.title || '')}" readonly style="cursor: default;"></td>
                    <td><input type="number" class="price-input" data-index="${index}" value="${price.toFixed(2)}" step="0.01" readonly style="cursor: default;"></td>
                    <td><input type="number" class="amount-input" data-index="${index}" value="${amount}" step="0.01" readonly style="cursor: default;"></td>
                    <td><button type="button" class="delete-btn" data-index="${index}" style="background:#ff6b6b; color:white; padding:5px 10px; border:none; border-radius:4px; cursor:pointer;">Remove</button></td>
                `;
                billBody.appendChild(row);
                grandTotal += price * quantity;
            });

            // Attach event listeners to delete buttons
            billBody.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    const idx = parseInt(button.getAttribute('data-index'), 10);
                    if (!isNaN(idx) && idx >= 0 && idx < products.length) {
                        products.splice(idx, 1);
                        localStorage.setItem('billProducts', JSON.stringify(products));
                        loadBillItems();
                        updateBillCounter();
                    }
                });
            });

            // Attach event listeners to quantity inputs
            billBody.querySelectorAll('.quantity-input').forEach(input => {
                input.addEventListener('change', () => {
                    const idx = parseInt(input.getAttribute('data-index'), 10);
                    const newQty = parseFloat(input.value) || 0;
                    
                    if (!isNaN(idx) && idx >= 0 && idx < products.length) {
                        if (newQty > 0) {
                            products[idx].quantity = newQty;
                            localStorage.setItem('billProducts', JSON.stringify(products));
                            loadBillItems();
                            updateBillCounter();
                        } else {
                            input.value = products[idx].quantity;
                            showToast('Quantity must be greater than 0');
                        }
                    }
                });
            });
        }

        // Add total row
        const totalRow = document.createElement('tr');
        totalRow.classList.add('bill-total-row');
        totalRow.innerHTML = '<td colspan="3" class="text-right"><strong>Gr. Total:</strong></td><td colspan="2"><input type="number" name="totalPrice" id="totalPrice" placeholder="0.00" step="0.01" readonly></td>';
        billBody.appendChild(totalRow);

        const totalInput = totalRow.querySelector('#totalPrice');
        if (totalInput) {
            totalInput.value = grandTotal.toFixed(2);
        }
    } catch (error) {
        console.error('Error loading bill items:', error);
        showToast('Error loading bill items. Please refresh the page.');
    }
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, error, info)
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 10000;
        animation: slideIn 0.3s ease-in;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

/**
 * Update bill counter display
 * @function
 */
function updateBillCounter() {
    try {
        const products = JSON.parse(localStorage.getItem('billProducts')) || [];
        const counter = document.getElementById('billCounter');
        if (counter) {
            counter.textContent = products.length;
        }
    } catch (error) {
        console.error('Error updating bill counter:', error);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        loadBillItems();
        updateBillCounter();
        
        // Set today's date on the bill date field if present
        const billDate = document.getElementById('billDate');
        if (billDate && !billDate.value) {
            const today = new Date().toISOString().split('T')[0];
            billDate.value = today;
        }
    } catch (error) {
        console.error('DOMContentLoaded error:', error);
    }
});


/**
 * Handle client selection and auto-populate fields
 * @function
 */
function handleClientSelection() {
    try {
        const selectElement = document.getElementById('clientSelect');
        if (!selectElement) {
            console.warn('Client select element not found');
            return;
        }
        
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const clientDetailsSection = document.getElementById('clientDetailsSection');
        const indicator = document.getElementById('clientModeIndicator');
        
        if (!selectedOption.value) {
            // Create new client - show all fields as editable
            if (indicator) {
                indicator.innerHTML = '<span class="material-icons-sharp" style="font-size: 16px; vertical-align: middle; color: #4CAF50;">person_add</span> Creating new client - fill in the details below';
                indicator.style.color = '#4CAF50';
            }
            
            resetClientForm();
            setFieldsEditable(true);
        } else {
            // Existing client selected - populate and make fields readonly
            const name = selectedOption.getAttribute('data-name') || '';
            const phone = selectedOption.getAttribute('data-phone') || '';
            const email = selectedOption.getAttribute('data-email') || '';
            const address = selectedOption.getAttribute('data-address') || '';
            const city = selectedOption.getAttribute('data-city') || '';
            const country = selectedOption.getAttribute('data-country') || '';
            const postal = selectedOption.getAttribute('data-postal') || '';
            
            if (indicator) {
                indicator.innerHTML = '<span class="material-icons-sharp" style="font-size: 16px; vertical-align: middle; color: #2196F3;">person</span> Using existing client - information is pre-filled';
                indicator.style.color = '#2196F3';
            }
            
            // Populate fields safely
            const fields = {
                'clientName': escapeHtml(name),
                'phone': escapeHtml(phone),
                'email': escapeHtml(email),
                'address': escapeHtml(address),
                'city': escapeHtml(city),
                'country': escapeHtml(country),
                'postal_code': escapeHtml(postal)
            };
            
            Object.keys(fields).forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    el.value = fields[id];
                    el.readOnly = true;
                    el.style.backgroundColor = '#f5f5f5';
                }
            });
            
            setFieldsEditable(false);
        }
    } catch (error) {
        console.error('Error in handleClientSelection:', error);
        showToast('Error selecting client. Please try again.', 'error');
    }
}

/**
 * Reset client form fields
 * @function
 */
function resetClientForm() {
    const fieldIds = ['clientName', 'phone', 'email', 'address', 'city', 'country', 'postal_code'];
    fieldIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.value = '';
            el.style.backgroundColor = '';
        }
    });
    
    const indicator = document.getElementById('clientModeIndicator');
    if (indicator) {
        indicator.innerHTML = '<span class="material-icons-sharp" style="font-size: 16px; vertical-align: middle;">info</span> Select an existing client or create a new one';
        indicator.style.color = '#666';
    }
    
    const selectElement = document.getElementById('clientSelect');
    if (selectElement) {
        selectElement.value = '';
    }
}

/**
 * Set form fields editable or readonly
 * @param {boolean} editable - Whether fields should be editable
 */
function setFieldsEditable(editable) {
    const fieldIds = ['clientName', 'phone', 'email', 'address', 'city', 'country', 'postal_code'];
    fieldIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.readOnly = !editable;
            el.style.backgroundColor = editable ? '' : '#f5f5f5';
        }
    });
}
        
        const cityField = document.getElementById('city');
        const countryField = document.getElementById('country');
        const postalField = document.getElementById('postal_code');
        if (cityField) cityField.value = city;
        if (countryField) countryField.value = country;
        if (postalField) postalField.value = postal;
        
        // Make fields readonly and style them
        document.getElementById('clientName').readOnly = true;
        document.getElementById('phone').readOnly = true;
        document.getElementById('email').readOnly = true;
        document.getElementById('address').readOnly = true;
        
        document.getElementById('clientName').style.backgroundColor = '#f0f0f0';
        document.getElementById('phone').style.backgroundColor = '#f0f0f0';
        document.getElementById('email').style.backgroundColor = '#f0f0f0';
        document.getElementById('address').style.backgroundColor = '#f0f0f0';
        
        if (cityField) {
            cityField.readOnly = true;
            cityField.style.backgroundColor = '#f0f0f0';
        }
        if (countryField) {
            countryField.readOnly = true;
            countryField.style.backgroundColor = '#f0f0f0';
        }
        if (postalField) {
            postalField.readOnly = true;
            postalField.style.backgroundColor = '#f0f0f0';
        }
    }
}

// Make handleClientSelection available globally
window.handleClientSelection = handleClientSelection;

// Function To Clear the Bill
const clearBillBtn = document.getElementById('clear-bill-btn');
if (clearBillBtn) {
    clearBillBtn.addEventListener('click', clearBill);
}
function clearBill() {
    // Clear the products from local storage
    localStorage.removeItem('billProducts');

    // Reset client selection
    const clientSelect = document.getElementById('clientSelect');
    if (clientSelect) {
        clientSelect.value = '';
    }
    
    // Reset indicator
    const indicator = document.getElementById('clientModeIndicator');
    if (indicator) {
        indicator.innerHTML = '<span class="material-icons-sharp" style="font-size: 16px; vertical-align: middle;">info</span> Select an existing client or create a new one';
        indicator.style.color = '#666';
    }

    // Reset all form fields
    document.getElementById('clientName').value = '';
    document.getElementById('clientName').readOnly = false;
    document.getElementById('clientName').style.backgroundColor = '';
    
    document.getElementById('phone').value = '';
    document.getElementById('phone').readOnly = false;
    document.getElementById('phone').style.backgroundColor = '';
    
    document.getElementById('email').value = '';
    document.getElementById('email').readOnly = false;
    document.getElementById('email').style.backgroundColor = '';
    
    document.getElementById('address').value = '';
    document.getElementById('address').readOnly = false;
    document.getElementById('address').style.backgroundColor = '';
    
    const cityField = document.getElementById('city');
    const countryField = document.getElementById('country');
    const postalField = document.getElementById('postal_code');
    
    if (cityField) {
        cityField.value = '';
        cityField.readOnly = false;
        cityField.style.backgroundColor = '';
    }
    if (countryField) {
        countryField.value = '';
        countryField.readOnly = false;
        countryField.style.backgroundColor = '';
    }
    if (postalField) {
        postalField.value = '';
        postalField.readOnly = false;
        postalField.style.backgroundColor = '';
    }
    
    // Reset grand total
    let grandTotalInput = document.getElementById('totalPrice');
    if (grandTotalInput) {
        grandTotalInput.value = '0.00';
    }

    // Reload bill items to reflect the changes
    loadBillItems();
}

// Function To Save the Bill for each client
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, setting up form handler');
    const billForm = document.getElementById('bill-form');
    
    // Only proceed if form exists on this page
    if (!billForm) {
        console.log('Bill form not found on this page - skipping initialization');
        return;
    }
    
    console.log('Bill form found:', billForm);
    billForm.addEventListener('submit', function (e) {
        console.log('Form submit triggered');
        const clientName = document.getElementById('clientName').value;
        const billDate = document.getElementById('billDate').value;
        
        console.log('Client name:', clientName);
        console.log('Bill date:', billDate);
        
        if (!clientName) {
            e.preventDefault();
            alert('Please enter client name');
            return;
        }
        
        if (!billDate) {
            e.preventDefault();
            alert('Please select bill date');
            return;
        }
        
        // Get products from localStorage
        const products = JSON.parse(localStorage.getItem('billProducts')) || [];
        
        if (products.length === 0) {
            e.preventDefault();
            alert('Please add at least one product to the bill');
            return;
        }
        
        console.log('Products to submit:', products);
        console.log('Total products:', products.length);
        
        // Prepare a single bill with multiple items (sent as JSON)
        const totalAmount = products.reduce((sum, product) => sum + (product.price * product.quantity), 0);
        const totalQuantity = products.reduce((sum, product) => sum + Number(product.quantity), 0);
        const descriptionSummary = products.map(p => p.title).join(', ');

        const descriptionInput = document.getElementById('description');
        const quantityInput = document.getElementById('quantity');
        const priceInput = document.getElementById('price');
        const amountInput = document.getElementById('amount');
        const totalPriceInput = document.getElementById('totalPrice');
        const itemsJsonInput = document.getElementById('items_json');

        if (descriptionInput) descriptionInput.value = descriptionSummary;
        if (quantityInput) quantityInput.value = totalQuantity.toFixed(2);
        if (priceInput) priceInput.value = products.length === 1 ? parseFloat(products[0].price).toFixed(2) : '0.00';
        if (amountInput) amountInput.value = totalAmount.toFixed(2);
        if (totalPriceInput) totalPriceInput.value = totalAmount.toFixed(2);
        if (itemsJsonInput) itemsJsonInput.value = JSON.stringify(products);

        // Allow normal form submission to carry the payload
        console.log('Prepared multi-item bill payload, submitting form normally');

        // Clear local storage so the builder resets on next visit
        localStorage.removeItem('billProducts');
        updateBillCounter();
    });
});

// Add Product Form
function toggleProductForm() {
    var form = document.getElementById("productForm");
    if (form.style.display === "none" || form.style.display === "") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

const productSearchInput = document.getElementById("myInput");
if (productSearchInput) {
    productSearchInput.addEventListener("keyup", function () {
        var input, filter, cards, title, i, txtValue;
        input = document.getElementById("myInput");
        filter = input.value.toUpperCase();
        cards = document.getElementsByClassName("product-card");

        // Loop through all product cards, and hide those who don't match the search query
        for (i = 0; i < cards.length; i++) {
            title = cards[i].getElementsByTagName("h2")[0];
            txtValue = title.textContent || title.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                cards[i].style.display = "";
            } else {
                cards[i].style.display = "none";
            }
        }
    });
}

function addToBill(productTitle, productPrice) {
    console.log('addToBill called:', productTitle, productPrice);
    
    // Ensure price is a valid number
    let price = parseFloat(productPrice);
    if (isNaN(price)) {
        alert('Invalid product price');
        return;
    }

    // Check if user is on create-bill page or products page
    const isCreateBillPage = document.getElementById('bills-container') !== null;
    
    if (isCreateBillPage) {
        // If on create-bill page, add to selected bill directly
        addItemToSelectedBill(productTitle, price);
    } else {
        // If on products page, show bill selector or save to localStorage
        showBillSelector(productTitle, price);
    }
}

function addItemToSelectedBill(productTitle, price) {
    const selectedBillNum = window.selectedBillForProducts || 1;
    const billContent = document.getElementById(`bill-${selectedBillNum}`);
    
    if (!billContent) {
        showBillToast('Bill not found');
        return;
    }
    
    // Add a new item row
    const itemsBody = billContent.querySelector('.items-body');
    const newRow = itemsBody.querySelector('.item-row').cloneNode(true);
    
    // Fill in the product details
    newRow.querySelector('.item-quantity').value = 1;
    newRow.querySelector('.item-description').value = productTitle;
    newRow.querySelector('.item-price').value = price.toFixed(2);
    newRow.querySelector('.item-amount').value = (price * 1).toFixed(2);
    
    itemsBody.appendChild(newRow);
    
    // Update the bill total
    updateBillTotalById(`bill-${selectedBillNum}`);
    
    // Scroll to the new item
    billContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    showBillToast(`${productTitle} added to Bill #${selectedBillNum}`);
}

function showBillSelector(productTitle, price) {
    // Create a temporary storage for the product
    let product = { 
        title: productTitle, 
        price: price, 
        quantity: 1 
    };

    // Retrieve existing products from local storage
    let products = JSON.parse(localStorage.getItem('billProducts')) || [];

    // Check if the product already exists
    let existingProduct = products.find(p => p.title === productTitle);
    if (existingProduct) {
        existingProduct.quantity += 1;
        showBillToast(`${productTitle} quantity updated (${existingProduct.quantity})`);
    } else {
        products.push(product);
        showBillToast(`${productTitle} added to bill`);
    }

    // Save the updated products array back to local storage
    localStorage.setItem('billProducts', JSON.stringify(products));
    console.log('Products saved to localStorage:', products);

    // Update the bill counter badge
    updateBillCounter();
    
    // Auto-open the modal to show the bill
    const modal = document.getElementById('billBuilderModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        console.log('Bill builder modal opened automatically');
    }
    
    console.log('Bill items reloaded and counter updated');
}

let billToastTimeout;
function showBillToast(message) {
    console.log('showBillToast called with:', message);
    const toast = document.getElementById('bill-toast');
    console.log('Toast element:', toast);
    
    if (!toast) {
        console.error('Toast element not found!');
        return;
    }

    toast.textContent = message;
    toast.style.display = 'block';
    toast.classList.add('show');
    // Force a reflow to ensure the animation triggers
    void toast.offsetWidth;
    console.log('Toast displayed');

    if (billToastTimeout) {
        clearTimeout(billToastTimeout);
    }

    billToastTimeout = setTimeout(() => {
        toast.classList.remove('show');
        console.log('Toast hiding');
        // Hide after animation
        setTimeout(() => {
            toast.style.display = 'none';
        }, 300);
    }, 2000);
}

// Update bill counter badge
function updateBillCounter() {
    const products = JSON.parse(localStorage.getItem('billProducts')) || [];
    const totalItems = products.reduce((sum, product) => sum + product.quantity, 0);
    const badge = document.getElementById('bill-counter-badge');
    
    if (badge) {
        if (totalItems > 0) {
            badge.textContent = totalItems;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Filter Orders
document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to filter inputs, if present
    const filterInputs = document.querySelectorAll('.custom-control-input');
    const priceRange = document.querySelector('.form-control-range');

    if (filterInputs.length && priceRange) {
        filterInputs.forEach(input => input.addEventListener('change', filterProducts));
        priceRange.addEventListener('input', filterProducts);
    }

    function filterProducts() {
        const selectedCategories = getSelectedCategories();
        const selectedPriceRange = getPriceRange();
        const products = document.querySelectorAll('.product-card'); // Assuming product cards have a class 'product-card'

        products.forEach(product => {
            const categories = (product.getAttribute('data-categories') || '').split(','); // Assuming product cards have a 'data-categories' attribute
            const price = parseInt(product.getAttribute('data-price') || '0', 10); // Assuming product cards have a 'data-price' attribute

            const isCategoryMatch = categories.some(category => selectedCategories.includes(category));
            const isPriceMatch = price >= selectedPriceRange.min && price <= selectedPriceRange.max;

            if (isCategoryMatch && isPriceMatch) {
                product.style.display = '';
            } else {
                product.style.display = 'none';
            }
        });
    }

    function getSelectedCategories() {
        return Array.from(filterInputs)
            .filter(input => input.checked)
            .map(input => input.id);
    }

    function getPriceRange() {
        // Assuming there's a way to get min and max price from the UI, e.g., parsing slider values
        const minEl = document.getElementById('slider-range-value1');
        const maxEl = document.getElementById('slider-range-value2');
        return {
            min: minEl ? parseInt(minEl.textContent.replace('$', '') || '0', 10) : 0,
            max: maxEl ? parseInt(maxEl.textContent.replace('$', '') || '0', 10) : 0
        };
    }
});
