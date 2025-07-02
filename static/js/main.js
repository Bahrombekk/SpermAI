// static/js/main.js
document.getElementById('fileInput').addEventListener('change', function(e) {
    if (!e.target.files[0]) {
        alert('Iltimos, rasm faylini tanlang!');
        return;
    }

    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const placeholder = document.querySelector('.image-placeholder');
        placeholder.innerHTML = 
            `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 10px;">`;
        console.log('Image preview loaded');
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('file', file);
    const analyzeBtn = document.querySelector('.btn-primary');

    analyzeBtn.innerHTML = '⏳ Tahlil qilinmoqda...';
    analyzeBtn.disabled = true;

    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server xatosi: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received data:', data);
        if (data.error) {
            throw new Error(data.message);
        }

        // Update stats panel - TUZATILGAN QISM
        const statsItems = document.querySelectorAll('.stats-panel .stat-item');
        
        // Hayotiy holat bo'yicha (0,1,2-indexlar)
        statsItems[0].querySelector('.stat-value').textContent = `${data.stats.Live || 0} ta`;
        statsItems[1].querySelector('.stat-value').textContent = `${data.stats.Dead || 0} ta`;
        statsItems[2].querySelector('.stat-value').textContent = `${data.stats.Immature || 0} ta`;

        const totalCells = data.total_cells || 0;
        console.log('Total cells:', totalCells);
        console.log('Classification data:', data.classification);
        
        // Tiriklar orasida tasnif (3,4,5-indexlar) - TUZATILGAN
        const normalCount = data.classification.Normal || 0;
        const abnormalCount = data.classification.Abnormal || 0;
        const otherCount = data.classification.Other || 0;
        
        console.log(`Normal: ${normalCount}, Abnormal: ${abnormalCount}, Other: ${otherCount}`);
        
        // Foizlarni hisoblash
        const normalPercent = totalCells > 0 ? ((normalCount / totalCells) * 100).toFixed(1) : 0;
        const abnormalPercent = totalCells > 0 ? ((abnormalCount / totalCells) * 100).toFixed(1) : 0;
        const otherPercent = totalCells > 0 ? ((otherCount / totalCells) * 100).toFixed(1) : 0;
        
        statsItems[3].querySelector('.stat-value').textContent = `${normalCount} (${normalPercent}%)`;
        statsItems[4].querySelector('.stat-value').textContent = `${abnormalCount} (${abnormalPercent}%)`;
        statsItems[5].querySelector('.stat-value').textContent = `${otherCount} (${otherPercent}%)`;

        // Progress bar yangilash
        document.querySelector('.progress-fill').style.width = `${normalPercent}%`;
        
        // Umumiy hujayra soni - ID bilan aniq topamiz
        const totalCellsElement = document.getElementById('total-cells-count');
        if (totalCellsElement) {
            totalCellsElement.textContent = `${totalCells} hujayra`;
        } else {
            // Fallback: eski usul
            const fallbackElement = document.querySelector('.stats-panel div:last-child div:last-child');
            if (fallbackElement) {
                fallbackElement.textContent = `${totalCells} hujayra`;
            }
        }
        console.log('Total cells updated to:', totalCells);
        console.log('Stats panel updated');

        // Update crop results
        const cropGrid = document.querySelector('.crop-grid');
        cropGrid.innerHTML = '';
        ['Normal', 'Abnormal', 'Other'].forEach(cls => {
            const items = data.cropped_images.filter(img => img.class_name === cls);
            if (items.length === 0) return;

            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'crop-category';
            categoryDiv.innerHTML = `
                <h4 class="crop-title">${cls} Spermalar (${items.length} ta)</h4>
                <div class="crop-images">
                    ${items.slice(0, 3).map(item => `
                        <div class="crop-item">
                            <div class="crop-image"><img src="${item.image}" style="width: 100%; height: 100%; object-fit: cover;"></div>
                            <div class="crop-label">${item.label}</div>
                        </div>
                    `).join('')}
                    ${items.length > 3 ? `<div class="crop-more">+${items.length - 3} ta</div>` : ''}
                </div>
            `;
            cropGrid.appendChild(categoryDiv);
        });
        console.log('Crop grid updated with', data.cropped_images.length, 'images');

        analyzeBtn.innerHTML = '✅ Tahlil tugallandi';
        setTimeout(() => {
            analyzeBtn.innerHTML = '🔍 Tahlil Boshlash';
            analyzeBtn.disabled = false;
        }, 2000);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Xato yuz berdi: ' + error.message);
        analyzeBtn.innerHTML = '❌ Xato yuz berdi';
        setTimeout(() => {
            analyzeBtn.innerHTML = '🔍 Tahlil Boshlash';
            analyzeBtn.disabled = false;
        }, 2000);
    });
});

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        if (this.href.includes('/report')) {
            window.location.href = '/report';
        }
    });
});

function changeLanguage(lang) {
    console.log('Language changed to:', lang);
}