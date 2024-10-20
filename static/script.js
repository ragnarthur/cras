﻿// Validação de formulários com Bootstrap
(function () {
    'use strict';

    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
})();

// Função para formatar e limitar o campo de telefone a 11 dígitos numéricos
const telefoneInput = document.getElementById('telefone');
if (telefoneInput) {
    telefoneInput.addEventListener('input', function (e) {
        let telefone = e.target.value;
        
        // Remove tudo que não for número
        telefone = telefone.replace(/\D/g, '');
        
        // Limita o número de dígitos a 11
        if (telefone.length > 11) {
            telefone = telefone.substring(0, 11);
        }
        
        // Adiciona os parênteses ao DDD e o hífen no número
        telefone = telefone.replace(/^(\d{2})(\d)/g, '($1) $2');
        telefone = telefone.replace(/(\d)(\d{4})$/, '$1-$2');
        
        // Atualiza o valor do campo com a formatação
        e.target.value = telefone;
    });
}

// Função para customizar a saudação dependendo do horário
document.addEventListener('DOMContentLoaded', function () {
    const saudacaoElement = document.getElementById('saudacao');
    
    if (saudacaoElement) {
        const now = new Date();
        const hours = now.getHours();
        let saudacao = '';

        if (hours < 12) {
            saudacao = 'Bom dia';
        } else if (hours >= 12 && hours < 18) {
            saudacao = 'Boa tarde';
        } else {
            saudacao = 'Boa noite';
        }

        // Atualiza a saudação mantendo o nome
        saudacaoElement.textContent = saudacao + saudacaoElement.textContent.slice(saudacaoElement.textContent.indexOf(','));
    }
});
