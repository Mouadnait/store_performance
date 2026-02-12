// ========================================
// Store Performance - Base JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // ========== ERROR HANDLING WRAPPER ==========
    try {
        initializeApp();
    } catch (error) {
        console.error('Critical error during app initialization:', error);
    }
});

// ========== MAIN INITIALIZATION FUNCTION ==========
function initializeApp() {
    // ========== SIDEBAR TOGGLE ==========
    const sidebar = document.querySelector('.sidebar');
    // Prefer the new header toggle; fall back to sidebar header if present
    const toggle = document.querySelector('.home-header-left .toggle') || document.querySelector('.sidebar header .toggle');
    const home = document.querySelector('.home');
    const themeToggleButtons = Array.from(document.querySelectorAll('.theme-toggle'));
    const languageSwitch = document.querySelector('.language-switch');
    const languageToggleButton = languageSwitch ? languageSwitch.querySelector('.language-toggle') : null;
    const languageMenu = languageSwitch ? languageSwitch.querySelector('.language-menu') : null;
    const languageButtons = languageSwitch ? languageSwitch.querySelectorAll('.language-menu button') : [];
    const languageLabel = languageSwitch ? languageSwitch.querySelector('.language-label') : null;

    const languageDisplayNames = {
        en: 'English',
        fr: 'Français',
        es: 'Español'
    };

    const applySidebarStateToBody = () => {
        if (!document.body) {
            return;
        }

        const isClosed = sidebar && sidebar.classList.contains('close');
        document.body.classList.toggle('sidebar-closed', Boolean(isClosed));
    };

    const applyThemePreference = (mode) => {
        const preference = mode === 'dark' ? 'dark' : 'light';
        const isDark = preference === 'dark';

        if (document.body) {
            document.body.classList.toggle('dark', isDark);
            document.body.classList.toggle('dark-mode', isDark);
        }

        if (document.documentElement) {
            document.documentElement.dataset.theme = preference;
            document.documentElement.style.colorScheme = preference;
        }

        themeToggleButtons.forEach((button) => {
            button.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            button.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            button.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');

            const labelEl = button.querySelector('.button-label');
            if (labelEl) {
                labelEl.textContent = isDark ? 'Light' : 'Dark';
            }

            const iconEl = button.querySelector('i');
            if (iconEl) {
                iconEl.classList.remove('bx-sun', 'bx-moon');
                iconEl.classList.add(isDark ? 'bx-sun' : 'bx-moon');
            }
        });

        const settingsToggle = document.getElementById('darkModeToggle');
        if (settingsToggle) {
            settingsToggle.checked = isDark;
            settingsToggle.setAttribute('aria-checked', isDark ? 'true' : 'false');
        }

        try {
            localStorage.setItem('themePreference', preference);
        } catch (error) {
            console.warn('Could not store theme preference:', error);
        }
    };

    const resolveInitialTheme = () => {
        try {
            const storedTheme = localStorage.getItem('themePreference');
            if (storedTheme === 'dark' || storedTheme === 'light') {
                return storedTheme;
            }
        } catch (error) {
            console.warn('Unable to read saved theme preference:', error);
        }

        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        return 'light';
    };

    const setLanguageMenuOpen = (isOpen) => {
        if (!languageSwitch || !languageToggleButton) {
            return;
        }

        languageSwitch.setAttribute('data-open', isOpen ? 'true' : 'false');
        languageToggleButton.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    };

    const applyLanguagePreference = (languageCode) => {
        if (!languageDisplayNames) {
            return;
        }

        const fallback = Object.prototype.hasOwnProperty.call(languageDisplayNames, languageCode) ? languageCode : 'en';
        const labelText = languageDisplayNames[fallback];

        if (languageLabel) {
            languageLabel.textContent = labelText;
        }

        if (document.documentElement) {
            document.documentElement.setAttribute('lang', fallback);
        }

        languageButtons.forEach((button) => {
            const isActive = button.dataset.lang === fallback;
            button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        try {
            localStorage.setItem('languagePreference', fallback);
        } catch (error) {
            console.warn('Could not store language preference:', error);
        }
    };
    
    // Safely restore sidebar state from localStorage
    try {
        const sidebarState = localStorage.getItem('sidebarState');
        if (sidebarState === 'closed' && sidebar) {
            sidebar.classList.add('close');
        }
    } catch (error) {
        console.warn('LocalStorage unavailable:', error);
    }
    applySidebarStateToBody();

    const initialTheme = resolveInitialTheme();
    applyThemePreference(initialTheme);

    let initialLanguage = 'en';
    try {
        const storedLanguage = localStorage.getItem('languagePreference');
        if (storedLanguage) {
            initialLanguage = storedLanguage;
        }
    } catch (error) {
        console.warn('Unable to read saved language preference:', error);
    }
    applyLanguagePreference(initialLanguage);

    themeToggleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const nextTheme = document.body && document.body.classList.contains('dark') ? 'light' : 'dark';
            applyThemePreference(nextTheme);
        });
    });

    const settingsToggle = document.getElementById('darkModeToggle');
    if (settingsToggle) {
        settingsToggle.addEventListener('change', () => {
            const nextTheme = settingsToggle.checked ? 'dark' : 'light';
            applyThemePreference(nextTheme);
        });
    }

    window.toggleDarkMode = function() {
        const nextTheme = document.body && document.body.classList.contains('dark') ? 'light' : 'dark';
        applyThemePreference(nextTheme);
    };

    window.setThemePreference = function(mode) {
        applyThemePreference(mode);
    };

    if (languageToggleButton) {
        languageToggleButton.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = languageSwitch && languageSwitch.getAttribute('data-open') === 'true';
            setLanguageMenuOpen(!isOpen);
        });
    }

    languageButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();
            const selectedLanguage = button.dataset.lang || 'en';
            applyLanguagePreference(selectedLanguage);
            setLanguageMenuOpen(false);
        });
    });

    document.addEventListener('click', (event) => {
        if (languageSwitch && !languageSwitch.contains(event.target)) {
            setLanguageMenuOpen(false);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            setLanguageMenuOpen(false);
        }
    });
    
    // Desktop sidebar toggle with enhanced animation
    if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
            try {
                // Add transitioning class for smoother animation
                sidebar.classList.add('transitioning');
                sidebar.classList.toggle('close');
                
                // Store state safely
                try {
                    localStorage.setItem('sidebarState', sidebar.classList.contains('close') ? 'closed' : 'open');
                } catch (error) {
                    console.warn('Could not save sidebar state:', error);
                }
                
                // Remove transitioning class after animation
                setTimeout(() => {
                    sidebar.classList.remove('transitioning');
                }, 300);
                
                // Rotate toggle icon smoothly
                toggle.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                toggle.style.transform = sidebar.classList.contains('close') ? 'rotate(180deg)' : 'rotate(0deg)';

                applySidebarStateToBody();
            } catch (error) {
                console.error('Error toggling sidebar:', error);
            }
        });
        
        // Set initial toggle icon rotation
        if (sidebar && sidebar.classList.contains('close')) {
            toggle.style.transform = 'rotate(180deg)';
        }
        applySidebarStateToBody();
    }
    
    // ========== MOBILE MENU ==========
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    // Safely open mobile menu
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function(e) {
            try {
                e.stopPropagation();
                if (sidebar) {
                    sidebar.classList.add('mobile-open');
                }
                if (sidebarOverlay) {
                    sidebarOverlay.classList.add('active');
                }
                document.body.style.overflow = 'hidden';
            } catch (error) {
                console.error('Error opening mobile menu:', error);
            }
        });
    }
    
    // Close mobile menu when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            try {
                if (sidebar) {
                    sidebar.classList.remove('mobile-open');
                }
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            } catch (error) {
                console.error('Error closing mobile menu:', error);
            }
        });
    }
    
    // Close mobile menu when clicking a link
    const navLinks = document.querySelectorAll('.sidebar .nav-link a, .sidebar .quick-action');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            try {
                // Only close on mobile
                if (window.innerWidth <= 768 && sidebar) {
                    sidebar.classList.remove('mobile-open');
                    if (sidebarOverlay) {
                        sidebarOverlay.classList.remove('active');
                    }
                    document.body.style.overflow = '';
                }
            } catch (error) {
                console.error('Error handling nav link click:', error);
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
            try {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(function() {
                    alert.remove();
                }, 300);
            } catch (error) {
                console.warn('Error removing alert:', error);
            }
        }, 5000);
    });
    
    // ========== RESPONSIVE ADJUSTMENTS ==========
    function handleResize() {
        try {
            const width = window.innerWidth;
            
            // Reset mobile menu state on desktop
            if (width > 768) {
                if (sidebar) {
                    sidebar.classList.remove('mobile-open');
                }
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('active');
                }
                document.body.style.overflow = '';
            }
        } catch (error) {
            console.error('Error in resize handler:', error);
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
        try {
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
        } catch (error) {
            console.error('Error in keyboard handler:', error);
        }
    });
    
    // ========== SCROLL POSITION MEMORY ==========
    const menuBar = document.querySelector('.sidebar .menu-bar');
    if (menuBar) {
        try {
            // Restore scroll position
            const savedScrollPos = localStorage.getItem('sidebarScrollPos');
            if (savedScrollPos) {
                menuBar.scrollTop = parseInt(savedScrollPos);
            }
            
            // Save scroll position on scroll with debounce
            let scrollTimeout;
            menuBar.addEventListener('scroll', function() {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    try {
                        localStorage.setItem('sidebarScrollPos', menuBar.scrollTop);
                    } catch (error) {
                        console.warn('Could not save scroll position:', error);
                    }
                }, 150);
            });
        } catch (error) {
            console.warn('Scroll position memory error:', error);
        }
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
        if (trigger && trigger.getAttribute('data-tooltip')) {
            trigger.setAttribute('title', trigger.getAttribute('data-tooltip'));
        }
    });
}

