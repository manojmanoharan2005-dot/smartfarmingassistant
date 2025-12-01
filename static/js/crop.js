document.addEventListener('DOMContentLoaded', function() {
    const cropForm = document.getElementById('cropForm');
    const stateSelect = document.getElementById('state');
    const districtSelect = document.getElementById('district');
    
    // Load states and districts
    if (stateSelect) {
        loadStatesAndDistricts();
    }
    
    if (cropForm) {
        cropForm.addEventListener('submit', handleCropSubmission);
    }
});

function loadStatesAndDistricts() {
    fetch('/static/data/states_districts.json')
        .then(response => response.json())
        .then(data => {
            populateStates(data);
        });
}

function handleCropSubmission(e) {
    e.preventDefault();
    // Handle form submission
    console.log('Submitting crop recommendation form...');
}
