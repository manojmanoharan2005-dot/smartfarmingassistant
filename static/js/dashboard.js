/**
 * Smart Farming Assistant - Dashboard Core JS
 * Extracted from dashboard.html
 */

// Global Variables & Data Initialization
let dashboardData = {};
try {
    const dataElement = document.getElementById('dashboard-data');
    if (dataElement) {
        dashboardData = JSON.parse(dataElement.textContent);
    }
} catch (e) {
    console.error('Failed to parse dashboard data:', e);
}

const currentUserId = dashboardData.userId || '';
const userState = dashboardData.userState || '';
const userDistrict = dashboardData.userDistrict || '';

// Modal Variables
let currentViewCropId = '';
let currentViewCropName = '';
let currentViewCropStage = '';
let currentViewCropNotes = '';
let currentFertilizerName = '';

// Charts
let priceTrendChart = null;
let expenseChart = null;
const expenseHistory = [];

/**
 * UI & Sidebar Functions
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }
}

// Handlers for Data Attributes in HTML
function handleCropView(btn) {
    const d = btn.dataset;
    openCropViewModal(d.id, d.crop, d.stage, parseFloat(d.progress), parseInt(d.day), d.started, d.notes);
}

function handleCropEdit(btn) {
    const d = btn.dataset;
    openCropEditModal(d.id, d.crop, d.stage, d.notes);
}

function handleFertilizerView(btn) {
    const d = btn.dataset;
    openFertilizerViewModal(d.id, d.fertilizer, d.crop, d.date, d.soil, d.n, d.p, d.k);
}

/**
 * Crop Modal Functions
 */
function openCropViewModal(id, cropName, stage, progress, currentDay, startDate, notes) {
    currentViewCropId = id;
    currentViewCropName = cropName;
    currentViewCropStage = stage;
    currentViewCropNotes = notes || '';

    const els = {
        'viewCropName': cropName,
        'viewCropStage': stage,
        'viewProgressText': progress + '%',
        'viewCurrentDay': currentDay,
        'viewStartDate': startDate,
        'viewNotes': notes || 'No notes added yet.'
    };

    for (const [id, val] of Object.entries(els)) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    // Update progress circle
    const circle = document.getElementById('viewProgressCircle');
    if (circle) {
        const circumference = 314.16;
        const offset = circumference - (circumference * progress / 100);
        circle.style.strokeDashoffset = offset;
    }

    // Generate timeline
    generateTimeline(stage, progress);

    const modal = document.getElementById('cropViewModal');
    if (modal) modal.style.display = 'flex';

    // Setup Action Buttons
    const editBtn = document.getElementById('editCropBtn');
    if (editBtn) {
        editBtn.onclick = function () {
            closeCropViewModal();
            setTimeout(() => {
                openCropEditModal(currentViewCropId, currentViewCropName, currentViewCropStage, currentViewCropNotes);
            }, 100);
        };
    }

    const fullViewBtn = document.getElementById('fullViewCropBtn');
    if (fullViewBtn) {
        fullViewBtn.onclick = function () {
            window.location.href = '/growing/view/' + id;
        };
    }
}

function closeCropViewModal() {
    const modal = document.getElementById('cropViewModal');
    if (modal) modal.style.display = 'none';
}

function generateTimeline(currentStage, progress) {
    const stages = [
        { name: 'Seed Sowing', icon: '🌱', days: '1-7' },
        { name: 'Germination', icon: '🌿', days: '7-14' },
        { name: 'Seedling', icon: '🌾', days: '14-30' },
        { name: 'Vegetative Growth', icon: '🌳', days: '30-60' },
        { name: 'Flowering', icon: '🌸', days: '60-75' },
        { name: 'Fruit Development', icon: '🍎', days: '75-90' },
        { name: 'Maturity', icon: '✅', days: '90-110' },
        { name: 'Harvest Ready', icon: '🎉', days: '110+' }
    ];

    const currentIndex = stages.findIndex(s => s.name === currentStage);
    const timeline = document.getElementById('viewTimeline');
    if (!timeline) return;

    timeline.innerHTML = '';

    stages.forEach((stage, index) => {
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;

        const item = document.createElement('div');
        item.style.cssText = 'display: flex; gap: 12px; margin-bottom: 16px; position: relative;';

        // Vertical line
        if (index < stages.length - 1) {
            item.innerHTML += `<div style="position: absolute; left: 11px; top: 28px; bottom: -16px; width: 2px; background: ${isCompleted ? '#10b981' : '#e2e8f0'};"></div>`;
        }

        // Icon circle
        const iconBg = isCompleted ? '#10b981' : (isCurrent ? '#3b82f6' : '#e2e8f0');
        const iconColor = isCompleted || isCurrent ? 'white' : '#94a3b8';

        item.innerHTML += `
            <div style="width: 24px; height: 24px; border-radius: 50%; background: ${iconBg}; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; z-index: 1;">
                ${isCompleted ? '✓' : stage.icon}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 13px; font-weight: 600; color: ${isCurrent ? '#3b82f6' : (isCompleted ? '#10b981' : '#64748b')};">
                    ${stage.name} ${isCurrent ? '(Current)' : ''}
                </div>
                <div style="font-size: 11px; color: #94a3b8;">Days ${stage.days}</div>
            </div>
        `;

        timeline.appendChild(item);
    });
}

function openCropEditModal(id, cropName, stage, notes) {
    const els = {
        'editCropId': id,
        'editCropName': cropName,
        'editCropStage': stage,
        'editCropNotes': notes || ''
    };

    for (const [elId, val] of Object.entries(els)) {
        const el = document.getElementById(elId);
        if (el) el.value = val;
    }

    const title = document.getElementById('editCropTitle');
    if (title) title.textContent = 'Editing: ' + cropName;

    const modal = document.getElementById('cropEditModal');
    if (modal) modal.style.display = 'flex';
}

function closeCropEditModal() {
    const modal = document.getElementById('cropEditModal');
    if (modal) modal.style.display = 'none';
}

/**
 * Fertilizer functions
 */
function openFertilizerViewModal(id, fertilizerName, crop, date, soilType, nitrogen, phosphorus, potassium) {
    currentFertilizerName = fertilizerName || 'fertilizer';

    const els = {
        'viewFertilizerName': fertilizerName || 'Fertilizer',
        'viewFertilizerCrop': crop || '-',
        'viewFertilizerSoil': soilType || 'Not specified',
        'viewFertilizerDate': date || '-',
        'viewFertilizerN': nitrogen || '-',
        'viewFertilizerP': phosphorus || '-',
        'viewFertilizerK': potassium || '-'
    };

    for (const [id, val] of Object.entries(els)) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    const modal = document.getElementById('fertilizerViewModal');
    if (modal) modal.style.display = 'flex';
}

