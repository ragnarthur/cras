// Validação de formulários com Bootstrap
(function () {
    'use strict'

    // Busca todos os formulários que precisam de validação
    var forms = document.querySelectorAll('.needs-validation')

    // Valida cada formulário
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }

            form.classList.add('was-validated')
        }, false)
    })
})()
