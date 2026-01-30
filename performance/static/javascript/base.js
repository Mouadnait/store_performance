// ========================================
// Store Performance - Base JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // ========== SIDEBAR TOGGLE ==========
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.querySelector('.sidebar header .toggle');
    const home = document.querySelector('.home');
    
    // Restore sidebar state from localStorage
    const sidebarState = localStorage.getItem('sidebarState');
    if (sidebarState === 'closed' && sidebar) {
        sidebar.classList.add('close');
    }
    
    // Desktop sidebar toggle with enhanced animation
    if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
            // Add transitioning class for smoother animation
            sidebar.classList.add('transitioning');
            sidebar.classList.toggle('close');
            
            // Store state
            localStorage.setItem('sidebarState', sidebar.classList.contains('close') ? 'closed' : 'open');
            
            // Remove transitioning class after animation
            setTimeout(() => {
                sidebar.classList.remove('transitioning');
            }, 300);
            
            // Rotate toggle icon smoothly
            toggle.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            toggle.style.transform = sidebar.classList.contains('close') ? 'rotate(180deg)' : 'rotate(0deg)';
        });
        
        // Set initial toggle icon rotation
        if (sidebar && sidebar.classList.contains('close')) {
            toggle.style.transform = 'rotate(180deg)';
        }
    }
    
    // ========== MOBILE MENU ==========
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    // Open mobile menu
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.add('mobile-open');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    // Close mobile menu when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Close mobile menu when clicking a link
    const navLinks = document.querySelectorAll('.sidebar .nav-link a, .sidebar .quick-action');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Only close on mobile
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('mobile-open');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    // ========== ACTIVE LINK HIGHLIGHTING ==========
    const currentPath = window.location.pathname;
    const allNavLinks = document.querySelectorAll('.sidebar a');
    
    allNavLinks.forEach(function(link) {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath) {
            link.classList.add('active');
            link.classList.remove('none');
        }
    });
    
    // ========== AUTO-DISMISS ALERTS ==========
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // ========== RESPONSIVE ADJUSTMENTS ==========
    function handleResize() {
        const width = window.innerWidth;
        
        // Reset mobile menu state on desktop
        if (width > 768) {
            sidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    // Debounce resize handler
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    });
    
    // Initial check
    handleResize();
    
    // ========== SMOOTH SCROLL ==========
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && targetId !== '#!') {
                e.preventDefault();
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ========== KEYBOARD NAVIGATION ==========
    // Toggle sidebar with Ctrl/Cmd + B
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            if (toggle && sidebar) {
                toggle.click();
            }
        }
        
        // Close mobile menu with Escape key
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('mobile-open')) {
            sidebar.classList.remove('mobile-open');
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('active');
            }
            document.body.style.overflow = '';
        }
    });
    
    // ========== SCROLL POSITION MEMORY ==========
    const menuBar = document.querySelector('.sidebar .menu-bar');
    if (menuBar) {
        // Restore scroll position
        const savedScrollPos = localStorage.getItem('sidebarScrollPos');
        if (savedScrollPos) {
            menuBar.scrollTop = parseInt(savedScrollPos);
        }
        
        // Save scroll position on scroll
        let scrollTimeout;
        menuBar.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                localStorage.setItem('sidebarScrollPos', menuBar.scrollTop);
            }, 150);
        });
    }
    
    // ========== ENHANCED HOVER EFFECTS ==========
    const quickActions = document.querySelectorAll('.sidebar .quick-action');
    quickActions.forEach(action => {
        action.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });
    
    // ========== PREVENT HORIZONTAL SCROLL ==========
    document.body.style.overflowX = 'hidden';
    
    // ========== TOOLTIP INITIALIZATION (if needed) ==========
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(function(trigger) {
        trigger.setAttribute('title', trigger.getAttribute('data-tooltip'));
    });
});

// ========== UTILITY FUNCTIONS ==========