// ========== UTILITY FUNCTIONS ==========

// ========== AJAX CONTENT LOADING ==========
// Intercept all internal navigation links
document.addEventListener('click', function(e) {
    try {
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
    } catch (error) {
        console.error('Error in link click handler:', error);
    }
});

// Load page content via AJAX
function loadPageViaAJAX(url, linkElement) {
    try {
        // Show loading state
        const home = document.querySelector('.home');
        const pageContent = document.querySelector('.page-content');
        
        if (!home || !pageContent) {
            console.warn('Required elements not found for AJAX loading');
            return;
        }
        
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
            credentials: 'include',
            signal: AbortSignal.timeout(30000) // 30 second timeout
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            try {
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
                    
                    if (!currentTitle || !currentContent) {
                        window.location.href = url;
                        return;
                    }
                    
                    // Fade out current content
                    currentContent.style.opacity = '0';
                    
                    // Wait for fade out
                    setTimeout(() => {
                        try {
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
                        } catch (error) {
                            console.error('Error updating page content:', error);
                            window.location.href = url;
                        }
                    }, 300);
                } else {
                    // Fallback to full page reload if content not found
                    console.warn('Page structure not found in AJAX response');
                    window.location.href = url;
                }
            } catch (error) {
                console.error('Error parsing AJAX response:', error);
                window.location.href = url;
            }
        })
        .catch(error => {
            console.error('AJAX Load Error:', error);
            // Fallback to full page reload
            window.location.href = url;
        });
    } catch (error) {
        console.error('Error in loadPageViaAJAX:', error);
        window.location.href = url;
    }
}

