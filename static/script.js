// Client-side script for enhanced UX

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('routine-form');
    const statusDiv = document.getElementById('status');
    const dateDisplay = document.getElementById('date-display');
    
    // Update date display
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    dateDisplay.textContent = now.toLocaleDateString('en-US', options);
    
    // Form submission handler
    form.addEventListener('submit', function(e) {
        statusDiv.textContent = 'Updating progress...';
        statusDiv.className = '';
    });
    
    // Real-time checkbox feedback
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const li = this.closest('li');
            if (this.checked) {
                li.style.background = 'rgba(0, 255, 127, 0.2)';
                li.style.borderLeftColor = '#00ff7f';
            } else {
                li.style.background = 'rgba(255, 100, 100, 0.15)';
                li.style.borderLeftColor = '#ff6464';
            }
        });
    });
    
    // Auto-detect special tasks (Curd Rice)
    const taskLabels = document.querySelectorAll('.task-list label');
    taskLabels.forEach(label => {
        if (label.textContent.includes('Curd Rice')) {
            label.closest('li').classList.add('special-task');
        }
    });
});