// ========== AJAX CONTENT LOADING ==========
// Intercept all internal navigation links
document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href]');
    
    // Only handle internal links
    if (!link) return;
    
    const href = link.getAttribute('href');
    
    // Skip special links
    if (!href || 
        href.startsWith('http') || 
        href.startsWith('mailto:') || 
        href.startsWith('tel:') ||
        href.startsWith('#') ||
        href.startsWith('javascript:') ||
        link.target === '_blank' ||
        link.hasAttribute('data-no-ajax')) {
        return;
    }
    
    // Check if link is part of sidebar or main navigation
    const isNavLink = link.closest('.sidebar') || link.closest('.nav-link');
    
    if (isNavLink) {
        e.preventDefault();
        loadPageViaAJAX(href, link);
    }
});

// Load page content via AJAX
function loadPageViaAJAX(url, linkElement) {
    // Show loading state
    const home = document.querySelector('.home');
    const pageContent = document.querySelector('.page-content');
    
    if (!home || !pageContent) return;
    
    // Add loading class
    home.classList.add('loading');
    pageContent.style.opacity = '0.6';
    pageContent.style.pointerEvents = 'none';
    
    // Close mobile menu if open
    const sidebar = document.querySelector('.sidebar');
    const mobileHeader = document.querySelector('.mobile-header');
    if (mobileHeader && sidebar && sidebar.classList.contains('mobile-open')) {
        const overlay = document.querySelector('.sidebar-overlay');
        sidebar.classList.remove('mobile-open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    // Fetch the page with AJAX header
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'text/html',
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        // Parse the response to extract content
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');
        
        // Extract page title
        const newTitle = newDoc.querySelector('.page-title');
        const newContent = newDoc.querySelector('.page-content');
        
        if (newTitle && newContent) {
            // Get current elements
            const currentTitle = document.querySelector('.page-title');
            const currentContent = document.querySelector('.page-content');
            
            // Fade out current content
            currentContent.style.opacity = '0';
            
            // Wait for fade out
            setTimeout(() => {
                // Replace content
                currentTitle.innerHTML = newTitle.innerHTML;
                currentContent.innerHTML = newContent.innerHTML;
                
                // Fade in new content
                currentContent.style.opacity = '1';
                
                // Update URL without page reload
                window.history.pushState({url: url}, '', url);
                
                // Update active navigation link
                updateActiveNavLink(url);
                
                // Re-initialize any scripts that might be needed
                reinitializePageScripts();
                
                // Scroll to top
                home.scrollTop = 0;
                
                // Remove loading state
                home.classList.remove('loading');
            }, 300);
        } else {
            // Fallback to full page reload if content not found
            window.location.href = url;
        }
    })
    .catch(error => {
        console.error('AJAX Load Error:', error);
        // Fallback to full page reload
        window.location.href = url;
    });
}

// Update active navigation link
function updateActiveNavLink(url) {
    // Remove active class from all links
    document.querySelectorAll('.sidebar .nav-link a').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current link
    const currentLink = document.querySelector(`.sidebar .nav-link a[href="${url}"]`);
    if (currentLink) {
        currentLink.classList.add('active');
    }
}

// Re-initialize page-specific scripts
function reinitializePageScripts() {
    // This can be extended to reinitialize charts, datepickers, etc.
    // For now, just ensure tooltips are initialized
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(function(trigger) {
        trigger.setAttribute('title', trigger.getAttribute('data-tooltip'));
    });
}

// Handle browser back/forward
window.addEventListener('popstate', function(e) {
    if (e.state && e.state.url) {
        loadPageViaAJAX(e.state.url);
    }
});

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class='bx bx-${type === 'success' ? 'check-circle' : 'error-circle'}'></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after delay
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format currency
function formatCurrency(amount, currency = '$') {
    return currency + parseFloat(amount).toFixed(2);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions to global scope
window.showToast = showToast;
window.confirmAction = confirmAction;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.debounce = debounce;
