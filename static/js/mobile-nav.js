/**
 * Mobile Navigation Handler
 * Handles hamburger menu toggle and sidebar behavior on mobile devices
 */

(function() {
    'use strict';
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    function init() {
        setupMobileToggle();
        setupSidebarOverlay();
        setupResponsiveHandlers();
        setupKeyboardHandlers();
    }
    
    /**
     * Setup mobile sidebar toggle button
     */
    function setupMobileToggle() {
        const toggle = document.querySelector('.mobile-sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (!toggle || !sidebar) return;
        
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleSidebar();
        });
    }
    
    /**
     * Toggle sidebar visibility
     */
    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const toggle = document.querySelector('.mobile-sidebar-toggle');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (!sidebar) return;
        
        const isActive = sidebar.classList.toggle('active');
        
        // Toggle icon
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.className = isActive ? 'fas fa-times' : 'fas fa-bars';
            }
        }
        
        // Toggle overlay
        if (overlay) {
            overlay.classList.toggle('active', isActive);
        }
        
        // Prevent body scroll when sidebar is open
        document.body.style.overflow = isActive ? 'hidden' : '';
    }
    
    /**
     * Close sidebar
     */
    function closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const toggle = document.querySelector('.mobile-sidebar-toggle');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (!sidebar) return;
        
        sidebar.classList.remove('active');
        
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-bars';
            }
        }
        
        if (overlay) {
            overlay.classList.remove('active');
        }
        
        document.body.style.overflow = '';
    }
    
    /**
     * Setup overlay click to close sidebar
     */
    function setupSidebarOverlay() {
        // Create overlay if it doesn't exist
        let overlay = document.querySelector('.sidebar-overlay');
        
        if (!overlay && document.querySelector('.sidebar')) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }
        
        if (overlay) {
            overlay.addEventListener('click', closeSidebar);
        }
        
        // Close sidebar when clicking on sidebar links (mobile)
        const sidebarLinks = document.querySelectorAll('.sidebar a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            });
        });
    }
    
    /**
     * Setup keyboard handlers (ESC to close)
     */
    function setupKeyboardHandlers() {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeSidebar();
            }
        });
    }
    
    /**
     * Setup responsive handlers
     */
    function setupResponsiveHandlers() {
        let resizeTimer;
        
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                // Close sidebar when switching to desktop view
                if (window.innerWidth > 768) {
                    closeSidebar();
                }
            }, 250);
        });
    }
    
    // Export functions for external use
    window.MobileNav = {
        toggle: toggleSidebar,
        close: closeSidebar
    };
    
})();
