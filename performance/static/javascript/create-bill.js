console.log('create-bill.js file loaded successfully');

// Create a new bill
function loadBillItems() {
    const products = JSON.parse(localStorage.getItem('billProducts')) || [];
    const billBody = document.querySelector('.bill-table tbody');

    if (!billBody) return;

    // Rebuild tbody each time to avoid stale DOM and force live updates
    billBody.innerHTML = '';

    let grandTotal = 0;

    if (!products.length) {
        const emptyRow = document.createElement('tr');
        emptyRow.classList.add('bill-empty-row');
        emptyRow.innerHTML = '<td colspan="5" class="bill-empty-message">No products added yet. Click "Add to Bill" on any product above.</td>';
        billBody.appendChild(emptyRow);
    } else {
        products.forEach((product, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="number" class="quantity-input" data-index="${index}" value="${product.quantity}" step="0.01" min="1"></td>
                <td><input type="text" class="description-input" data-index="${index}" value="${product.title}" readonly style="cursor: default;"></td>
                <td><input type="number" class="price-input" data-index="${index}" value="${parseFloat(product.price).toFixed(2)}" step="0.01" readonly style="cursor: default;"></td>
                <td><input type="number" class="amount-input" data-index="${index}" value="${(product.price * product.quantity).toFixed(2)}" step="0.01" readonly style="cursor: default;"></td>
                <td><button type="button" class="delete-btn" data-index="${index}" style="background:#ff6b6b; color:white; padding:5px 10px; border:none; border-radius:4px; cursor:pointer;">Remove</button></td>
            `;
            billBody.appendChild(row);
            grandTotal += product.price * product.quantity;
        });

        billBody.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const idx = Number(button.getAttribute('data-index'));
                products.splice(idx, 1);
                localStorage.setItem('billProducts', JSON.stringify(products));
                loadBillItems();
                updateBillCounter(); // Update counter after removal
            });
        });

        billBody.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', () => {
                const idx = Number(input.getAttribute('data-index'));
                const newQty = parseFloat(input.value);
                if (newQty > 0) {
                    products[idx].quantity = newQty;
                    localStorage.setItem('billProducts', JSON.stringify(products));
                    loadBillItems();
                    updateBillCounter(); // Update counter after quantity change
                } else {
                    input.value = products[idx].quantity;
                }
            });
        });

    }

    const totalRow = document.createElement('tr');
    totalRow.classList.add('bill-total-row');
    totalRow.innerHTML = '<td colspan="3" class="text-right"><strong>Gr. Total:</strong></td><td colspan="2"><input type="number" name="totalPrice" id="totalPrice" placeholder="0.00" step="0.01" readonly></td>';
    billBody.appendChild(totalRow);

    const totalInput = totalRow.querySelector('#totalPrice');
    if (totalInput) totalInput.value = grandTotal.toFixed(2);
}

document.addEventListener('DOMContentLoaded', function() {
    loadBillItems();
    updateBillCounter();
});

// Set today's date on the bill date field if present
document.addEventListener('DOMContentLoaded', function() {
    const billDate = document.getElementById('billDate');
    if (billDate && !billDate.value) {
        billDate.valueAsDate = new Date();
    }
});

// Handle client selection and auto-populate fields
function handleClientSelection() {
    const selectElement = document.getElementById('clientSelect');
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const clientDetailsSection = document.getElementById('clientDetailsSection');
    const indicator = document.getElementById('clientModeIndicator');
    
    if (selectedOption.value === '') {
        // Create new client - show all fields as editable
        if (indicator) {
            indicator.innerHTML = '<span class="material-icons-sharp" style="font-size: 16px; vertical-align: middle; color: #4CAF50;">person_add</span> Creating new client - fill in the details below';
            indicator.style.color = '#4CAF50';
        }
        
        document.getElementById('clientName').value = '';
        document.getElementById('clientName').readOnly = false;
        document.getElementById('phone').value = '';
        document.getElementById('phone').readOnly = false;
        document.getElementById('email').value = '';
        document.getElementById('email').readOnly = false;
        document.getElementById('address').value = '';
        document.getElementById('address').readOnly = false;
        
        const cityField = document.getElementById('city');
        const countryField = document.getElementById('country');
        const postalField = document.getElementById('postal_code');
        if (cityField) {
            cityField.value = '';
            cityField.readOnly = false;
        }
        if (countryField) {
            countryField.value = '';
            countryField.readOnly = false;
        }
        if (postalField) {
            postalField.value = '';
            postalField.readOnly = false;
        }
        
        // Reset styling
        document.getElementById('clientName').style.backgroundColor = '';
        document.getElementById('phone').style.backgroundColor = '';
        document.getElementById('email').style.backgroundColor = '';
        document.getElementById('address').style.backgroundColor = '';
        if (cityField) cityField.style.backgroundColor = '';
        if (countryField) countryField.style.backgroundColor = '';
        if (postalField) postalField.style.backgroundColor = '';
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
        
        // Populate fields
        document.getElementById('clientName').value = name;
        document.getElementById('phone').value = phone;
        document.getElementById('email').value = email;
        document.getElementById('address').value = address;
        
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
    console.log('Bill form found:', billForm);
    
    if (billForm) {
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
    }
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
