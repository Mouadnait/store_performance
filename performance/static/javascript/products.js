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

// add product to bill
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
// End of Filter Orders
