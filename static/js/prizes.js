// Prize Management JavaScript

// Wait for DOM and Bootstrap to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for Bootstrap to be available
    if (typeof bootstrap === 'undefined') {
        setTimeout(function() {
            initializePrizeChart();
            initializeFileUpload();
        }, 100);
    } else {
        initializePrizeChart();
        initializeFileUpload();
    }
});

// Helper function to safely get modal
function safeGetModal(modalId) {
    console.log('Поиск модального окна:', modalId);
    
    // Wait a bit for DOM to be fully ready
    let attempts = 0;
    const maxAttempts = 10;
    
    function findModal() {
        attempts++;
        const modalElement = document.getElementById(modalId);
        
        if (!modalElement) {
            if (attempts < maxAttempts) {
                console.log(`Попытка ${attempts}: элемент ${modalId} не найден, повтор через 100мс`);
                setTimeout(findModal, 100);
                return;
            }
            console.error(`Модальное окно с ID "${modalId}" не найдено после ${maxAttempts} попыток`);
            console.log('Доступные элементы с ID modal:', document.querySelectorAll('[id*="modal"]'));
            return null;
        }
        
        if (typeof bootstrap === 'undefined') {
            console.error('Bootstrap не загружен');
            return null;
        }
        
        try {
            console.log('Создание модального окна для:', modalId);
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            return modal;
        } catch (error) {
            console.error('Ошибка создания модального окна:', error);
            return null;
        }
    }
    
    findModal();
    return null; // Возвращаем null, так как это асинхронная операция
}

// Toggle between table and card view
function toggleView() {
    const tableView = document.getElementById('tableView');
    const cardView = document.getElementById('cardView');
    const viewIcon = document.getElementById('viewIcon');
    const viewText = document.getElementById('viewText');
    
    if (tableView && cardView && viewIcon && viewText) {
        if (tableView.style.display === 'none') {
            tableView.style.display = 'block';
            cardView.style.display = 'none';
            viewIcon.className = 'fas fa-th';
            viewText.textContent = 'Карточки';
        } else {
            tableView.style.display = 'none';
            cardView.style.display = 'block';
            viewIcon.className = 'fas fa-table';
            viewText.textContent = 'Таблица';
        }
    }
}

// Initialize prize chart
function initializePrizeChart() {
    const prizeChartElement = document.getElementById('prizeChart');
    if (prizeChartElement && typeof Chart !== 'undefined') {
        // Get data from data attributes or calculate from visible elements
        const usedPrizes = parseInt(prizeChartElement.dataset.used || '0');
        const totalPrizes = parseInt(prizeChartElement.dataset.total || '0');
        const availablePrizes = totalPrizes - usedPrizes;

        const prizeCtx = prizeChartElement.getContext('2d');
        new Chart(prizeCtx, {
            type: 'doughnut',
            data: {
                labels: ['Доступные', 'Использованные'],
                datasets: [{
                    data: [availablePrizes, usedPrizes],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                }
            }
        });
    }
}

// Prize Management Functions
function showAddPrizeModal() {
    safeGetModal('addPrizeModal');
}

function addPrize() {
    const prizeId = document.getElementById('prizeId').value.trim();
    const prizeName = document.getElementById('prizeName').value.trim();
    const prizeDescription = document.getElementById('prizeDescription').value.trim();
    
    if (!prizeId || !prizeName) {
        alert('ID приза и название обязательны');
        return;
    }
    
    fetch('/api/prizes/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prize_id: prizeId,
            prize_name: prizeName,
            prize_description: prizeDescription
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при добавлении приза: ' + error);
    });
}

function removePrize(prizeId) {
    if (!confirm('Вы уверены, что хотите удалить этот приз?')) {
        return;
    }
    
    fetch('/api/prizes/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prize_id: prizeId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при удалении приза: ' + error);
    });
}

// Prize List Management Functions
function showCreatePrizeListModal() {
    safeGetModal('createPrizeListModal');
}

