/**
 * Authentication page scripts
 */

// Auto-close alert messages after 3 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                if (typeof $ !== 'undefined' && $.fn.alert) {
                    $(alert).alert('close');
                } else {
                    // Fallback for Bootstrap 5+
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            });
        }, 3000);
    }
});
