function updateDistricts() {
    const statesDistrictsData = JSON.parse(document.getElementById('states-districts-data').textContent);
    const stateSelect = document.getElementById('state');
    const districtSelect = document.getElementById('district');
    const selectedState = stateSelect.value;

    districtSelect.innerHTML = '<option value="">Select your district</option>';

    if (selectedState && statesDistrictsData[selectedState]) {
        statesDistrictsData[selectedState].forEach(function (district) {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtSelect.appendChild(option);
        });
    }
}

// Globalize for safety
window.updateDistricts = updateDistricts;
