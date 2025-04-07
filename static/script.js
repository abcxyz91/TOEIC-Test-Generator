document.addEventListener('DOMContentLoaded', function() {

    // --- Reusable Function for Button Loading State ---
    function setupButtonLoading(formId, buttonId, options = {}) {
        const form = document.getElementById(formId);
        if (!form) return; // Exit if form not found

        form.addEventListener('submit', function(event) {
            const button = document.getElementById(buttonId);
            if (!button) return; // Exit if button not found

            const defaults = {
                buttonTextSelector: '.button-text', // Default selector for text span
                loaderSelector: '.loader',         // Default selector for loader span
                iconSelector: null,                // Default selector for icon span (optional)
                loadingText: 'Processing...',      // Default loading text
                hideIconOnLoad: true               // Default behavior for icon
            };
            const config = { ...defaults, ...options }; // Merge user options with defaults

            const buttonTextEl = button.querySelector(config.buttonTextSelector);
            const loaderEl = button.querySelector(config.loaderSelector);
            const iconEl = config.iconSelector ? button.querySelector(config.iconSelector) : null;

            // Disable button
            button.disabled = true;

            // Update appearance
            if (buttonTextEl) buttonTextEl.textContent = config.loadingText;
            if (loaderEl) loaderEl.classList.remove('hidden');
            if (iconEl && config.hideIconOnLoad) iconEl.classList.add('hidden');
        });
    }

    // --- Setup Loading States for Specific Buttons ---
    setupButtonLoading('grammar-test-form', 'grammar-test-button', {
        iconSelector: '[aria-label="pencil"]',
        loadingText: 'Generating...'
    });

    setupButtonLoading('reading-test-form', 'reading-test-button', {
        iconSelector: '[aria-label="glasses"]',
        loadingText: 'Generating...'
    });

    setupButtonLoading('retake-test-form', 'retake-button', {
         iconSelector: '[aria-label="refresh"]',
         loadingText: 'Generating...'
    });


    // --- Subtle animation for flash messages ---
    const flashMessages = document.querySelectorAll('[role="alert"].animate-fade-in'); // Target only alerts meant to fade in
    flashMessages.forEach((msg, index) => {
        msg.style.opacity = '0';
        msg.style.animationDelay = `${index * 0.1}s`;
        void msg.offsetWidth;
        msg.style.opacity = '1'; 

        // Add fade-out animation for success messages after 3 seconds
        if (msg.classList.contains('bg-green-100')) {
            setTimeout(() => {
                msg.classList.remove('animate-fade-in');
                msg.classList.add('animate-fade-out');
                // Remove the element after animation completes
                setTimeout(() => {
                    msg.remove();
                }, 600); // Duration of fade-out animation
            }, 3000); // 3 seconds delay before fade-out starts
        }
    });

    // --- Form validation for test submission ---
    const testForm = document.querySelector('form[action="/test"]');
    if (testForm) {
        testForm.addEventListener('submit', function(event) {
            // Get all radio button groups
            const questionCount = document.querySelectorAll('h3[class*="text-xl"]').length;
            const answers = new Array(questionCount).fill(false);

            // Check each question's answer
            for (let i = 0; i < questionCount; i++) {
                const radioButtons = document.querySelectorAll(`input[name="answers[${i}]"]`);
                answers[i] = Array.from(radioButtons).some(radio => radio.checked);
            }

            // If any question is unanswered
            if (answers.includes(false)) {
                event.preventDefault(); // Prevent form submission
                
                // Create and show flash message
                const flashContainer = document.querySelector('.w-full.max-w-4xl');
                const flashMessage = document.createElement('div');
                flashMessage.className = 'animate-fade-in transition-all duration-600 bg-red-100 border-red-500 text-red-700 border-l-4 p-4 mb-4 rounded-lg shadow-md';
                flashMessage.setAttribute('role', 'alert');
                flashMessage.innerHTML = '<p class="font-medium">Please answer all questions before submitting!</p>';
                
                // Insert flash message at the top of the container
                flashContainer.insertBefore(flashMessage, flashContainer.firstChild);

                // Scroll to first unanswered question
                const firstUnanswered = answers.findIndex(answered => !answered);
                const firstUnansweredQuestion = document.querySelector(`h3[class*="text-xl"]:nth-of-type(${firstUnanswered + 1})`);
                firstUnansweredQuestion.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Remove flash message after 3 seconds
                setTimeout(() => {
                    flashMessage.classList.remove('animate-fade-in');
                    flashMessage.classList.add('animate-fade-out');
                    setTimeout(() => flashMessage.remove(), 600);
                }, 3000);
            }
        });
    }
});