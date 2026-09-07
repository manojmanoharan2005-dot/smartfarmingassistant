/**
 * Mobile Navigation & Sidebar Handler
 * Smart Farming Assistant - Complete Mobile Responsive UI Adaptation
 */

(function () {
    'use strict';

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        setupPublicNavbar();
        setupDashboardSidebar();
        setupBottomNavHighlight();
        setupPasswordToggles();
        setupKeyboardHandlers();
        setupResponsiveResize();
        autoWrapTables();
        setupChartResizing();
    }

    /**
     * Public Header Navbar Hamburger Toggle
     */
    function setupPublicNavbar() {
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const navMenu = document.querySelector('.navbar-menu');

        if (mobileMenuBtn && navMenu) {
            mobileMenuBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                navMenu.classList.toggle('active');
                const icon = mobileMenuBtn.querySelector('i');
                if (icon) {
                    icon.className = navMenu.classList.contains('active') ? 'fas fa-times' : 'fas fa-bars';
                }
            });

            // Close navbar menu when clicking any nav link
            navMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('active');
                    const icon = mobileMenuBtn.querySelector('i');
                    if (icon) icon.className = 'fas fa-bars';
                });
            });

            // Close navbar menu on click outside
            document.addEventListener('click', function (e) {
                if (!navMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                    navMenu.classList.remove('active');
                    const icon = mobileMenuBtn.querySelector('i');
                    if (icon) icon.className = 'fas fa-bars';
                }
            });
        }
    }

    /**
     * Dashboard Sidebar Drawer & Overlay Setup
     */
    function setupDashboardSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        // Ensure sidebar overlay exists
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }

        overlay.addEventListener('click', closeSidebar);

        // Ensure mobile sidebar toggle button exists inside main-content if missing
        let toggle = document.querySelector('.mobile-sidebar-toggle');
        const mainContent = document.querySelector('.main-content');

        if (!toggle && mainContent && window.innerWidth <= 1024) {
            toggle = document.createElement('button');
            toggle.className = 'mobile-sidebar-toggle';
            toggle.setAttribute('aria-label', 'Toggle Navigation Menu');
            toggle.innerHTML = '<i class="fas fa-bars"></i>';
            mainContent.insertBefore(toggle, mainContent.firstChild);
        }

        if (toggle) {
            toggle.addEventListener('click', function (e) {
                e.stopPropagation();
                toggleSidebar();
            });
        }

        // Close sidebar on link click (mobile)
        sidebar.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function () {
                if (window.innerWidth <= 1024) {
                    closeSidebar();
                }
            });
        });
    }

    /**
     * Toggle Sidebar Drawer
     */
    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const toggle = document.querySelector('.mobile-sidebar-toggle');

        if (!sidebar) return;

        const isActive = sidebar.classList.toggle('active');

        if (overlay) {
            overlay.classList.toggle('active', isActive);
        }

        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.className = isActive ? 'fas fa-times' : 'fas fa-bars';
            }
        }

        document.body.style.overflow = isActive ? 'hidden' : '';
    }

    /**
     * Close Sidebar Drawer
     */
    function closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const toggle = document.querySelector('.mobile-sidebar-toggle');

        if (!sidebar) return;

        sidebar.classList.remove('active');

        if (overlay) {
            overlay.classList.remove('active');
        }

        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-bars';
            }
        }

        document.body.style.overflow = '';
    }

    /**
     * Highlight current tab in bottom navigation
     */
    function setupBottomNavHighlight() {
        const currentPath = window.location.pathname;
        const bottomNavItems = document.querySelectorAll('.bottom-nav-item');

        bottomNavItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && href !== '#' && currentPath.includes(href)) {
                bottomNavItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            }
        });
    }

    /**
     * Password Visibility Toggle Setup
     */
    function setupPasswordToggles() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            const group = input.parentElement;
            if (group && group.classList.contains('input-group') && !group.querySelector('.password-toggle-btn')) {
                const toggleBtn = document.createElement('button');
                toggleBtn.type = 'button';
                toggleBtn.className = 'password-toggle-btn';
                toggleBtn.setAttribute('aria-label', 'Toggle Password Visibility');
                toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';

                toggleBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';
                    toggleBtn.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
                });

                group.appendChild(toggleBtn);
            }
        });
    }

    /**
     * Handle Chart.js resizing on orientation / window changes
     */
    function setupChartResizing() {
        window.addEventListener('orientationchange', function () {
            setTimeout(() => {
                if (window.Chart && window.Chart.instances) {
                    Object.values(window.Chart.instances).forEach(chart => {
                        if (chart && typeof chart.resize === 'function') {
                            chart.resize();
                        }
                    });
                }
            }, 300);
        });
    }

    /**
     * Close on ESC key press
     */
    function setupKeyboardHandlers() {
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeSidebar();
                const navMenu = document.querySelector('.navbar-menu');
                if (navMenu) navMenu.classList.remove('active');
            }
        });
    }

    /**
     * Window Resize Handler
     */
    function setupResponsiveResize() {
        let timer;
        window.addEventListener('resize', function () {
            clearTimeout(timer);
            timer = setTimeout(function () {
                if (window.innerWidth > 1024) {
                    closeSidebar();
                }
            }, 200);
        });
    }

    /**
     * Automatically wrap tables in .table-responsive if not already wrapped
     */
    function autoWrapTables() {
        document.querySelectorAll('table').forEach(table => {
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }

    // Expose global methods
    window.toggleSidebar = toggleSidebar;
    window.closeSidebar = closeSidebar;
    window.toggleMobileMenu = function () {
        const navMenu = document.querySelector('.navbar-menu');
        if (navMenu) navMenu.classList.toggle('active');
    };

    window.MobileNav = {
        toggle: toggleSidebar,
        close: closeSidebar
    };

})();