function closeFertilizerViewModal() {
    const modal = document.getElementById('fertilizerViewModal');
    if (modal) modal.style.display = 'none';
}

function openAmazonLink() {
    const url = 'https://www.amazon.in/s?k=' + encodeURIComponent(currentFertilizerName + ' fertilizer');
    window.open(url, '_blank');
}

function openIndiamartLink() {
    const url = 'https://www.indiamart.com/search.mp?ss=' + encodeURIComponent(currentFertilizerName + ' fertilizer');
    window.open(url, '_blank');
}

/**
 * Buy Dropdown
 */
function toggleBuyDropdown(button) {
    const container = button.parentElement;
    const dropdown = container.querySelector('.buy-dropdown');

    // Close all other dropdowns first
    document.querySelectorAll('.buy-dropdown').forEach(d => {
        if (d !== dropdown) d.style.display = 'none';
    });

    // Toggle this dropdown
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Delete Functions
 */
function deleteCropActivity(activityId) {
    if (confirm('Are you sure you want to delete this crop activity?')) {
        fetch('/growing/delete/' + activityId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to delete: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to delete activity');
            });
    }
}

function deleteFertilizer(fertilizerId) {
    if (confirm('Are you sure you want to delete this fertilizer recommendation?')) {
        fetch('/fertilizer/delete/' + fertilizerId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to delete: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to delete recommendation');
            });
    }
}

/**
 * Chatbot Functions
 */
function toggleChatbot() {
    const win = document.getElementById('chatbotWindow');
    if (win) win.classList.toggle('active');
}

function openChatbotModal() {
    const win = document.getElementById('chatbotWindow');
    if (win) win.classList.add('active');
}

function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const messagesContainer = document.getElementById('chatMessages');

    // Add user message
    messagesContainer.innerHTML += `
        <div class="chat-message user">
            <div class="message-avatar">👤</div>
            <div class="message-content">${message}</div>
        </div>
    `;

    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Send to server
    fetch('/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.response) {
                messagesContainer.innerHTML += `
                    <div class="chat-message bot">
                        <div class="message-avatar">🤖</div>
                        <div class="message-content">${data.response}</div>
                    </div>
                `;
            } else {
                const errorMsg = data.error || 'Sorry, I couldn\'t process your request. Please try again.';
                messagesContainer.innerHTML += `
                    <div class="chat-message bot">
                        <div class="message-avatar">🤖</div>
                        <div class="message-content">${errorMsg}</div>
                    </div>
                `;
            }
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Fetch error:', error);
            messagesContainer.innerHTML += `
                <div class="chat-message bot">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">Sorry, I couldn't process your request. Please try again.</div>
                </div>
            `;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
}

/**
 * Price Trend Analysis
 */
function loadPriceTrend(commodity, days = 7) {
    if (!commodity) return;

    // Update active button state
    const btn7 = document.getElementById('btn-7d');
    const btn30 = document.getElementById('btn-30d');
    if (btn7) btn7.classList.toggle('active', days === 7);
    if (btn30) btn30.classList.toggle('active', days === 30);

    fetch(`/api/price-trend/${commodity}?state=${userState}&district=${userDistrict}&days=${days}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderTrendChart(data);
            } else {
                console.error('Trend data error:', data.error);
            }
        })
        .catch(error => console.error('Error fetching trend:', error));
}

function renderTrendChart(data) {
    const canvas = document.getElementById('priceTrendChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    const labels = data.trend_data.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    });

    const prices = data.trend_data.map(item => item.modal_price / 100); // per kg

    if (priceTrendChart) {
        priceTrendChart.destroy();
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, 180);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0)');

    priceTrendChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `${data.commodity} Price`,
                data: prices,
                backgroundColor: gradient,
                borderColor: '#10b981',
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: '#10b981',
                hoverBorderColor: '#fff',
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1e293b',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return `Price: ₹${context.raw.toFixed(2)}/kg`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false, drawBorder: false },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                        font: { size: 10 },
                        maxRotation: 0
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                        font: { size: 10 },
                        callback: function (value) { return '₹' + value; }
                    }
                }
            }
        }
    });

    // Update summary info
    const nameEl = document.getElementById('trend-commodity-name');
    if (nameEl) nameEl.textContent = data.commodity;

    const locationInfo = document.getElementById('trend-location-info');
    if (locationInfo) {
        if (data.data_level === 'district') {
            locationInfo.textContent = `Price analysis in ${userDistrict}`;
        } else if (data.data_level === 'state') {
            locationInfo.textContent = `Price analysis in ${userState} Avg`;
        } else {
            locationInfo.textContent = `Price analysis (National Avg)`;
        }
    }

    const dirEl = document.getElementById('trend-direction');
    const changeEl = document.getElementById('trend-change');
    const iconEl = document.getElementById('trend-direction-icon');
    const recEl = document.getElementById('trend-recommendation');

    if (dirEl) dirEl.textContent = data.analysis.direction;
    if (changeEl) {
        changeEl.textContent = (data.analysis.change_percent >= 0 ? '+' : '') + data.analysis.change_percent + '%';
    }

    if (iconEl && recEl) {
        if (data.analysis.direction === 'Rising') {
            iconEl.className = 'fas fa-arrow-trend-up';
            iconEl.style.color = '#10b981';
            if (changeEl) changeEl.style.color = '#10b981';
            recEl.innerHTML = '<span style="color: #ef4444; font-weight: 700;">Wait</span> - Price is increasing, consider selling after 3 days.';
        } else if (data.analysis.direction === 'Falling') {
            iconEl.className = 'fas fa-arrow-trend-down';
            iconEl.style.color = '#ef4444';
            if (changeEl) changeEl.style.color = '#ef4444';
            recEl.innerHTML = '<span style="color: #10b981; font-weight: 700;">Sell Now</span> - Price might drop further, sell today.';
        } else {
            iconEl.className = 'fas fa-arrows-left-right';
            iconEl.style.color = '#f97316';
            if (changeEl) changeEl.style.color = '#f97316';
            recEl.innerHTML = '<span style="color: #f97316; font-weight: 700;">Hold/Sell</span> - Price is stable, you can sell if needed.';
        }
    }
}

function viewTrend(commodity) {
    const select = document.getElementById('commodity-select');
    if (select) select.value = commodity;

    const nameEl = document.getElementById('trend-commodity-name');
    if (nameEl) nameEl.textContent = commodity;

    loadPriceTrend(commodity);
    const card = document.getElementById('trend-card');
    if (card) card.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Profile & Weather Modal
 */
function openProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) modal.style.display = 'flex';
}

function closeProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) modal.style.display = 'none';
}

function openWeatherModal() {
    const modal = document.getElementById('weatherModal');
    if (modal) modal.style.display = 'flex';
    fetchWeatherByLocation();
}

function closeWeatherModal() {
    const modal = document.getElementById('weatherModal');
    if (modal) modal.style.display = 'none';
}

function getWeatherIcon(code) {
    if (code === 0) return '☀️';
    if (code <= 3) return '⛅';
    if (code <= 48) return '🌫️';
    if (code <= 67) return '🌧️';
    if (code <= 77) return '🌨️';
    if (code <= 82) return '🌧️';
    if (code <= 86) return '❄️';
    if (code <= 99) return '⛈️';
    return '🌤️';
}

function displayWeather(data, locationName) {
    const current = data.current;
    const weatherIcon = getWeatherIcon(current.weather_code || 0);

    const content = document.getElementById('weatherModalContent');
    if (content) {
        content.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 64px;">${weatherIcon}</div>
                <h2 style="margin: 12px 0 4px 0;">${Math.round(current.temperature_2m)}°C</h2>
                <p style="color: var(--text-secondary); margin: 0;">${locationName || 'Current Location'}</p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px;">
                    <div style="padding: 16px; background: var(--body-bg); border-radius: 8px;">
                        <div style="font-size: 24px;">💧</div>
                        <div style="font-weight: 700;">${current.relative_humidity_2m}%</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Humidity</div>
                    </div>
                    <div style="padding: 16px; background: var(--body-bg); border-radius: 8px;">
                        <div style="font-size: 24px;">💨</div>
                        <div style="font-weight: 700;">${Math.round(current.wind_speed_10m)} km/h</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Wind</div>
                    </div>
                    <div style="padding: 16px; background: var(--body-bg); border-radius: 8px;">
                        <div style="font-size: 24px;">👁️</div>
                        <div style="font-weight: 700;">${(current.visibility / 1000).toFixed(1)} km</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Visibility</div>
                    </div>
                </div>
            </div>
        `;
    }
}

