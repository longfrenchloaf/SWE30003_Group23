// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('animatedSidebar');
    const mainContent = document.getElementById('mainContent');
    const headerSidebarToggle = document.getElementById('headerSidebarToggle');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (mainContent) mainContent.classList.add('sidebar-active');
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (mainContent) mainContent.classList.remove('sidebar-active');
    }

    if (headerSidebarToggle) {
        headerSidebarToggle.addEventListener('click', function(event) {
            event.stopPropagation();
            if (sidebar && sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', closeSidebar);
    }

    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links .nav-item');
    const sidebarLinks = document.querySelectorAll('.sidebar-links a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    const inputs = document.querySelectorAll('input[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.classList.add('input-error'); 
            } else {
                this.classList.remove('input-error');
            }
        });
        input.addEventListener('focus', function() {
            this.classList.remove('input-error');
        });
    });

    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        if (button.type === 'submit' && button.form) {
            button.form.addEventListener('submit', function(event) {
                const message = button.getAttribute('data-confirm') || 'Are you sure?';
                if (!confirm(message)) {
                    event.preventDefault();
                }
            });
        } else {
            button.addEventListener('click', function(event) {
                const message = this.getAttribute('data-confirm') || 'Are you sure?';
                if (!confirm(message)) {
                    event.preventDefault();
                }
            });
        }
    });

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const sunIcon = themeToggle.querySelector('.fa-sun');
        const moonIcon = themeToggle.querySelector('.fa-moon');

        function setTheme(theme) {
            document.body.classList.remove('light-theme', 'dark-theme');
            document.body.classList.add(theme + '-theme');
            localStorage.setItem('theme', theme);
            if (sunIcon && moonIcon) {
                if (theme === 'dark') {
                    sunIcon.style.display = 'none';
                    moonIcon.style.display = 'inline-block';
                } else {
                    sunIcon.style.display = 'inline-block';
                    moonIcon.style.display = 'none';
                }
            }
        }

        themeToggle.addEventListener('click', () => {
            let currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
            let newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });

        const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        setTheme(savedTheme);
    }

    const animatedItems = document.querySelectorAll('.fade-in-item, .list-group-item');
    animatedItems.forEach((item, index) => {
        if (!item.classList.contains('trip-option')) {
            item.style.animationDelay = `${index * 0.07}s`;
        }
    });

    const createOrderForm = document.getElementById('createOrderForm');
    if (createOrderForm) {
        const paymentTypeRadios = createOrderForm.querySelectorAll('input[name="payment_type"]');
        const cardDetailsDiv = createOrderForm.querySelector('#card-payment-details');
        const ewalletDetailsDiv = createOrderForm.querySelector('#ewallet-payment-details');

        function togglePaymentDetailsVisibility() {
            const selectedPaymentTypeRadio = createOrderForm.querySelector('input[name="payment_type"]:checked');
            if (!selectedPaymentTypeRadio) {
                 if(cardDetailsDiv) cardDetailsDiv.classList.add('hidden');
                 if(ewalletDetailsDiv) ewalletDetailsDiv.classList.add('hidden');
                return;
            }
            const selectedPaymentType = selectedPaymentTypeRadio.value;

            if (cardDetailsDiv && ewalletDetailsDiv) {
                if (selectedPaymentType === 'card') {
                    cardDetailsDiv.classList.remove('hidden');
                    ewalletDetailsDiv.classList.add('hidden');
                } else if (selectedPaymentType === 'ewallet') {
                    cardDetailsDiv.classList.add('hidden');
                    ewalletDetailsDiv.classList.remove('hidden');
                } else {
                    cardDetailsDiv.classList.add('hidden');
                    ewalletDetailsDiv.classList.add('hidden');
                }
            }
        }

        if (paymentTypeRadios.length > 0 && cardDetailsDiv && ewalletDetailsDiv) {
            paymentTypeRadios.forEach(radio => {
                radio.addEventListener('change', togglePaymentDetailsVisibility);
            });
            togglePaymentDetailsVisibility();
        }
    }
