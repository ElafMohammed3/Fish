document.addEventListener('DOMContentLoaded', function() {
    var closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var msg = this.parentElement;
            msg.style.display = 'none';
        });
    });

    var messages = document.querySelectorAll('.msg');
    messages.forEach(function(msg) {
        setTimeout(function() {
            if (msg.parentNode) {
                msg.style.display = 'none';
            }
        }, 5000);
    });

    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var required = this.querySelectorAll('[required]');
            var valid = true;

            required.forEach(function(field) {
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
});