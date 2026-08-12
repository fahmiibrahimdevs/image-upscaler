document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const upscaleForm = document.getElementById('upscaleForm');
    const btnProcess = document.getElementById('btnProcess');
    
    // Display Containers
    const comparatorContainer = document.getElementById('comparatorContainer');
    const splitViewContainer = document.getElementById('splitViewContainer');
    const sideViewContainer = document.getElementById('sideViewContainer');
    
    // Images
    const imgBefore = document.getElementById('imgBefore');
    const imgAfter = document.getElementById('imgAfter');
    const imgSideBefore = document.getElementById('imgSideBefore');
    const imgSideAfter = document.getElementById('imgSideAfter');
    
    // Slider & Clip Layers
    const comparatorCanvas = document.getElementById('comparatorCanvas');
    const afterClippedLayer = document.getElementById('afterClippedLayer');
    const sliderDivider = document.getElementById('sliderDivider');
    
    // View Modes & Buttons
    const btnModeSplit = document.getElementById('btnModeSplit');
    const btnModeSide = document.getElementById('btnModeSide');
    const btnNewImage = document.getElementById('btnNewImage');
    const btnDownload = document.getElementById('btnDownload');
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    const processingIndicator = document.getElementById('processingIndicator');
    const statTime = document.getElementById('statTime');
    const statFile = document.getElementById('statFile');

    // Controls
    const presetSelect = document.getElementById('preset');
    const sharpnessSlider = document.getElementById('sharpness');
    const edgeBoostSlider = document.getElementById('edge_boost');
    const contrastSlider = document.getElementById('contrast');
    const denoiseSlider = document.getElementById('denoise');
    const binarizeToggle = document.getElementById('binarize');
    const scaleRadios = document.querySelectorAll('input[name="scale_factor"]');

    const sharpnessVal = document.getElementById('sharpnessVal');
    const edgeBoostVal = document.getElementById('edgeBoostVal');
    const contrastVal = document.getElementById('contrastVal');
    const denoiseVal = document.getElementById('denoiseVal');

    let currentFile = null;
    let autoUpdateTimer = null;
    let currentViewMode = 'split';

    // Helper: Update Numerical Badge Labels
    function updateBadgeLabels() {
        sharpnessVal.textContent = sharpnessSlider.value;
        edgeBoostVal.textContent = edgeBoostSlider.value;
        contrastVal.textContent = contrastSlider.value;
        denoiseVal.textContent = denoiseSlider.value;
    }

    // Real-Time Debounced Auto-Update
    function triggerAutoUpdate() {
        updateBadgeLabels();
        if (!currentFile) return;

        clearTimeout(autoUpdateTimer);
        processingIndicator.classList.remove('hidden');

        autoUpdateTimer = setTimeout(() => {
            processUpscale(false);
        }, 350); // 350ms debounce
    }

    // Listen to changes on all controls for Real-Time Update
    [sharpnessSlider, edgeBoostSlider, contrastSlider, denoiseSlider].forEach(slider => {
        slider.addEventListener('input', triggerAutoUpdate);
    });

    binarizeToggle.addEventListener('change', triggerAutoUpdate);
    scaleRadios.forEach(radio => radio.addEventListener('change', triggerAutoUpdate));

    // Preset Selection Auto-Configuration
    presetSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'text_focus') {
            sharpnessSlider.value = 2.4;
            edgeBoostSlider.value = 2.0;
            contrastSlider.value = 1.35;
            denoiseSlider.value = 1.0;
            binarizeToggle.checked = false;
        } else if (val === 'hybrid_photo_text') {
            sharpnessSlider.value = 1.6;
            edgeBoostSlider.value = 1.2;
            contrastSlider.value = 1.15;
            denoiseSlider.value = 0.8;
            binarizeToggle.checked = false;
        } else if (val === 'binarized_text') {
            sharpnessSlider.value = 2.8;
            edgeBoostSlider.value = 2.0;
            contrastSlider.value = 1.5;
            denoiseSlider.value = 1.0;
            binarizeToggle.checked = true;
        }
        triggerAutoUpdate();
    });

    // Drag & Drop File Handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            alert('Silakan pilih file gambar yang valid (PNG, JPG, WEBP).');
            return;
        }

        currentFile = file;
        statFile.textContent = file.name;

        // Preview original image immediately in all views
        const reader = new FileReader();
        reader.onload = (evt) => {
            imgBefore.src = evt.target.result;
            imgAfter.src = evt.target.result;
            imgSideBefore.src = evt.target.result;
            imgSideAfter.src = evt.target.result;

            dropzone.classList.add('hidden');
            comparatorContainer.classList.remove('hidden');

            // Immediately trigger upscale processing for instant results!
            processUpscale(true);
        };
        reader.readAsDataURL(file);
    }

    btnNewImage.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        comparatorContainer.classList.add('hidden');
        dropzone.classList.remove('hidden');
    });

    // Upscale API Request Function
    async function processUpscale(showFullOverlay = false) {
        if (!currentFile) return;

        if (showFullOverlay) {
            loadingOverlay.classList.remove('hidden');
        } else {
            processingIndicator.classList.remove('hidden');
        }

        const formData = new FormData(upscaleForm);
        formData.append('image', currentFile);

        try {
            const response = await fetch('/api/upscale', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Update images for both split & side-by-side views
                imgBefore.src = data.original_image;
                imgAfter.src = data.processed_image;
                imgSideBefore.src = data.original_image;
                imgSideAfter.src = data.processed_image;

                // Download link setup
                btnDownload.href = data.processed_image;
                btnDownload.download = `sharp_${data.filename.replace(/\.[^/.]+$/, '')}.png`;

                // Stats setup
                statTime.textContent = data.processing_time;
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (err) {
            console.error(err);
        } finally {
            loadingOverlay.classList.add('hidden');
            processingIndicator.classList.add('hidden');
        }
    }

    upscaleForm.addEventListener('submit', (e) => {
        e.preventDefault();
        processUpscale(true);
    });

    // Clip-Path Split Slider Dragging Mechanism
    let isDragging = false;

    function setSliderPosition(percentage) {
        percentage = Math.max(0, Math.min(100, percentage));
        // Clip polygon: clipped top layer shows right side from X% to 100%
        afterClippedLayer.style.clipPath = `polygon(${percentage}% 0, 100% 0, 100% 100%, ${percentage}% 100%)`;
        sliderDivider.style.left = `${percentage}%`;
    }

    function handleMove(clientX) {
        if (!isDragging) return;
        const rect = comparatorCanvas.getBoundingClientRect();
        const offsetX = clientX - rect.left;
        const percentage = (offsetX / rect.width) * 100;
        setSliderPosition(percentage);
    }

    sliderDivider.addEventListener('mousedown', (e) => {
        isDragging = true;
        e.preventDefault();
    });

    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', (e) => handleMove(e.clientX));

    // Touch Support for mobile & tablets
    sliderDivider.addEventListener('touchstart', (e) => {
        isDragging = true;
    });

    window.addEventListener('touchend', () => isDragging = false);
    window.addEventListener('touchmove', (e) => {
        if (isDragging && e.touches.length > 0) {
            handleMove(e.touches[0].clientX);
        }
    });

    // Click anywhere on canvas to jump slider handle to that position
    comparatorCanvas.addEventListener('click', (e) => {
        const rect = comparatorCanvas.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const percentage = (offsetX / rect.width) * 100;
        setSliderPosition(percentage);
    });

    // View Mode Switcher Logic
    btnModeSplit.addEventListener('click', () => {
        currentViewMode = 'split';
        btnModeSplit.classList.add('active');
        btnModeSide.classList.remove('active');
        splitViewContainer.classList.remove('hidden');
        sideViewContainer.classList.add('hidden');
    });

    btnModeSide.addEventListener('click', () => {
        currentViewMode = 'side';
        btnModeSide.classList.add('active');
        btnModeSplit.classList.remove('active');
        sideViewContainer.classList.remove('hidden');
        splitViewContainer.classList.add('hidden');
    });

    // Initial default position: 50% split
    setSliderPosition(50);
});
