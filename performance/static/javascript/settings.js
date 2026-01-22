// ===== SETTINGS PAGE JAVASCRIPT =====

// Toggle Edit Profile Modal
function toggleEditProfile() {
    const modal = document.getElementById('editProfileModal');
    if (modal.classList.contains('show')) {
        modal.classList.remove('show');
    } else {
        modal.classList.add('show');
    }
}

// Toggle Change Password Modal
function toggleChangePassword() {
    const modal = document.getElementById('changePasswordModal');
    if (modal.classList.contains('show')) {
        modal.classList.remove('show');
    } else {
        modal.classList.add('show');
    }
}

// Preview Profile Image before upload
function previewProfileImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function (e) {
            const preview = document.getElementById('profileImagePreview');
            preview.src = e.target.result;
            
            // Show success message
            showNotification('Image preview updated', 'success');
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Toggle Dark Mode
function toggleDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    if (toggle.checked) {
        body.classList.add('dark-mode');
        body.classList.add('dark');
        localStorage.setItem('darkMode', 'enabled');
        showNotification('Dark mode enabled', 'success');
    } else {
        body.classList.remove('dark-mode');
        body.classList.remove('dark');
        localStorage.setItem('darkMode', 'disabled');
        showNotification('Dark mode disabled', 'success');
    }
}

// Initialize Dark Mode on Page Load
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeEnabled = localStorage.getItem('darkMode') === 'enabled';
    
    if (darkModeEnabled) {
        darkModeToggle.checked = true;
        document.body.classList.add('dark-mode');
        document.body.classList.add('dark');
    }
}

// Confirm Delete Account
function confirmDeleteAccount() {
    const confirmed = confirm(
        'Are you sure you want to delete your account? This action cannot be undone.\n\n' +
        'All your data, products, clients, and bills will be permanently deleted.'
    );
    
    if (confirmed) {
        const doubleConfirmed = confirm(
            'This is your final warning. Type your email to confirm deletion:\n\n' +
            'This action is irreversible!'
        );
        
        if (doubleConfirmed) {
            // In production, you would send a delete request here
            showNotification('Account deletion initiated', 'warning');
            // window.location.href = '/delete-account/';
        }
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="material-icons-sharp">${getIconForType(type)}</span>
            <p>${message}</p>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Get icon based on notification type
function getIconForType(type) {
    const icons = {
        'success': 'check_circle',
        'error': 'error',
        'warning': 'warning',
        'info': 'info'
    };
    return icons[type] || 'info';
}

// Handle Edit Profile Form Submission
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initializeDarkMode();
    
    const editProfileForm = document.getElementById('editProfileForm');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showNotification('Profile updated successfully!', 'success');
            toggleEditProfile();
            // In production, you would send the form data here
        });
    }
    
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showNotification('Password changed successfully!', 'success');
            toggleChangePassword();
            // In production, you would send the password change request here
        });
    }
    
    // Close modals when clicking outside
    const modals = document.querySelectorAll('.modal');
    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
    
    // Add smooth scroll for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Toggle switches with animation
    const toggleSwitches = document.querySelectorAll('.toggle-switch');
    toggleSwitches.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const label = this.parentElement.querySelector('.label-text h4').textContent;
            const state = this.checked ? 'enabled' : 'disabled';
            showNotification(`${label} ${state}`, 'success');
        });
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            modal.classList.remove('show');
        });
    }
    
    // Ctrl+S to save (prevent default)
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const activeForm = document.querySelector('.modal.show form');
        if (activeForm) {
            activeForm.dispatchEvent(new Event('submit'));
        }
    }
});

// Lazy load profile image
function lazyLoadProfileImage() {
    const image = document.getElementById('profileImagePreview');
    if (image && image.src) {
        const img = new Image();
        img.onload = function() {
            image.style.opacity = '1';
        };
        img.src = image.src;
    }
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        toggleEditProfile,
        toggleChangePassword,
        previewProfileImage,
        toggleDarkMode,
        confirmDeleteAccount,
        showNotification
    };
}

// Performance monitoring
function logPerformanceMetrics() {
    if (window.performance && window.performance.timing) {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log('Page Load Time:', pageLoadTime, 'ms');
    }
}

// Call on page load
window.addEventListener('load', () => {
    logPerformanceMetrics();
    initializeDarkMode();
});
