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

document.addEventListener('DOMContentLoaded', loadBillItems);

// Set today's date on the bill date field if present
document.addEventListener('DOMContentLoaded', function() {
    const billDate = document.getElementById('billDate');
    if (billDate && !billDate.value) {
        billDate.valueAsDate = new Date();
    }
});

// Function To Clear the Bill
const clearBillBtn = document.getElementById('clear-bill-btn');
if (clearBillBtn) {
    clearBillBtn.addEventListener('click', clearBill);
}
function clearBill() {
    // Clear the products from local storage
    localStorage.removeItem('billProducts');

    // Reset all form fields
    document.getElementById('clientName').value = '';
    document.getElementById('phone').value = '';
    document.getElementById('email').value = '';
    document.getElementById('address').value = '';
    
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
            
            console.log('Form validation passed, submitting...');
            // Let the form submit normally to Django
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
    // Ensure price is a valid number
    let price = parseFloat(productPrice);
    if (isNaN(price)) {
        alert('Invalid product price');
        return;
    }

    // Create a product object
    let product = { 
        title: productTitle, 
        price: price, 
        quantity: 1 
    };

    // Retrieve existing products from local storage and parse them
    let products = JSON.parse(localStorage.getItem('billProducts')) || [];

    // Check if the product already exists
    let existingProduct = products.find(p => p.title === productTitle);
    if (existingProduct) {
        existingProduct.quantity += 1; // Increment quantity
    } else {
        products.push(product); // Add new product
    }

    // Save the updated products array back to local storage
    localStorage.setItem('billProducts', JSON.stringify(products));

    // Reload bill items to display the product
    loadBillItems();
    
    // Scroll to the bill builder
    const billBuilder = document.getElementById('bill-builder');
    if (billBuilder) {
        billBuilder.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
