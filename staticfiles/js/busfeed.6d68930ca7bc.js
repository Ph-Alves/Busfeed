/**
 * BusFeed JavaScript - Sistema de transporte público inteligente
 * 
 * Funcionalidades principais:
 * - Acessibilidade e navegação por teclado
 * - Validação de formulários básica
 * - Interface responsiva
 * 
 * @author Equipe BusFeed
 * @version 1.0.0
 */

(function() {
    'use strict';

    // Namespace global do BusFeed
    window.BusFeed = {
        version: '1.0.0',
        settings: {
            searchDelay: 300,
            debug: false
        }
    };

    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        console.log('BusFeed v' + BusFeed.version + ' iniciado');
        setupAccessibility();
        setupKeyboardShortcuts();
        setupForms();
    }

    function setupAccessibility() {
        // Skip link para conteúdo principal
        const skipLink = document.querySelector('a[href="#main-content"]');
        if (skipLink) {
            skipLink.addEventListener('click', function(e) {
                e.preventDefault();
                const mainContent = document.querySelector('#main-content');
                if (mainContent) {
                    mainContent.focus();
                    announceToScreenReader('Navegou para o conteúdo principal');
                }
            });
        }

        // Melhorar acessibilidade de botões collapse
        const toggleButtons = document.querySelectorAll('[data-bs-toggle]');
        toggleButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                setTimeout(function() {
                    updateAriaExpanded(button);
                }, 100);
            });
        });
    }

    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            if (!e.altKey) return;
            
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    window.location.href = '/';
                    break;
                case '2':
                    e.preventDefault();
                    focusSearchForm();
                    break;
                case '3':
                    e.preventDefault();
                    window.location.href = '/paradas/';
                    break;
                case 'r':
                case 'R':
                    e.preventDefault();
                    window.location.href = '/rotas/';
                    break;
                case 'h':
                case 'H':
                    e.preventDefault();
                    window.location.href = '/horarios/';
                    break;
                case 'm':
                case 'M':
                    e.preventDefault();
                    focusMainMenu();
                    break;
            }
        });
    }

    function setupForms() {
        // Formulário de busca com debounce
        const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
        searchInputs.forEach(function(input) {
            let timeoutId;
            
            input.addEventListener('input', function() {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(function() {
                    handleSearchInput(input);
                }, BusFeed.settings.searchDelay);
            });
        });

        // Validação de formulários
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(setupFormValidation);
    }

    // Utilitários de acessibilidade
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'visually-hidden';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(function() {
            document.body.removeChild(announcement);
        }, 1000);
    }

    function updateAriaExpanded(button) {
        const target = document.querySelector(button.getAttribute('data-bs-target'));
        if (target) {
            const isExpanded = target.classList.contains('show');
            button.setAttribute('aria-expanded', isExpanded);
        }
    }

    function focusSearchForm() {
        const searchInput = document.querySelector('#origem, input[type="search"]');
        if (searchInput) {
            searchInput.focus();
            announceToScreenReader('Foco movido para o campo de busca');
        }
    }

    function focusMainMenu() {
        const mainNav = document.querySelector('.navbar-nav');
        if (mainNav) {
            const firstLink = mainNav.querySelector('a');
            if (firstLink) {
                firstLink.focus();
                announceToScreenReader('Foco movido para o menu principal');
            }
        }
    }

    function handleSearchInput(input) {
        const value = input.value.trim();
        if (value.length >= 3) {
            console.log('Buscando por:', value);
        }
    }

    function setupFormValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
        
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                focusFirstError(form);
            }
        });
    }

    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        if (field.required && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        } else if (field.type === 'email' && value && !isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Digite um email válido';
        }

        if (isValid) {
            markFieldAsValid(field);
        } else {
            markFieldAsInvalid(field, errorMessage);
        }

        return isValid;
    }

    function validateForm(form) {
        const fields = form.querySelectorAll('input, select, textarea');
        let isValid = true;
        
        fields.forEach(function(field) {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    function markFieldAsValid(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        removeFieldError(field);
    }

    function markFieldAsInvalid(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, message);
    }

    function showFieldError(field, message) {
        removeFieldError(field);
        
        const error = document.createElement('div');
        error.className = 'invalid-feedback';
        error.textContent = message;
        error.setAttribute('role', 'alert');
        
        field.parentNode.appendChild(error);
    }

    function removeFieldError(field) {
        const error = field.parentNode.querySelector('.invalid-feedback');
        if (error) {
            error.remove();
        }
    }

    function focusFirstError(form) {
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.focus();
        }
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

})(); 
})(); 