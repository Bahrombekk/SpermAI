document.getElementById('fileInput').addEventListener('change', function(e) {
    if (e.target.files[0]) {
        const file = e.target.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            document.querySelector('.image-placeholder').innerHTML = 
                `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 10px;">`;
        };
        reader.readAsDataURL(file);
        
        // Send image to backend
        const formData = new FormData();
        formData.append('file', file);
        const analyzeBtn = document.querySelector('.btn-primary');
        
        analyzeBtn.innerHTML = '⏳ Tahlil qilinmoqda...';
        analyzeBtn.disabled = true;
        
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.message);
            }
            
            // Update stats panel
            document.querySelector('.stat-item:nth-child(1) .stat-value').textContent = `${data.stats.Live} ta`;
            document.querySelector('.stat-item:nth-child(2) .stat-value').textContent = `${data.stats.Dead} ta`;
            document.querySelector('.stat-item:nth-child(3) .stat-value').textContent = `${data.stats.Immature} ta`;
            
            document.querySelector('.stat-item:nth-child(5) .stat-value').textContent = `${data.classification.Normal} (${(data.classification.Normal/data.total_cells*100).toFixed(1)}%)`;
            document.querySelector('.stat-item:nth-child(6) .stat-value').textContent = `${data.classification.Abnormal} (${(data.classification.Abnormal/data.total_cells*100).toFixed(1)}%)`;
            document.querySelector('.stat-item:nth-child(7) .stat-value').textContent = `${data.classification.Other} (${(data.classification.Other/data.total_cells*100).toFixed(1)}%)`;
            
            document.querySelector('.progress-fill').style.width = `${(data.classification.Normal/data.total_cells*100)}%`;
            document.querySelector('.stats-panel div:last-child div:last-child').textContent = `${data.total_cells} hujayra`;
            
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
            
            analyzeBtn.innerHTML = '✅ Tahlil tugallandi';
            setTimeout(() => {
                analyzeBtn.innerHTML = '🔍 Tahlil Boshlash';
                analyzeBtn.disabled = false;
            }, 2000);
        })
        .catch(error => {
            console.error('Error:', error);
            analyzeBtn.innerHTML = '❌ Xato yuz berdi';
            setTimeout(() => {
                analyzeBtn.innerHTML = '🔍 Tahlil Boshlash';
                analyzeBtn.disabled = false;
            }, 2000);
        });
    }
});

// Navigation active state
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});