// Update active navigation link
function updateActiveNavLink(url) {
    try {
        // Remove active class from all links
        document.querySelectorAll('.sidebar .nav-link a').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to current link
        const currentLink = document.querySelector(`.sidebar .nav-link a[href="${url}"]`);
        if (currentLink) {
            currentLink.classList.add('active');
        }
    } catch (error) {
        console.warn('Error updating active nav link:', error);
    }
}

// Re-initialize page-specific scripts
function reinitializePageScripts() {
    try {
        // Ensure tooltips are initialized
        const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
        tooltipTriggers.forEach(function(trigger) {
            if (trigger && trigger.getAttribute('data-tooltip')) {
                trigger.setAttribute('title', trigger.getAttribute('data-tooltip'));
            }
        });
        
        // Dispatch custom event for page-specific initialization
        window.dispatchEvent(new CustomEvent('pageLoaded'));
    } catch (error) {
        console.warn('Error reinitializing page scripts:', error);
    }
}

// Handle browser back/forward
window.addEventListener('popstate', function(e) {
    try {
        if (e.state && e.state.url) {
            loadPageViaAJAX(e.state.url);
        }
    } catch (error) {
        console.error('Error handling popstate:', error);
    }
});

// Show toast notification
function showToast(message, type = 'success', duration = 3000) {
    try {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class='bx bx-${type === 'success' ? 'check-circle' : type === 'error' ? 'error-circle' : 'info-circle'}'></i>
            <span>${message}</span>
        `;
        
        // Append to body
        if (document.body) {
            document.body.appendChild(toast);
            
            // Animate in
            setTimeout(() => toast.classList.add('show'), 10);
            
            // Remove after delay
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    } catch (error) {
        console.error('Error showing toast:', error);
    }
}

// Confirm dialog
function confirmAction(message, callback) {
    try {
        if (confirm(message)) {
            callback();
        }
    } catch (error) {
        console.error('Error in confirmAction:', error);
    }
}

// Format currency
function formatCurrency(amount, currency = '$') {
    try {
        return currency + parseFloat(amount).toFixed(2);
    } catch (error) {
        console.warn('Error formatting currency:', error);
        return currency + '0.00';
    }
}

// Format date
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        console.warn('Error formatting date:', error);
        return dateString;
    }
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
