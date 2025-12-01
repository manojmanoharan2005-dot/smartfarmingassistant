document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    loadDashboardData();
    
    // Sidebar navigation
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

function loadDashboardData() {
    // Load user statistics and recent activities
    console.log('Loading dashboard data...');
}
