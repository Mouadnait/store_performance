/**
 * ============================================================
 * AUTH JAVASCRIPT - Authentication Page Interactions
 * ============================================================
 */

// Form submission handler
function submitForm(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Add loading state to button
    if (submitButton) {
        submitButton.classList.add('btn-loading');
        submitButton.disabled = true;
    }
    
    // Form will submit normally
    // Remove this if you want to prevent default and use AJAX
    // event.preventDefault();
}

// Auto-dismiss messages after delay
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message-alert');
    
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.animation = 'slideOut 0.3s ease-in-out';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Password visibility toggle
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bx-show');
        icon.classList.add('bx-hide');
    } else {
        input.type = 'password';
        icon.classList.remove('bx-hide');
        icon.classList.add('bx-show');
    }
}

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';
