document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('diseaseImage');
    const imagePreview = document.getElementById('imagePreview');
    const uploadForm = document.getElementById('diseaseForm');
    
    if (fileInput) {
        fileInput.addEventListener('change', handleImageUpload);
    }
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleDiseaseDetection);
    }
});

function handleImageUpload(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'image-preview';
            
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = '';
            preview.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
}

function handleDiseaseDetection(e) {
    e.preventDefault();
    console.log('Processing disease detection...');
}
