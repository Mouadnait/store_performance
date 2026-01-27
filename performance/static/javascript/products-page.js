/**
 * Products Page JavaScript
 * Handles modal operations, search/filter functionality, and image preview
 */

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================

/**
 * Toggle product form modal
 */
function toggleProductForm() {
    openProductFormModal();
}

/**
 * Open product form modal
 */
function openProductFormModal() {
    const modal = document.getElementById('productFormModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        console.log('Product form modal opened');
    } else {
        console.error('Product form modal not found');
    }
}

/**
 * Close product form modal
 */
function closeProductFormModal() {
    const modal = document.getElementById('productFormModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        console.log('Product form modal closed');
    }
}

/**
 * Open bill builder modal
 */
function openBillBuilderModal() {
    const modal = document.getElementById('billBuilderModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        console.log('Bill builder modal opened');
    } else {
        console.error('Bill builder modal not found');
    }
}

/**
 * Close bill builder modal
 */
function closeBillBuilderModal() {
    const modal = document.getElementById('billBuilderModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        console.log('Bill builder modal closed');
    }
}

/**
 * Open bill builder modal when scrolling
 */
function scrollToBillBuilder() {
    openBillBuilderModal();
}

// ============================================================================
// FILTER FUNCTION
// ============================================================================

/**
 * Filter products by search term and category
 */
function myFunction() {
    const input = document.getElementById('myInput');
    const categoryFilter = document.getElementById('categoryFilter');
    
    if (!input || !categoryFilter) {
        console.error('Search or category filter element not found');
        return;
    }
    
    const searchFilter = input.value.toUpperCase();
    const selectedCategory = categoryFilter.value.toUpperCase();
    const cards = document.querySelectorAll('#productsGrid .product-card');
    
    if (cards.length === 0) {
        console.warn('No product cards found');
        return;
    }
    
    cards.forEach(card => {
        const titleElement = card.querySelector('.product-title');
        const categoryElement = card.querySelector('.product-category');
        
        const title = titleElement ? titleElement.textContent.toUpperCase() : '';
        const category = categoryElement ? categoryElement.textContent.toUpperCase() : '';
        
        const matchesSearch = searchFilter === '' || 
                            title.indexOf(searchFilter) > -1 || 
                            category.indexOf(searchFilter) > -1;
        const matchesCategory = selectedCategory === '' || 
                               category.indexOf(selectedCategory) > -1;
        
        if (matchesSearch && matchesCategory) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
    
    console.log('Products filtered - Search:', searchFilter, 'Category:', selectedCategory);
}

// ============================================================================
// IMAGE PREVIEW FUNCTIONALITY
// ============================================================================

/**
 * Initialize image preview for product image input
 */
function initializeImagePreview() {
    const imageInput = document.querySelector('input[name="image"]');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('imagePreview');
                    const previewImg = document.getElementById('previewImg');
                    if (previewImg && preview) {
                        previewImg.src = event.target.result;
                        preview.style.display = 'block';
                        console.log('Image preview loaded');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// ============================================================================
// MODAL CLOSE ON OUTSIDE CLICK
// ============================================================================

/**
 * Close modals when clicking outside the modal content
 */
function initializeModalCloseOnOutsideClick() {
    const productModal = document.getElementById('productFormModal');
    const billModal = document.getElementById('billBuilderModal');
    
    window.addEventListener('click', function(event) {
        if (productModal && event.target === productModal) {
            closeProductFormModal();
        }
        if (billModal && event.target === billModal) {
            closeBillBuilderModal();
        }
    });
    
    console.log('Modal close-on-outside-click initialized');
}

// ============================================================================
// PAGE INITIALIZATION
// ============================================================================

/**
 * Initialize all page functionality when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Products page loaded - initializing components');
    
    initializeImagePreview();
    initializeModalCloseOnOutsideClick();
    
    console.log('All components initialized successfully');
});