function searchWeatherByCity() {
    const cityInput = document.getElementById('citySearchInput');
    const city = cityInput.value.trim();
    if (!city) {
        alert('Please enter a city name');
        return;
    }

    const content = document.getElementById('weatherModalContent');
    if (content) {
        content.innerHTML = `
            <div style="text-align: center; padding: 30px;">
                <div class="loading-spinner"></div>
                <p style="margin-top: 16px; color: var(--text-secondary);">Searching for ${city}...</p>
            </div>
        `;
    }

    fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`)
        .then(response => response.json())
        .then(geoData => {
            if (!geoData.results || geoData.results.length === 0) {
                if (content) {
                    content.innerHTML = `
                        <div style="text-align: center; padding: 30px; color: #dc2626;">
                            <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 16px;"></i>
                            <p>City not found. Please try another city name.</p>
                        </div>
                    `;
                }
                return;
            }

            const location = geoData.results[0];
            const locationName = `${location.name}${location.admin1 ? ', ' + location.admin1 : ''}${location.country ? ', ' + location.country : ''}`;

            fetch(`https://api.open-meteo.com/v1/forecast?latitude=${location.latitude}&longitude=${location.longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,visibility,weather_code&timezone=auto`)
                .then(response => response.json())
                .then(data => { displayWeather(data, locationName); })
                .catch(err => {
                    if (content) content.innerHTML = `<div style="text-align: center; padding: 30px; color: #dc2626;"><p>Error fetching weather data.</p></div>`;
                });
        })
        .catch(err => {
            if (content) content.innerHTML = `<div style="text-align: center; padding: 30px; color: #dc2626;"><p>Error searching for city.</p></div>`;
        });
}

