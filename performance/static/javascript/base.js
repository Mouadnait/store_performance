/**
 * Store Performance Dashboard - Main JavaScript Module
 * Handles sidebar navigation, mobile menu, dark mode, and accessibility
 */

document.addEventListener("DOMContentLoaded", () => {
    'use strict';
    
    // DOM Elements
    const body = document.querySelector('body');
    const sidebar = body ? body.querySelector('nav') : null;
    const toggle = body ? body.querySelector(".toggle") : null;
    const searchBtn = body ? body.querySelector(".search-box") : null;
    const mobileMenuToggle = body ? body.querySelector(".mobile-menu-toggle") : null;
    const sidebarOverlay = body ? body.querySelector(".sidebar-overlay") : null;

    // Utility function to close mobile menu
    const closeMobileMenu = () => {
        if (sidebar) sidebar.classList.remove("mobile-open");
        if (sidebarOverlay) sidebarOverlay.classList.remove("active");
        if (body) body.classList.remove("mobile-menu-open");
    };

    // Utility function to open mobile menu
    const openMobileMenu = () => {
        if (sidebar) sidebar.classList.add("mobile-open");
        if (sidebarOverlay) sidebarOverlay.classList.add("active");
        if (body) body.classList.add("mobile-menu-open");
    };

    // Desktop sidebar toggle with localStorage persistence
    if (toggle && sidebar) {
        toggle.addEventListener("click", (e) => {
            e.preventDefault();
            sidebar.classList.toggle("close");
            const collapsed = sidebar.classList.contains('close');
            localStorage.setItem('sidebarCollapsed', collapsed ? '1' : '0');
            
            // Add haptic feedback if available
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }
        });
        
        // Accessibility: allow keyboard toggle
        toggle.setAttribute('tabindex', '0');
        toggle.setAttribute('role', 'button');
        toggle.setAttribute('aria-label', 'Toggle sidebar');
        toggle.setAttribute('aria-pressed', 'false');
        
        toggle.addEventListener('keyup', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggle.click();
            }
        });
        
        // Update aria-pressed attribute
        const updateAriaPressed = () => {
            const isPressed = sidebar.classList.contains('close');
            toggle.setAttribute('aria-pressed', isPressed);
        };
        toggle.addEventListener('click', updateAriaPressed);
    }

    // Mobile menu toggle with proper event handling
    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const isOpen = sidebar.classList.contains("mobile-open");
            
            if (isOpen) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
            
            // Haptic feedback
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }
        });
    }

    // Close mobile menu when overlay is clicked
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeMobileMenu();
        });
    }

    // Close mobile menu when a link is clicked
    if (sidebar) {
        const sidebarLinks = sidebar.querySelectorAll('.nav-link a, .quick-action, a[href^="/"]');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    // Small delay to allow navigation to complete
                    setTimeout(closeMobileMenu, 100);
                }
            });
        });
    }

    // Handle window resize with debouncing
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 768 && sidebar) {
                closeMobileMenu();
                // Restore desktop sidebar state from localStorage
                const isCollapsed = localStorage.getItem('sidebarCollapsed') === '1';
                if (isCollapsed) {
                    sidebar.classList.add('close');
                } else {
                    sidebar.classList.remove('close');
                }
            }
        }, 250);
    });

    // ESC key to close mobile menu
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && window.innerWidth <= 768) {
            closeMobileMenu();
        }
    });

    // Search button interaction
    if (searchBtn && sidebar) {
        searchBtn.addEventListener("click", () => {
            sidebar.classList.remove("close");
            localStorage.setItem('sidebarCollapsed', '0');
        });
    }

    // Restore sidebar collapsed state (desktop only)
    if (window.innerWidth > 768 && sidebar) {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === '1';
        if (isCollapsed) {
            sidebar.classList.add('close');
            if (toggle) {
                toggle.setAttribute('aria-pressed', 'true');
            }
        }
    }

    // Load dark mode preference from localStorage
    try {
        const darkModeEnabled = localStorage.getItem('darkMode') === 'enabled';
        if (darkModeEnabled && body) {
            body.classList.add('dark-mode');
            body.classList.add('dark');
        }
    } catch (error) {
        console.warn('localStorage not available:', error);
    }

    // Smooth scroll behavior for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Initialize clean state on load
    if (window.innerWidth <= 768) {
        closeMobileMenu();
    }

    // Suppress console errors in production
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Production error tracking can be added here
    }
});
