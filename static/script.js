document.addEventListener('DOMContentLoaded', function() {
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const msg = this.parentElement;
            msg.style.display = 'none';
        });
    });

    const messages = document.querySelectorAll('.msg');
    messages.forEach(msg => {
        setTimeout(() => {
            if (msg.parentNode) {
                msg.style.display = 'none';
            }
        }, 5000);
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const required = this.querySelectorAll('[required]');
            let valid = true;

            required.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = 'red';
                    
                    field.addEventListener('input', function() {
                        this.style.borderColor = '#ddd';
                    });
                }
            });

            if (!valid) {
                e.preventDefault();
                alert('املأ الحقول المطلوبة');
            }
        });
    });

    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const preview = this.closest('.field').querySelector('.image-preview');
            
            const fileCardText = this.closest('.file-card')?.querySelector('.file-text');
            if (fileCardText && file) {
                fileCardText.textContent = file.name;
            }
            
            if (file && preview) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else if (preview) {
                preview.style.display = 'none';
            }
        });
    });
});