function fetchWeatherByLocation() {
    const content = document.getElementById('weatherModalContent');
    if (content) {
        content.innerHTML = `
            <div style="text-align: center; padding: 30px;">
                <div class="loading-spinner"></div>
                <p style="margin-top: 16px; color: var(--text-secondary);">Getting your location...</p>
            </div>
        `;
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,visibility,weather_code&timezone=auto`)
                    .then(res => res.json())
                    .then(data => { displayWeather(data, 'Your Location'); })
                    .catch(() => { if (content) content.innerHTML = '<p>Error.</p>'; });
            },
            () => {
                if (content) {
                    content.innerHTML = `
                        <div style="text-align: center; padding: 30px; color: #dc2626;">
                            <i class="fas fa-location-arrow" style="font-size: 48px; margin-bottom: 16px;"></i>
                            <p>Please enable location access. Or search above.</p>
                        </div>
                    `;
                }
            }
        );
    }
}

/**
 * Calculators & Schemes
 */
function openCalculatorModal() {
    const modal = document.getElementById('calculatorModal');
    if (modal) modal.style.display = 'flex';
    const input = document.getElementById('entryDate');
    if (input && !input.value) {
        input.value = new Date().toISOString().split('T')[0];
    }
}

function closeCalculatorModal() {
    const modal = document.getElementById('calculatorModal');
    if (modal) modal.style.display = 'none';
}

function openGovtSchemesModal() {
    const modal = document.getElementById('govtSchemesModal');
    if (modal) modal.style.display = 'flex';
}

function closeGovtSchemesModal() {
    const modal = document.getElementById('govtSchemesModal');
    if (modal) modal.style.display = 'none';
}

function openEquipmentModal() {
    const modal = document.getElementById('equipmentModal');
    if (modal) modal.style.display = 'flex';
    fetchEquipmentings();
}

function closeEquipmentModal() {
    const modal = document.getElementById('equipmentModal');
    if (modal) modal.style.display = 'none';

    // Reset to view mode
    const form = document.getElementById('equipmentListingForm');
    const list = document.getElementById('equipmentListContainer');
    const btn = document.getElementById('toggleEquipFormBtn');
    if (form) form.style.display = 'none';
    if (list) list.style.display = 'grid';
    if (btn) btn.innerHTML = '<i class="fas fa-plus"></i> List Your Equipment';
}

function openFarmersManualModal() {
    const modal = document.getElementById('farmersManualModal');
    if (modal) modal.style.display = 'flex';
    showManualSection('soil');
}

function closeFarmersManualModal() {
    const modal = document.getElementById('farmersManualModal');
    if (modal) modal.style.display = 'none';
}

function showManualSection(sectionName) {
    document.querySelectorAll('.manual-section').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.manual-tab').forEach(t => {
        t.style.background = '#f1f5f9';
        t.style.color = '#64748b';
        t.classList.remove('active');
    });

    const sec = document.getElementById('section-' + sectionName);
    if (sec) sec.style.display = 'block';

    const tab = document.getElementById('tab-' + sectionName);
    if (tab) {
        tab.style.background = '#10b981';
        tab.style.color = 'white';
        tab.classList.add('active');
    }
}

/**
 * Equipment & Rentals
 */
function toggleEquipmentForm() {
    const form = document.getElementById('equipmentListingForm');
    const list = document.getElementById('equipmentListContainer');
    const btn = document.getElementById('toggleEquipFormBtn');
    const title = document.getElementById('equipmentModalTitle');
    const subtitle = document.getElementById('equipmentModalSubtitle');

    if (!form || !list || !btn) return;

    if (form.style.display === 'none') {
        form.style.display = 'block';
        list.style.display = 'none';
        btn.innerHTML = '<i class="fas fa-list"></i> View Listings';
        if (title) title.textContent = 'List Equipment';
        if (subtitle) subtitle.textContent = 'Help fellow farmers by sharing your machinery.';
    } else {
        form.style.display = 'none';
        list.style.display = 'grid';
        btn.innerHTML = '<i class="fas fa-plus"></i> List Your Equipment';
        if (title) title.textContent = 'Rent Farm Machinery';
        if (subtitle) subtitle.textContent = 'Connect with local farmers.';
        fetchEquipmentings();
    }
}

function fetchEquipmentings() {
    const container = document.getElementById('equipmentListContainer');
    if (!container) return;

    fetch('/api/equipment')
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px;"><h4>No equipment listed yet</h4></div>`;
                return;
            }

            container.innerHTML = data.map(item => {
                const isOwner = item.owner_id === currentUserId;
                let btnText = 'Rent Now';
                let btnDisabled = '';
                let btnStyle = '';

                if (isOwner) {
                    btnText = 'Your Listing';
                    btnDisabled = 'disabled';
                    btnStyle = 'background: #3b82f6; opacity: 0.8; cursor: default;';
                } else if (item.status === 'rented') {
                    btnText = 'Rented';
                    btnDisabled = 'disabled';
                    btnStyle = 'background: #94a3b8;';
                } else if (item.status === 'requested') {
                    btnText = 'Requested';
                    btnDisabled = 'disabled';
                    btnStyle = 'background: #f59e0b;';
                }

                return `
                    <div class="equipment-card">
                        <div class="equipment-image">
                            ${item.image_emoji || '🚜'} 
                            <div class="equipment-badge" style="background: ${item.status === 'available' ? '#dcfce7' : '#fee2e2'};">
                                ${item.status}
                            </div>
                        </div>
                        <div class="equipment-content">
                            <h4>${item.name}</h4>
                            <div><i class="fas fa-map-marker-alt"></i> ${item.location}</div>
                            <div class="equipment-stats">
                                <div>Rate: ₹${item.rate}/${item.rate_unit}</div>
                            </div>
                            <button class="rent-btn" onclick="rentEquipment('${item._id}')" ${btnDisabled} style="${btnStyle}">
                                ${btnText}
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        })
        .catch(() => { if (container) container.innerHTML = '<p>Error loading.</p>'; });
}

function submitEquipmentListing() {
    const submitBtn = document.querySelector('#addEquipmentForm button[type="submit"]');
    if (!submitBtn) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Listing...';

    const data = {
        name: document.getElementById('equipName').value,
        type: document.getElementById('equipType').value,
        rate: document.getElementById('equipRate').value,
        rate_unit: document.getElementById('equipRateUnit').value,
        description: document.getElementById('equipDesc').value,
        image_emoji: document.getElementById('equipType').value === 'Tractor' ? '🚜' : '🛠️'
    };

    fetch('/api/equipment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(res => {
            if (res.success) {
                showToast('Equipment listed!', 'success');
                const form = document.getElementById('addEquipmentForm');
                if (form) form.reset();
                toggleEquipmentForm();
            } else {
                showToast(res.error || 'Failed', 'error');
            }
        })
        .catch(() => showToast('Error', 'error'))
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'List Equipment';
        });
}

function rentEquipment(id) {
    if (!confirm('Are you sure you want to rent this equipment?')) return;
    fetch(`/api/equipment/${id}/rent`, { method: 'POST' })
        .then(res => res.json())
        .then(res => {
            if (res.success) {
                showToast('Rental request sent!', 'success');
                fetchEquipmentings();
            } else {
                showToast(res.error || 'Failed', 'error');
            }
        });
}

/**
 * Expense Benchmarks
 */
const cropBenchmarks = {
    rice: { seed: 2000, fertilizer: 6000, pesticide: 2500, total: 35000 },
    wheat: { seed: 1500, fertilizer: 5000, pesticide: 2000, total: 28000 },
    maize: { seed: 1500, fertilizer: 5000, pesticide: 2000, total: 30000 },
    cotton: { seed: 3000, fertilizer: 7000, pesticide: 4000, total: 42000 },
    sugarcane: { seed: 8000, fertilizer: 10000, pesticide: 3000, total: 60000 },
    tomato: { seed: 5000, fertilizer: 10000, pesticide: 5000, total: 60000 },
    potato: { seed: 15000, fertilizer: 8000, pesticide: 4000, total: 55000 },
    onion: { seed: 4000, fertilizer: 8000, pesticide: 3500, total: 50000 }
    // More benchmarks can be added here
};

function loadBenchmarkData() {
    const cropType = document.getElementById('cropType').value;
    const seedB = document.getElementById('seedBenchmark');
    const fertB = document.getElementById('fertilizerBenchmark');
    const pestB = document.getElementById('pesticideBenchmark');

    if (!cropType || !cropBenchmarks[cropType]) {
        if (seedB) seedB.textContent = '';
        if (fertB) fertB.textContent = '';
        if (pestB) pestB.textContent = '';
        return;
    }

    const b = cropBenchmarks[cropType];
    if (seedB) seedB.textContent = `Average: ₹${b.seed.toLocaleString('en-IN')}/acre`;
    if (fertB) fertB.textContent = `Average: ₹${b.fertilizer.toLocaleString('en-IN')}/acre`;
    if (pestB) pestB.textContent = `Average: ₹${b.pesticide.toLocaleString('en-IN')}/acre`;
}

function calculateTotal() {
    const getVal = id => parseFloat(document.getElementById(id)?.value) || 0;
    const expenses = {
        seed: getVal('seedCost'),
        fertilizer: getVal('fertilizerCost'),
        pesticide: getVal('pesticideCost'),
        irrigation: getVal('irrigationCost'),
        labor: getVal('laborCost'),
        machinery: getVal('machineryCost'),
        other: getVal('otherCost')
    };

    const total = Object.values(expenses).reduce((a, b) => a + b, 0);

    const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    setTxt('totalExpense', '₹' + total.toLocaleString('en-IN'));
    setTxt('seedDisplay', '₹' + expenses.seed.toLocaleString('en-IN'));
    setTxt('fertilizerDisplay', '₹' + expenses.fertilizer.toLocaleString('en-IN'));
    setTxt('pesticideDisplay', '₹' + expenses.pesticide.toLocaleString('en-IN'));
    setTxt('irrigationDisplay', '₹' + expenses.irrigation.toLocaleString('en-IN'));
    setTxt('laborDisplay', '₹' + expenses.labor.toLocaleString('en-IN'));
    setTxt('machineryDisplay', '₹' + expenses.machinery.toLocaleString('en-IN'));
    setTxt('otherDisplay', '₹' + expenses.other.toLocaleString('en-IN'));

    updateExpenseChart(Object.values(expenses));

    const area = getVal('landArea');
    if (area > 0) {
        const perAcre = total / area;
        setTxt('costPerAcre', '₹' + perAcre.toLocaleString('en-IN', { maximumFractionDigits: 2 }) + ' per acre');
    }

    const qty = getVal('expectedYield');
    const price = getVal('marketPrice');
    const revenue = qty * price;
    const profit = revenue - total;

    setTxt('totalRevenue', '₹' + revenue.toLocaleString('en-IN'));
    setTxt('netProfit', '₹' + profit.toLocaleString('en-IN'));
}

function updateExpenseChart(data) {
    const ctx = document.getElementById('expenseChart');
    if (!ctx || typeof Chart === 'undefined') return;

    if (expenseChart) expenseChart.destroy();

    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Seeds', 'Fertilizers', 'Pesticides', 'Irrigation', 'Labor', 'Machinery', 'Other'],
            datasets: [{
                data: data,
                backgroundColor: ['#4caf50', '#2196f3', '#ff9800', '#00bcd4', '#9c27b0', '#f44336', '#607d8b']
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

function calculateLoan() {
    const p = parseFloat(document.getElementById('loanAmount')?.value) || 0;
    const r = parseFloat(document.getElementById('interestRate')?.value) || 0;
    const m = parseFloat(document.getElementById('loanPeriod')?.value) || 0;

    if (p > 0 && r > 0 && m > 0) {
        const mr = (r / 12) / 100;
        const emi = (p * mr * Math.pow(1 + mr, m)) / (Math.pow(1 + mr, m) - 1);
        const total = emi * m;
        document.getElementById('monthlyEMI').textContent = '₹' + Math.round(emi).toLocaleString('en-IN');
        document.getElementById('totalAmount').textContent = '₹' + Math.round(total).toLocaleString('en-IN');
    }
}

async function saveExpenseEntry() {
    const getVal = id => parseFloat(document.getElementById(id)?.value) || 0;
    const entry = {
        date: document.getElementById('entryDate')?.value,
        cropType: document.getElementById('cropType')?.value,
        expenses: {
            seed: getVal('seedCost'),
            fertilizer: getVal('fertilizerCost'),
            pesticide: getVal('pesticideCost'),
            irrigation: getVal('irrigationCost'),
            labor: getVal('laborCost'),
            machinery: getVal('machineryCost'),
            other: getVal('otherCost')
        },
        landArea: getVal('landArea'),
        expectedYield: getVal('expectedYield'),
        marketPrice: getVal('marketPrice')
    };

    if (!entry.date) return alert('Date required');

    try {
        const res = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(entry)
        });
        const data = await res.json();
        if (data.success) alert('Saved!');
    } catch (e) { alert('Error saving.'); }
}

/**
 * PDF & Reports
 */
function openDownloadModal() {
    const modal = document.getElementById('downloadModal');
    if (modal) modal.style.display = 'flex';
}

function closeDownloadModal() {
    const modal = document.getElementById('downloadModal');
    if (modal) modal.style.display = 'none';
}

function exportToPDF() {
    if (typeof window.jspdf === 'undefined') return alert('Loading PDF lib...');
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.text('Farming Expense Report', 105, 20, { align: 'center' });
    doc.text(`Crop: ${document.getElementById('cropType')?.value}`, 20, 40);
    doc.text(`Total Expense: ${document.getElementById('totalExpense')?.textContent}`, 20, 50);
    doc.save('report.pdf');
}

async function generateReport(cardElement, reportName) {
    if (typeof html2pdf === 'undefined') return alert('Loading PDF library... Please try again in a moment.');

    cardElement.classList.add('report-loading');
    const btnIcon = cardElement.querySelector('i');
    const originalClass = btnIcon ? btnIcon.className : '';
    if (btnIcon) btnIcon.className = 'fas fa-spinner fa-spin';

    try {
        let endpoint = '';
        if (reportName === 'Crop Plan PDF') endpoint = '/api/report/crop-plan';
        else if (reportName === 'Harvest Report') endpoint = '/api/report/harvest';
        else if (reportName === 'Profit Summary') endpoint = '/api/report/profit';
        else if (reportName === 'Market Report') endpoint = '/api/report/market-watch';
        else if (reportName === 'Weather Report') endpoint = '/api/report/weather';

        const res = await fetch(endpoint);
        const result = await res.json();

        if (!result.success) throw new Error(result.message);

        // --- Build Rich HTML Content ---
        const data = result.data;
        const user = data.user;
        const dateStr = new Date().toLocaleDateString('en-GB');

        // Base Wrapper
        let htmlContent = `
            <div style="font-family: 'Segoe UI', sans-serif; background: white; padding: 25px; max-width: 625px; margin: 0 auto; box-sizing: border-box;">
                <!-- Common Top Header -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #047857; margin: 0; font-size: 28px; font-weight: 600;">${reportName}</h1>
                    <div style="color: #64748b; font-size: 14px; margin-top: 10px; line-height: 1.6;">
                        <div>Generated on: ${dateStr}</div>
                        <div>Farmer: ${user.name.toUpperCase()}</div>
                        <div>Location: ${user.district}, ${user.state}</div>
                    </div>
                </div>
        `;

        if (reportName === 'Crop Plan PDF') {
            const activeCrops = data.crops.length;
            const avgProgress = Math.round(data.crops.reduce((acc, c) => acc + c.progress, 0) / (activeCrops || 1));

            htmlContent += `
                <!-- Dark Blue Header -->
                <div style="background: #1e3a8a; color: white; padding: 15px; text-align: center; margin-bottom: 30px; border-radius: 4px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 1px;">CROP CULTIVATION PLAN</h2>
                </div>

                <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">
                    Detailed cultivation schedule and status report for active crops.
                </p>

                <!-- 3 Cards Row -->
                <div style="display: flex; gap: 20px; margin-bottom: 40px;">
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">TOTAL CROPS</div>
                        <div style="font-size: 32px; font-weight: 700;">${activeCrops}</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">AVG PROGRESS</div>
                        <div style="font-size: 32px; font-weight: 700;">${avgProgress}%</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">ACTIVE STAGES</div>
                        <div style="font-size: 32px; font-weight: 700;">${activeCrops}</div>
                    </div>
                </div>

                <!-- Table -->
                <h3 style="color: #1e293b; font-size: 16px; margin-bottom: 15px;">Active Crop Status:</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px;">
                    <thead>
                        <tr style="background: #0f172a; color: white; text-transform: uppercase;">
                            <th style="padding: 8px; text-align: left;">Crop</th>
                            <th style="padding: 8px; text-align: left;">Stage</th>
                            <th style="padding: 8px; text-align: center;">Progress</th>
                            <th style="padding: 8px; text-align: center;">Started</th>
                            <th style="padding: 8px; text-align: left;">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.crops.map((c, i) => `
                            <tr style="border-bottom: 1px solid #e2e8f0; page-break-inside: avoid; background: ${i % 2 === 0 ? '#fff' : '#f8fafc'};">
                                <td style="padding: 8px; font-weight: 600; color: #475569;">${c.crop}</td>
                                <td style="padding: 8px; color: #334155;">${c.stage}</td>
                                <td style="padding: 8px; text-align: center;">
                                    <div style="background: #e2e8f0; height: 6px; width: 60px; margin: 0 auto; border-radius: 3px; overflow: hidden;">
                                        <div style="background: #10b981; width: ${c.progress}%; height: 100%;"></div>
                                    </div>
                                    <span style="font-size: 10px; color: #64748b;">${c.progress}%</span>
                                </td>
                                <td style="padding: 8px; text-align: center; color: #64748b;">${c.started}</td>
                                <td style="padding: 8px; color: #64748b; font-style: italic;">${c.notes || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <!-- Advisory Section -->
                <h3 style="color: #2563eb; font-size: 14px; text-transform: uppercase; margin-bottom: 10px;">AGRONOMIST NOTES:</h3>
                <div style="border: 2px solid #2563eb; background: #eff6ff; border-radius: 8px; padding: 20px;">
                    <p style="margin: 0; color: #334155; line-height: 1.6; font-size: 13px;">
                        <strong>[GENERAL ADVICE]</strong> Regular monitoring of crop stages is crucial. Ensure irrigation aligns with changes in crop water requirements as they progress.
                    </p>
                </div>
             `;

        } else if (reportName === 'Harvest Report') {
            const readyCount = data.crops.filter(c => c.progress >= 90).length;
            const upcomingCount = data.crops.length - readyCount;

            htmlContent += `
                <!-- Dark Blue Header -->
                <div style="background: #1e3a8a; color: white; padding: 15px; text-align: center; margin-bottom: 30px; border-radius: 4px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 1px;">HARVEST SCHEDULE & ESTIMATES</h2>
                </div>

                <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">
                    Estimated harvest windows and yield projections.
                </p>

                <!-- 3 Cards Row -->
                <div style="display: flex; gap: 20px; margin-bottom: 40px;">
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">READY TO HARVEST</div>
                        <div style="font-size: 32px; font-weight: 700;">${readyCount}</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">UPCOMING</div>
                        <div style="font-size: 32px; font-weight: 700;">${upcomingCount}</div>
                    </div>
                </div>

                <!-- Table -->
                <h3 style="color: #1e293b; font-size: 16px; margin-bottom: 15px;">Harvest Schedule:</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px;">
                    <thead>
                        <tr style="background: #0f172a; color: white; text-transform: uppercase;">
                            <th style="padding: 8px; text-align: left;">Crop</th>
                            <th style="padding: 8px; text-align: left;">Stage</th>
                            <th style="padding: 8px; text-align: left;">Estimated Yield</th>
                            <th style="padding: 8px; text-align: left;">Harvest Window</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.crops.map((c, i) => `
                            <tr style="border-bottom: 1px solid #e2e8f0; page-break-inside: avoid; background: ${i % 2 === 0 ? '#fff' : '#f8fafc'};">
                                <td style="padding: 8px; font-weight: 600; color: #475569;">${c.crop}</td>
                                <td style="padding: 8px; color: #334155;">${c.stage}</td>
                                <td style="padding: 8px; font-weight: 600; color: #15803d;">${c.estimated_yield}</td>
                                <td style="padding: 8px; color: #b91c1c; font-weight: 500;">${c.harvest_window}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <!-- Advisory Section -->
                <h3 style="color: #2563eb; font-size: 14px; text-transform: uppercase; margin-bottom: 10px;">HARVEST ADVISORY:</h3>
                <div style="border: 2px solid #2563eb; background: #eff6ff; border-radius: 8px; padding: 20px;">
                    <p style="margin: 0; color: #334155; line-height: 1.6; font-size: 13px;">
                        <strong>[POST-HARVEST]</strong> Plan for proper storage and transport immediately after harvest to minimize losses. Check market prices before selling.
                    </p>
                </div>
             `;

        } else if (reportName === 'Profit Summary') {
            htmlContent += `
                <!-- Dark Blue Header -->
                <div style="background: #1e3a8a; color: white; padding: 15px; text-align: center; margin-bottom: 30px; border-radius: 4px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 1px;">FINANCIAL PERFORMANCE REPORT</h2>
                </div>

                <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">
                    Overview of expenses, revenue, and profitability.
                </p>

                <!-- 3 Cards Row -->
                <div style="display: flex; gap: 20px; margin-bottom: 40px;">
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">REVENUE</div>
                        <div style="font-size: 24px; font-weight: 700;">₹${data.total_revenue.toLocaleString()}</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">EXPENSE</div>
                        <div style="font-size: 24px; font-weight: 700;">₹${data.total_expenses.toLocaleString()}</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">NET PROFIT</div>
                        <div style="font-size: 24px; font-weight: 700;">₹${data.net_profit.toLocaleString()}</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">ROI</div>
                        <div style="font-size: 24px; font-weight: 700;">${data.roi}%</div>
                    </div>
                </div>

                <!-- Table -->
                <h3 style="color: #1e293b; font-size: 16px; margin-bottom: 15px;">Crop-wise Financial Breakdown:</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px;">
                    <thead>
                        <tr style="background: #0f172a; color: white; text-transform: uppercase;">
                            <th style="padding: 8px; text-align: left;">Crop</th>
                            <th style="padding: 8px; text-align: right;">Revenue</th>
                            <th style="padding: 8px; text-align: right;">Expenses</th>
                            <th style="padding: 8px; text-align: right;">Profit</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(data.crop_wise).map(([crop, val], i) => `
                            <tr style="border-bottom: 1px solid #e2e8f0; page-break-inside: avoid; background: ${i % 2 === 0 ? '#fff' : '#f8fafc'};">
                                <td style="padding: 8px; font-weight: 600; color: #475569;">${crop}</td>
                                <td style="padding: 8px; text-align: right; color: #166534;">₹${val.revenue.toLocaleString()}</td>
                                <td style="padding: 8px; text-align: right; color: #991b1b;">₹${val.expenses.toLocaleString()}</td>
                                <td style="padding: 8px; text-align: right; font-weight: 600; color: ${(val.revenue - val.expenses) >= 0 ? '#15803d' : '#b91c1c'};">
                                    ₹${(val.revenue - val.expenses).toLocaleString()}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <!-- Advisory Section -->
                <h3 style="color: #2563eb; font-size: 14px; text-transform: uppercase; margin-bottom: 10px;">FINANCIAL ADVISORY:</h3>
                <div style="border: 2px solid #2563eb; background: #eff6ff; border-radius: 8px; padding: 20px;">
                    <p style="margin: 0; color: #334155; line-height: 1.6; font-size: 13px;">
                        <strong>[ANALYSIS]</strong> Review crops with low ROI. Consider reducing input costs through bulk purchasing or optimizing fertilizer usage.
                    </p>
                </div>
            `;

        } else if (reportName === 'Market Report') {
            const prices = data.prices;
            const maxPrice = Math.max(...prices.map(p => p.modal_price));
            const minPrice = Math.min(...prices.map(p => p.modal_price));

            htmlContent += `
                <!-- Dark Blue Header -->
                <div style="background: #1e3a8a; color: white; padding: 15px; text-align: center; margin-bottom: 30px; border-radius: 4px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 1px;">MARKET INTELLIGENCE REPORT</h2>
                </div>

                <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">
                    Real-time commodity prices and market trends in ${user.district}.
                </p>

                <!-- 3 Cards Row -->
                <div style="display: flex; gap: 20px; margin-bottom: 40px;">
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">COMMODITIES</div>
                        <div style="font-size: 32px; font-weight: 700;">${prices.length}</div>
                    </div>
                     <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">HIGHEST PRICE</div>
                        <div style="font-size: 32px; font-weight: 700;">₹${maxPrice}</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">LOWEST PRICE</div>
                        <div style="font-size: 32px; font-weight: 700;">₹${minPrice}</div>
                    </div>
                </div>

                <!-- Table -->
                <h3 style="color: #1e293b; font-size: 16px; margin-bottom: 15px;">Commodity Prices:</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px;">
                    <thead>
                        <tr style="background: #0f172a; color: white; text-transform: uppercase;">
                            <th style="padding: 8px; text-align: left;">Commodity</th>
                            <th style="padding: 8px; text-align: right;">Modal Price</th>
                            <th style="padding: 8px; text-align: right;">Min Price</th>
                            <th style="padding: 8px; text-align: right;">Max Price</th>
                            <th style="padding: 8px; text-align: right;">Market</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${prices.map((item, i) => `
                            <tr style="border-bottom: 1px solid #e2e8f0; page-break-inside: avoid; background: ${i % 2 === 0 ? '#fff' : '#f8fafc'};">
                                <td style="padding: 8px; font-weight: 600; color: #475569;">${item.commodity}</td>
                                <td style="padding: 8px; text-align: right; font-weight: 700; color: #1e293b;">₹${item.modal_price}</td>
                                <td style="padding: 8px; text-align: right; color: #64748b;">₹${item.min_price}</td>
                                <td style="padding: 8px; text-align: right; color: #64748b;">₹${item.max_price}</td>
                                <td style="padding: 8px; text-align: right; color: #475569; font-size: 10px;">${item.market}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                 <!-- Advisory Section -->
                <h3 style="color: #2563eb; font-size: 14px; text-transform: uppercase; margin-bottom: 10px;">MARKET ADVISORY:</h3>
                <div style="border: 2px solid #2563eb; background: #eff6ff; border-radius: 8px; padding: 20px;">
                    <p style="margin: 0; color: #334155; line-height: 1.6; font-size: 13px;">
                        <strong>[STRATEGY]</strong> Prices fluctuate daily. It is advisable to sell when prices are stable or rising. Check trend graphs for detailed 30-day analysis.
                    </p>
                </div>
            `;

        } else if (reportName === 'Weather Report') {
            const today = data.weather.current;
            const forecast = data.weather.forecast || [];

            // Helper for moon phase (mock logic for visual completeness)
            const phases = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'];
            const getPhase = (i) => phases[i % 8];

            htmlContent += `
                <!-- Dark Blue Header -->
                <div style="background: #1e3a8a; color: white; padding: 15px; text-align: center; margin-bottom: 30px; border-radius: 4px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 1px;">METEOROLOGICAL ADVISORY DASHBOARD</h2>
                </div>

                <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">
                    7-day agricultural forecast and field advisories for ${user.district}.
                </p>

                <!-- 3 Cards Row -->
                <div style="display: flex; gap: 20px; margin-bottom: 40px;">
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">CURRENT TEMP</div>
                        <div style="font-size: 32px; font-weight: 700;">${Math.round(today.temperature)}°C</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">HUMIDITY</div>
                        <div style="font-size: 32px; font-weight: 700;">${today.humidity}%</div>
                    </div>
                    <div style="flex: 1; background: #2563eb; color: white; padding: 25px 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.9;">WIND SPEED</div>
                        <div style="font-size: 32px; font-weight: 700;">${today.wind_speed} KM/H</div>
                    </div>
                </div>

                <!-- Forecast Table -->
                <h3 style="color: #1e293b; font-size: 16px; margin-bottom: 15px;">7-Day Daily Forecast:</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px;">
                    <thead>
                        <tr style="background: #0f172a; color: white; text-transform: uppercase;">
                            <th style="padding: 8px; text-align: left;">DAY</th>
                            <th style="padding: 8px; text-align: left;">CONDITION</th>
                            <th style="padding: 8px; text-align: center;">TEMP (L/H)</th>
                            <th style="padding: 8px; text-align: center;">UV/RAIN</th>
                            <th style="padding: 8px; text-align: left;">MOON PHASE</th>
                            <th style="padding: 8px; text-align: right;">WIND</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${forecast.map((day, index) => `
                            <tr style="border-bottom: 1px solid #e2e8f0; page-break-inside: avoid; background: ${index % 2 === 0 ? '#fff' : '#f8fafc'};">
                                <td style="padding: 8px; font-weight: 600; color: #475569;">
                                    ${index === 0 ? 'TODAY' : (index === 1 ? 'TOMORROW' : `DAY ${index + 1}`)}
                                </td>
                                <td style="padding: 8px; color: #334155;">
                                    ${day.code <= 3 ? 'Sunny/Clear' : (day.code <= 60 ? 'Cloudy' : 'Rain/Showers')}
                                </td>
                                <td style="padding: 8px; text-align: center; font-weight: 600;">
                                    ${Math.round(day.temp_min)}°C - ${Math.round(day.temp_max)}°C
                                </td>
                                <td style="padding: 8px; text-align: center; color: #64748b;">
                                    UV ${Math.floor(Math.random() * 5) + 1} / ${day.precipitation || 0}%
                                </td>
                                <td style="padding: 8px; color: #475569;">
                                    ${getPhase(new Date().getDate() + index)}
                                </td>
                                <td style="padding: 8px; text-align: right; color: #475569;">
                                    ${Math.round(day.wind_max || 12)}kph
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <!-- Advisory Section -->
                <h3 style="color: #2563eb; font-size: 14px; text-transform: uppercase; margin-bottom: 10px;">FIELD-LEVEL AGRICULTURAL ADVISORY:</h3>
                <div style="border: 2px solid #2563eb; background: #eff6ff; border-radius: 8px; padding: 20px;">
                    <p style="margin: 0; color: #334155; line-height: 1.6; font-size: 13px;">
                        <strong>[GENERAL ADVICE]</strong> Favorable conditions for field operations. Maintain standard irrigation schedules. Monitor for pest activity given the humidity levels.
                        <br><br>
                        <strong>[CROP SPECIFIC]</strong> Ensure proper drainage if rain is expected. Apply fertilizers during clear sky windows for maximum efficiency.
                    </p>
                </div>
            `;
        } else {
            htmlContent += `
                <div style="margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 20px; text-align: center; color: #94a3b8; font-size: 12px;">
                    <p>Generated by Smart Farming Assistant • helping farmers grow better</p>
                </div>
            `;
        }

        htmlContent += `
                <div style="margin-top: 60px; text-align: center; color: #94a3b8; font-size: 10px;">
                    Smart Farming Assistant - Generated via User Dashboard
                </div>
            `;

        // Generate PDF
        const element = document.createElement('div');
        element.innerHTML = htmlContent;
        // Adjusted width to prevent cutoff on right side (A4 is ~794px at 96dpi, but margins eat in)
        // 750px was still too wide. 625px is safer (794 - 96 = 698 max).
        element.style.width = '625px';

        const opt = {
            margin: [0.5, 0.5, 0.5, 0.5], // standard margins
            filename: `${reportName.toLowerCase().replace(/ /g, '_')}_${Date.now()}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
        };

        await html2pdf().set(opt).from(element).save();

        showToast('Report Generated Successfully!', 'success');

        const storageKey = 'last_gen_' + reportName.toLowerCase().replace(/ /g, '-');
        localStorage.setItem(storageKey, Date.now());
        updateLastGeneratedDates();

    } catch (e) {
        console.error(e);
        showToast(e.message || 'Error generating report', 'error');
    } finally {
        cardElement.classList.remove('report-loading');
        if (btnIcon) btnIcon.className = originalClass;
    }
}

function updateLastGeneratedDates() {
    const reportIds = ['crop-plan-pdf', 'harvest-report', 'profit-summary', 'market-report', 'weather-report'];
    reportIds.forEach(id => {
        const timestamp = localStorage.getItem(`last_gen_${id}`);
        const element = document.getElementById(`last-gen-${id}`);
        if (timestamp && element) {
            const diffDays = Math.floor((Date.now() - parseInt(timestamp)) / (1000 * 60 * 60 * 24));
            element.textContent = diffDays === 0 ? 'Last Generated: Today' : `Last Generated: ${diffDays} days ago`;
        }
    });
}

function resetCalculator() {
    ['seedCost', 'fertilizerCost', 'pesticideCost', 'irrigationCost', 'laborCost', 'machineryCost', 'otherCost', 'landArea', 'expectedYield', 'marketPrice'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    calculateTotal();
}

/**
 * Weather Refresh
 */
function refreshWeather() {
    const card = document.querySelector('.weather-card');
    if (card) card.style.opacity = '0.7';

    fetch('/api/weather-update')
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            const c = data.current;
            const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
            set('weather-temp', Math.round(c.temperature) + '°C');
            set('weather-humidity', c.humidity + '%');
            set('weather-wind', c.wind_speed + ' km/h');
            set('weather-desc', c.condition);
            set('weather-location', c.location);
            const icon = document.querySelector('.weather-icon-large');
            if (icon) icon.textContent = c.icon;
            if (card) card.style.opacity = '1';
        })
        .catch(() => { });
}

// Global Initialization
document.addEventListener('DOMContentLoaded', function () {
    // Sidebar Links Interaction
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function () {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Populate Commodity Select
    const commodities = [
        "Potato", "Tomato", "Onion", "Carrot", "Cabbage", "Cauliflower", "Spinach",
        "Brinjal", "Lady's Finger", "Apple", "Banana", "Mango", "Orange", "Wheat", "Rice"
    ];
    const select = document.getElementById('commodity-select');
    if (select) {
        commodities.sort().forEach(c => {
            const opt = document.createElement('option');
            opt.value = c; opt.textContent = c; opt.style.color = "#1e293b";
            select.appendChild(opt);
        });

        const def = dashboardData.defaultCommodity || 'Tomato';
        select.value = def;
        setTimeout(() => loadPriceTrend(def), 1000);
    }

    // Reports & Weather
    updateLastGeneratedDates();
    refreshWeather();
    setInterval(refreshWeather, 15 * 60 * 1000);

    // Form Submits
    const editForm = document.getElementById('editCropForm');
    if (editForm) {
        editForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const id = document.getElementById('editCropId').value;
            const body = {
                stage: document.getElementById('editCropStage').value,
                notes: document.getElementById('editCropNotes').value
            };
            fetch('/growing/update/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            }).then(r => r.json()).then(d => { if (d.success) location.reload(); });
        });
    }
});

// Expose to Window for Inline HTML Handlers
Object.assign(window, {
    toggleSidebar, handleCropView, handleCropEdit, handleFertilizerView,
    openCropViewModal, closeCropViewModal, openCropEditModal, closeCropEditModal,
    openFertilizerViewModal, closeFertilizerViewModal, openAmazonLink, openIndiamartLink,
    toggleBuyDropdown, deleteCropActivity, deleteFertilizer, toggleChatbot, openChatbotModal,
    loadPriceTrend, viewTrend, handleChatKeypress, sendChatMessage, openProfileModal,
    closeProfileModal, openWeatherModal, closeWeatherModal, searchWeatherByCity,
    fetchWeatherByLocation, openCalculatorModal, closeCalculatorModal, openGovtSchemesModal,
    closeGovtSchemesModal, openEquipmentModal, closeEquipmentModal, openFarmersManualModal,
    closeFarmersManualModal, showManualSection, toggleEquipmentForm, submitEquipmentListing,
    rentEquipment, loadBenchmarkData, calculateTotal, calculateLoan, saveExpenseEntry,
    openDownloadModal, closeDownloadModal, exportToPDF, generateReport, resetCalculator,
    refreshWeather
});