// --- Confirmation Dialog for Buy Ticket/Merchandise Forms ---
    const buyTicketForm = document.getElementById('buyTicketForm');
    if (buyTicketForm) {
        let hiddenProceedInputTicket = buyTicketForm.querySelector('input[name="proceed_with_payment_ticket"]');
        if (!hiddenProceedInputTicket) {
            hiddenProceedInputTicket = document.createElement('input');
            hiddenProceedInputTicket.type = 'hidden';
            hiddenProceedInputTicket.name = 'proceed_with_payment_ticket';
            buyTicketForm.appendChild(hiddenProceedInputTicket);
            console.log("JS: Created hidden input 'proceed_with_payment_ticket'");
        } else {
            console.log("JS: Found existing hidden input 'proceed_with_payment_ticket'");
        }
        
        let isProgrammaticSubmitTicket = false; // Flag specific to ticket form

        buyTicketForm.addEventListener('submit', function(event) {
            if (isProgrammaticSubmitTicket) {
                console.log("JS (Ticket): Programmatic submit detected. Allowing form submission.");
                isProgrammaticSubmitTicket = false; 
                return; 
            }
            
            event.preventDefault(); 
            console.log("JS (Ticket): Manual submit detected. Preventing default for confirmation.");

            // Re-ensure hidden input reference is valid (very defensive)
            if (!hiddenProceedInputTicket || !buyTicketForm.contains(hiddenProceedInputTicket)) {
                console.warn("JS (Ticket): hiddenProceedInputTicket reference lost/removed. Re-fetching/re-creating.");
                hiddenProceedInputTicket = buyTicketForm.querySelector('input[name="proceed_with_payment_ticket"]');
                 if (!hiddenProceedInputTicket) { // If still not found after re-querying
                    hiddenProceedInputTicket = document.createElement('input');
                    hiddenProceedInputTicket.type = 'hidden';
                    hiddenProceedInputTicket.name = 'proceed_with_payment_ticket';
                    buyTicketForm.appendChild(hiddenProceedInputTicket);
                    console.log("JS (Ticket): Re-created hidden input 'proceed_with_payment_ticket' during event.");
                }
            }

            if (confirm("Are you sure you want to proceed with the payment now?")) {
                hiddenProceedInputTicket.value = 'yes';
                console.log("JS (Ticket): User chose YES. Hidden input 'proceed_with_payment_ticket' value set to:", hiddenProceedInputTicket.value);
            } else {
                hiddenProceedInputTicket.value = 'no';
                console.log("JS (Ticket): User chose NO. Hidden input 'proceed_with_payment_ticket' value set to:", hiddenProceedInputTicket.value);
                alert("Your order will be created with payment pending. You can pay later from your order details.");
            }
            
            console.log(`JS (Ticket): Final value of hiddenProceedInputTicket before programmatic submit: '${hiddenProceedInputTicket.value}'`);
            
            isProgrammaticSubmitTicket = true; 
            buyTicketForm.submit(); 
        });
    }

    // Similar logic for buyMerchandiseForm (ensure variable names are distinct if co-existing)
    const buyMerchandiseForm = document.querySelector('form[action*="/buy-merchandise"]');
    // Ensure it's not the same as buyTicketForm if using querySelector and IDs might overlap
    if (buyMerchandiseForm && (!document.getElementById('buyTicketForm') || buyMerchandiseForm !== document.getElementById('buyTicketForm'))) {
        console.log("JS (Merch): Attaching listener to merchandise form:", buyMerchandiseForm);

        let hiddenProceedInputMerch = buyMerchandiseForm.querySelector('input[name="proceed_with_payment_merch"]');
        if (!hiddenProceedInputMerch) {
            hiddenProceedInputMerch = document.createElement('input');
            hiddenProceedInputMerch.type = 'hidden';
            hiddenProceedInputMerch.name = 'proceed_with_payment_merch';
            // IMPORTANT: Set an initial default value. The server-side default is 'no',
            // but this helps if JS runs and something goes wrong before confirm.
            hiddenProceedInputMerch.value = 'no'; // Initial JS default
            buyMerchandiseForm.appendChild(hiddenProceedInputMerch);
            console.log("JS (Merch): Created hidden input 'proceed_with_payment_merch' and set initial value to 'no'");
        } else {
            // If it exists, ensure its default value is 'no' before any user interaction
            // This can help if the page reloads with old form state preserved by the browser.
            hiddenProceedInputMerch.value = 'no';
            console.log("JS (Merch): Found existing hidden input 'proceed_with_payment_merch'. Ensured its value is 'no'.");
        }

        let isProgrammaticSubmitMerch = false;

        buyMerchandiseForm.addEventListener('submit', function(event) {
            console.log("JS (Merch): Submit event triggered for merchandise form.");
            if (isProgrammaticSubmitMerch) {
                console.log("JS (Merch): Programmatic submit detected. Allowing form submission.");
                // Value of hiddenProceedInputMerch should already be set from the confirm dialog
                console.log("JS (Merch): Value of 'proceed_with_payment_merch' on programmatic submit: " + hiddenProceedInputMerch.value);
                isProgrammaticSubmitMerch = false;
                return;
            }

            event.preventDefault();
            console.log("JS (Merch): Manual submit detected. Preventing default for confirmation.");

            // Explicitly set to 'no' before confirm, then change if user says 'yes'
            hiddenProceedInputMerch.value = 'no';
            console.log("JS (Merch): Set 'proceed_with_payment_merch' to 'no' before confirm dialog.");


            if (confirm("MERCHANDISE: Are you sure you want to proceed with the payment now for this merchandise?")) {
                hiddenProceedInputMerch.value = 'yes';
                console.log("JS (Merch): User chose YES. Hidden input 'proceed_with_payment_merch' value set to:", hiddenProceedInputMerch.value);
            } else {
                // Value is already 'no'
                console.log("JS (Merch): User chose NO. Hidden input 'proceed_with_payment_merch' value remains:", hiddenProceedInputMerch.value);
                alert("Your order for merchandise will be created with payment pending.");
            }
            
            console.log(`JS (Merch): Final value of hiddenProceedInputMerch before programmatic submit: '${hiddenProceedInputMerch.value}'`);
            
            isProgrammaticSubmitMerch = true;
            buyMerchandiseForm.submit();
        });
    } else if (buyMerchandiseForm) {
        // This case means querySelector found it, but it might be the ticket form.
        console.log("JS (Merch): Merchandise form selector found a form, but it might be the ticket form. Skipping merchandise-specific listener.");
    } else {
        console.log("JS (Merch): Merchandise form not found on this page.");
    }

    const tripOptions = document.querySelectorAll('.trip-selection-list .trip-option');
    if (tripOptions.length > 0) { // Check if these elements exist on the current page
        tripOptions.forEach(option => {
            const radio = option.querySelector('.form-check-input');
            if (radio) { // Ensure radio button exists
                option.addEventListener('click', function () {
                    tripOptions.forEach(opt => {
                        opt.classList.remove('selected');
                        const r = opt.querySelector('.form-check-input');
                        if (r) r.checked = false;
                    });
                    radio.checked = true;
                    option.classList.add('selected');
                });

                if (radio.checked) {
                    option.classList.add('selected');
                }
            }
        });
    }

    console.log("Main.js loaded and initialized.");
});