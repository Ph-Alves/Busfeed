/**
 * BusFeed - Sistema de transporte público inteligente para Brasília
 * JavaScript principal com foco em acessibilidade e experiência do usuário
 */

(function() {
    'use strict';

    // Configuração global do BusFeed
    window.BusFeed = {
        version: '1.0.0',
        initialized: false,
        settings: {
            apiUrl: '/api/v1/',
            mapCenter: [-15.7801, -47.9292], // Brasília
            mapZoom: 11,
            refreshInterval: 30000, // 30 segundos
            searchDelay: 300 // 300ms
        }
    };

    /**
     * Inicialização principal do sistema
     */
    function init() {
        if (BusFeed.initialized) return;
        
        console.log('Inicializando BusFeed v' + BusFeed.version);
        
        // Configurar acessibilidade
        setupAccessibility();
        
        // Configurar atalhos de teclado
        setupKeyboardShortcuts();
        
        // Configurar formulários
        setupForms();
        
        // Configurar notificações
        setupNotifications();
        
        // Configurar Service Worker para PWA
        setupServiceWorker();
        
        BusFeed.initialized = true;
        console.log('BusFeed inicializado com sucesso');
    }

    /**
     * Configurações de acessibilidade
     */
    function setupAccessibility() {
        // Melhorar navegação por teclado
        document.addEventListener('keydown', function(e) {
            // Escape para fechar modais e menus
            if (e.key === 'Escape') {
                closeModalsAndMenus();
            }
        });

        // Adicionar indicadores visuais para elementos focados
        document.addEventListener('focusin', function(e) {
            e.target.classList.add('focused');
        });

        document.addEventListener('focusout', function(e) {
            e.target.classList.remove('focused');
        });

        // Anunciar mudanças dinâmicas para leitores de tela
        window.announceToScreenReader = function(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            
            document.body.appendChild(announcement);
            
            setTimeout(function() {
                document.body.removeChild(announcement);
            }, 1000);
        };
    }

    /**
     * Configurar atalhos de teclado
     */
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Verificar se Alt está pressionado
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
                case 'm':
                case 'M':
                    e.preventDefault();
                    focusMainMenu();
                    break;
            }
        });
    }

    /**
     * Configurar formulários com validação e feedback
     */
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

        // Validação de formulários em tempo real
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(setupFormValidation);

        // Botão de trocar origem/destino
        const swapButton = document.querySelector('button[aria-label*="Trocar"]');
        if (swapButton) {
            swapButton.addEventListener('click', handleSwapOriginDestination);
        }
    }

    /**
     * Configurar sistema de notificações
     */
    function setupNotifications() {
        // Verificar suporte a notificações
        if ('Notification' in window) {
            // Solicitar permissão se ainda não foi concedida
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }

        // Configurar notificações do sistema
        window.showNotification = function(title, options) {
            options = options || {};
            
            if (Notification.permission === 'granted') {
                const notification = new Notification(title, {
                    icon: '/static/images/icon-192x192.png',
                    badge: '/static/images/badge-72x72.png',
                    ...options
                });
                
                notification.onclick = function() {
                    window.focus();
                    notification.close();
                };
                
                // Auto-close após 5 segundos
                setTimeout(function() {
                    notification.close();
                }, 5000);
            }
        };
    }

    /**
     * Configurar Service Worker para PWA
     */
    function setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('Service Worker registrado:', registration);
                })
                .catch(function(error) {
                    console.log('Erro ao registrar Service Worker:', error);
                });
        }
    }

    /**
     * Utilitários
     */
    function closeModalsAndMenus() {
        // Fechar modais do Bootstrap
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(function(modal) {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });

        // Fechar dropdowns
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(function(dropdown) {
            const toggle = dropdown.previousElementSibling;
            if (toggle) {
                bootstrap.Dropdown.getInstance(toggle)?.hide();
            }
        });
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
            // Implementar busca/autocomplete aqui
            console.log('Buscando por:', value);
        }
    }

    function setupFormValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(input);
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
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';

        // Validações específicas
        if (field.required && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        } else if (field.type === 'email' && value && !isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Digite um email válido';
        } else if (fieldName === 'mensagem' && value.length < 10) {
            isValid = false;
            errorMessage = 'A mensagem deve ter pelo menos 10 caracteres';
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
        let isFormValid = true;

        fields.forEach(function(field) {
            if (!validateField(field)) {
                isFormValid = false;
            }
        });

        return isFormValid;
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

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        removeFieldError(field);
    }

    function showFieldError(field, message) {
        removeFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        errorDiv.setAttribute('aria-live', 'polite');
        
        field.parentNode.appendChild(errorDiv);
    }

    function removeFieldError(field) {
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    function focusFirstError(form) {
        const firstInvalidField = form.querySelector('.is-invalid');
        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function handleSwapOriginDestination() {
        const origemInput = document.getElementById('origem');
        const destinoInput = document.getElementById('destino');
        
        if (origemInput && destinoInput) {
            const temp = origemInput.value;
            origemInput.value = destinoInput.value;
            destinoInput.value = temp;
            
            origemInput.focus();
            announceToScreenReader('Origem e destino foram trocados');
        }
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Utilitários para APIs
     */
    window.BusFeed.api = {
        get: function(endpoint, callback) {
            fetch(BusFeed.settings.apiUrl + endpoint)
                .then(response => response.json())
                .then(callback)
                .catch(error => console.error('Erro na API:', error));
        },
        
        post: function(endpoint, data, callback) {
            fetch(BusFeed.settings.apiUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(callback)
            .catch(error => console.error('Erro na API:', error));
        }
    };

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expor algumas funções globalmente para uso em templates
    window.announceToScreenReader = window.announceToScreenReader;
    window.showNotification = window.showNotification;

})(); 