function createPrizeList() {
    const listId = document.getElementById('listId').value.trim();
    const listName = document.getElementById('listName').value.trim();
    const prizeContent = document.getElementById('prizeContent').value.trim();
    
    if (!listId || !listName) {
        alert('ID списка и название обязательны');
        return;
    }
    
    fetch('/api/prize-lists/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            list_id: listId,
            list_name: listName,
            prize_content: prizeContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при создании списка призов: ' + error);
    });
}

function viewPrizeList(listId) {
    fetch(`/api/prize-lists/${listId}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Ошибка: ' + data.error);
            return;
        }
        
        const content = document.getElementById('prizeListContent');
        if (content) {
            content.innerHTML = `
                <div class="mb-3">
                    <h6>Название: <strong>${data.metadata.name || 'Без названия'}</strong></h6>
                    <p class="text-muted">Количество призов: ${data.metadata.prize_count || 0}</p>
                </div>
                <div class="border rounded p-3" style="background: #2d3748; max-height: 400px; overflow-y: auto;">
                    <pre class="mb-0" style="color: #e2e8f0;">${data.content || 'Список пуст'}</pre>
                </div>
            `;
        }
        
        safeGetModal('viewPrizeListModal');
    })
    .catch(error => {
        console.error('Ошибка при загрузке списка призов:', error);
        alert('Ошибка при загрузке списка призов: ' + error.message);
    });
}

function editPrizeList(listId) {
    fetch(`/api/prize-lists/${listId}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Ошибка: ' + data.error);
            return;
        }
        
        const editListId = document.getElementById('editListId');
        const editListName = document.getElementById('editListName');
        const editPrizeContent = document.getElementById('editPrizeContent');
        
        if (editListId && editListName && editPrizeContent) {
            editListId.value = listId;
            editListName.value = data.metadata.name || '';
            editPrizeContent.value = data.content || '';
        } else {
            console.error('Не найдены элементы формы редактирования');
            alert('Ошибка: элементы формы не найдены');
            return;
        }
        
        safeGetModal('editPrizeListModal');
    })
    .catch(error => {
        console.error('Ошибка при загрузке списка призов:', error);
        alert('Ошибка при загрузке списка призов: ' + error.message);
    });
}

function updatePrizeList() {
    const listId = document.getElementById('editListId').value;
    const listName = document.getElementById('editListName').value.trim();
    const prizeContent = document.getElementById('editPrizeContent').value.trim();
    
    if (!listName) {
        alert('Название списка обязательно');
        return;
    }
    
    fetch(`/api/prize-lists/${listId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            list_name: listName,
            prize_content: prizeContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при обновлении списка призов: ' + error);
    });
}

function removePrizeList(listId) {
    if (!confirm('Вы уверены, что хотите удалить этот список призов?')) {
        return;
    }
    
    fetch(`/api/prize-lists/${listId}/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при удалении списка призов: ' + error);
    });
}

// File Upload Functions
function initializeFileUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (dropZone && fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);
        
        // Handle file input change
        fileInput.addEventListener('change', function(e) {
            handleFiles(e.target.files);
        });
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        dropZone.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
    }
}

function unhighlight(e) {
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        dropZone.style.backgroundColor = '';
    }
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    if (!file.name.endsWith('.txt')) {
        alert('Пожалуйста, выберите текстовый файл (.txt)');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        const listId = 'list_' + Date.now();
        const listName = file.name.replace('.txt', '');
        
        if (confirm(`Создать новый список призов "${listName}" с ${content.split('\n').filter(line => line.trim()).length} призами?`)) {
            uploadPrizeList(listId, listName, content);
        }
    };
    reader.readAsText(file);
}

function uploadPrizeList(listId, listName, content) {
    fetch('/api/prize-lists/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            list_id: listId,
            list_name: listName,
            prize_content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при создании списка призов: ' + error);
    });
}