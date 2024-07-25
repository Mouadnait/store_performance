// Create a new bill
function loadBillItems() {
    let products = JSON.parse(localStorage.getItem('billProducts')) || [];
    let billBody = document.querySelector('.billbody tbody');

    while (billBody.children.length > 1) {
        billBody.removeChild(billBody.firstChild);
    }

    let grandTotal = 0;

    products.forEach((product, index) => {
        let row = billBody.insertRow(0);
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        let cell3 = row.insertCell(2);
        let cell4 = row.insertCell(3);
        let cell5 = row.insertCell(4);

        cell1.innerHTML = `<div><input type="number" class="quantity-input" data-index="${index}" value="${product.quantity}"></div>`;
        cell2.innerHTML = `<div>${product.title}</div>`;
        cell3.innerHTML = `<div>${product.price}</div>`;
        cell4.innerHTML = `<div>${(product.price * product.quantity).toFixed(2)}</div>`;
        cell5.innerHTML = `<button class="delete-btn" data-index="${index}">Delete</button>`;

        grandTotal += product.price * product.quantity;
    });

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function () {
            let productIndex = this.getAttribute('data-index');
            products.splice(productIndex, 1);
            localStorage.setItem('billProducts', JSON.stringify(products));
            loadBillItems();
        });
    });

    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function () {
            let productIndex = this.getAttribute('data-index');
            let newQuantity = parseInt(this.value);
            if (newQuantity > 0) {
                products[productIndex].quantity = newQuantity;
            } else {
                this.value = products[productIndex].quantity; // Reset if invalid
                return;
            }
            localStorage.setItem('billProducts', JSON.stringify(products));
            loadBillItems(); // Reload to update totals
        });
    });

    let grandTotalCell = document.querySelector('.billbody tbody tr:last-child td:last-child div input');
    if (grandTotalCell) {
        grandTotalCell.value = grandTotal.toFixed(2);
    }
}

document.addEventListener('DOMContentLoaded', loadBillItems);

// Function To Clear the Bill
document.getElementById('clear-bill-btn').addEventListener('click', clearBill);
function clearBill() {
    // Clear the products from local storage
    localStorage.removeItem('billProducts');

    // Optionally, reset the grand total to 0
    let grandTotalCell = document.querySelector('.billbody tbody tr:last-child td:last-child div input');
    if (grandTotalCell) {
        grandTotalCell.value = '0.00';
    }

    // Reload bill items to reflect the changes
    loadBillItems();
}

// Function To Save the Bill for each client
document.getElementById('save-bill-btn').addEventListener('click', function () {
    const clientName = document.querySelector('.billheader .firstline input[type="text"]').value; // Adjust the selector based on your actual input for the client name
    const billData = gatherBillData(); // Implement this function based on how you want to gather bill data

    // Assuming you're storing bills as an array of objects in localStorage
    let bills = JSON.parse(localStorage.getItem('bills')) || [];
    bills.push({ clientName: clientName, billData: billData });
    localStorage.setItem('bills', JSON.stringify(bills));

    alert('Bill saved for ' + clientName);
});

function gatherBillData() {
    // Implement gathering of bill data here
    // This is a placeholder function. You need to replace it with actual code to gather bill data from your form
    return {
        // Example data structure
        date: document.querySelector('.billheader .firstline input[type="text"]').value, // Adjust selector as needed
        items: [
            // Gather each item detail here
        ],
        totalPrice: document.getElementById('totalPrice').value
    };
}

//  add JavaScript to send the client's name to the backend when the "Save Bill" button is clicked. This example uses the Fetch API:
document.getElementById('save-bill-btn').addEventListener('click', function () {
    const clientName = document.getElementById('clientName').value;
    fetch('/client_bills/', { // The URL to your Django view
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Function to get CSRF token
        },
        body: JSON.stringify({ full_name: clientName })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Handle response
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submitForm(event) {
    event.preventDefault(); // Prevent default form submission
    var formData = new FormData(document.getElementById('billForm'));

    // Add additional data if needed
    formData.append('storeName', '{{request.user.username}}');
    formData.append('phoneNumber', '{{request.user.phone}}');

    fetch('/path/to/your/django/view/', { // Replace with your Django view URL
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}', // Include CSRF token
        },
    })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Handle success
        })
        .catch((error) => {
            console.error('Error:', error); // Handle errors
        });
}

// Call the submitForm function when the form is submitted
document.querySelector('form').addEventListener('submit', submitForm);



// Add Product Form
function toggleProductForm() {
    var form = document.getElementById("productForm");
    if (form.style.display === "none" || form.style.display === "") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

document.getElementById("myInput").addEventListener("keyup", function () {
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

function addToBill(productTitle, productPrice) {
    // Create a product object
    let product = { title: productTitle, price: productPrice, quantity: 1 };

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

    //alert('Product added to bill');
}

// Filter Orders
document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to filter inputs
    const filterInputs = document.querySelectorAll('.custom-control-input');
    const priceRange = document.querySelector('.form-control-range');

    filterInputs.forEach(input => input.addEventListener('change', filterProducts));
    priceRange.addEventListener('input', filterProducts);

    function filterProducts() {
        const selectedCategories = getSelectedCategories();
        const selectedPriceRange = getPriceRange();
        const products = document.querySelectorAll('.product-card'); // Assuming product cards have a class 'product-card'

        products.forEach(product => {
            const categories = product.getAttribute('data-categories').split(','); // Assuming product cards have a 'data-categories' attribute
            const price = parseInt(product.getAttribute('data-price'), 10); // Assuming product cards have a 'data-price' attribute

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
        return {
            min: parseInt(document.getElementById('slider-range-value1').textContent.replace('$', ''), 10),
            max: parseInt(document.getElementById('slider-range-value2').textContent.replace('$', ''), 10)
        };
    }
});
