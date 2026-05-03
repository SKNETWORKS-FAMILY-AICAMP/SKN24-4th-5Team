// Main application initialization
(function () {
    "use strict";

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (e) {
            const href = this.getAttribute("href");

            // Don't prevent default for navigation links
            if (this.hasAttribute("data-nav")) {
                return;
            }

            if (href === "#") {
                return;
            }

            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }
        });
    });

    // Add animation on scroll for feature cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, observerOptions);

    // Observe feature cards
    document.querySelectorAll(".feature-card").forEach((card) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        card.style.transition = "opacity 0.5s, transform 0.5s";
        observer.observe(card);
    });

    const modalOpenButtons = document.querySelectorAll("[data-modal-open]");
    let lastFocusedElement = null;

    function openModal(modal, trigger = null) {
        const parentModal = trigger ? trigger.closest(".custom-modal-backdrop.active") : null;
        const shouldStackModal = modal.hasAttribute("data-stacked-modal") || Boolean(parentModal);

        if (!document.activeElement.closest(".custom-modal-backdrop")) {
            lastFocusedElement = document.activeElement;
        }

        if (!shouldStackModal) {
            document.querySelectorAll(".custom-modal-backdrop.active").forEach((activeModal) => {
                if (activeModal !== modal) {
                    closeModal(activeModal, false);
                }
            });
        }

        modal.hidden = false;
        window.requestAnimationFrame(() => {
            modal.setAttribute("aria-hidden", "false");
            modal.classList.add("active");
        });
        document.body.classList.add("modal-open");

        const firstInput = modal.querySelector(
            ".login-modal__form input, .login-modal__form select, .login-modal__form textarea, .login-modal__form button, button, a",
        );
        if (firstInput) {
            firstInput.focus();
        }
    }

    function openModalById(modalId, trigger = null) {
        const modal = document.getElementById(modalId);

        if (modal) {
            openModal(modal, trigger);
        }
    }

    function closeModal(modal, restoreFocus = true) {
        modal.classList.remove("active");
        modal.setAttribute("aria-hidden", "true");
        modal.dispatchEvent(new CustomEvent("modal:close"));

        const hasAnotherActiveModal = Boolean(document.querySelector(".custom-modal-backdrop.active"));
        if (!hasAnotherActiveModal) {
            document.body.classList.remove("modal-open");
        }

        window.setTimeout(() => {
            if (!modal.classList.contains("active")) {
                modal.hidden = true;
            }
        }, 220);

        if (restoreFocus && lastFocusedElement) {
            lastFocusedElement.focus();
            lastFocusedElement = null;
        }
    }

    modalOpenButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            openModalById(button.getAttribute("data-modal-open"), button);
        });
    });

    document.querySelectorAll("[data-login-required]").forEach((link) => {
        link.addEventListener("click", (event) => {
            event.preventDefault();

            const loginModal = document.getElementById("loginModal");
            if (!loginModal) {
                return;
            }

            const nextInput = loginModal.querySelector('input[name="next"]');
            if (nextInput) {
                nextInput.value = link.getAttribute("href");
            }

            alert("로그인 후 이용 가능한 서비스입니다.");
            openModal(loginModal);
        });
    });

    document.querySelectorAll(".custom-modal-backdrop").forEach((modal) => {
        modal.setAttribute("aria-hidden", "true");

        modal.addEventListener("click", (event) => {
            const closeButton = event.target.closest("[data-modal-close]");

            if (closeButton) {
                event.preventDefault();
                event.stopPropagation();
                closeModal(closeButton.closest(".custom-modal-backdrop"));
                return;
            }

            if (event.target === modal) {
                event.stopPropagation();
                closeModal(modal);
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        const activeModals = document.querySelectorAll(".custom-modal-backdrop.active");
        const activeModal = activeModals[activeModals.length - 1];
        if (activeModal) {
            closeModal(activeModal);
        }
    });

    function setFeedback(element, message, type = "error") {
        if (!element) return;
        element.textContent = message;
        element.classList.remove("success", "error");
        if (message) element.classList.add(type);
    }

    function formatVerificationTime(totalSeconds) {
        const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
        const seconds = String(totalSeconds % 60).padStart(2, "0");

        return `${minutes}:${seconds}`;
    }

    function getCsrfToken() {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }

        const cookie = document.cookie.split("; ").find((row) => row.startsWith("csrftoken="));

        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    function createEmailVerificationController(options) {
        const sendButtons = options.sendButtons.filter(Boolean);
        let resendCooldownInterval = null;
        let verificationTimerInterval = null;
        let isVerificationSent = false;
        let isVerificationChecked = false;
        let verificationExpiresAt = 0;

        function startResendCooldown(button) {
            let remainingSeconds = 30;

            window.clearInterval(resendCooldownInterval);
            button.disabled = true;
            button.textContent = "재전송";

            resendCooldownInterval = window.setInterval(() => {
                remainingSeconds -= 1;

                if (remainingSeconds <= 0) {
                    window.clearInterval(resendCooldownInterval);
                    button.disabled = false;
                    button.textContent = "재전송";
                }
            }, 1000);
        }

        function expireVerification() {
            isVerificationChecked = false;
            verificationExpiresAt = 0;
        }

        function getDisplayedTimerExpiresAt() {
            const timerText = options.timer.textContent.trim();
            const match = timerText.match(/^(\d{1,2}):(\d{2})$/);

            if (!match || options.timer.classList.contains("is-expired")) {
                return 0;
            }

            const remainingSeconds = Number(match[1]) * 60 + Number(match[2]);
            return remainingSeconds > 0 ? Date.now() + remainingSeconds * 1000 : 0;
        }

        function getActiveExpiresAt() {
            if (verificationExpiresAt > Date.now()) {
                return verificationExpiresAt;
            }

            return getDisplayedTimerExpiresAt();
        }

        function startVerificationTimer() {
            let remainingSeconds = Math.max(0, Math.ceil((verificationExpiresAt - Date.now()) / 1000));

            if (remainingSeconds <= 0) {
                options.timer.textContent = "만료";
                options.timer.classList.add("is-expired");
                expireVerification();
                return;
            }

            window.clearInterval(verificationTimerInterval);
            options.timer.textContent = formatVerificationTime(remainingSeconds);
            options.timer.classList.remove("is-expired");

            verificationTimerInterval = window.setInterval(() => {
                remainingSeconds -= 1;

                if (remainingSeconds <= 0) {
                    window.clearInterval(verificationTimerInterval);
                    options.timer.textContent = "만료";
                    options.timer.classList.add("is-expired");
                    expireVerification();
                    return;
                }

                options.timer.textContent = formatVerificationTime(remainingSeconds);
            }, 1000);
        }

        async function send(button) {
            if (options.beforeSend) {
                const canSend = await options.beforeSend();
                if (!canSend) return;
            }

            const activeExpiresAtBeforeSend = getActiveExpiresAt();

            const formData = new FormData();
            formData.append("email", options.emailInput.value.trim());
            formData.append("purpose", options.purpose);

            try {
                button.disabled = true;
                const response = await fetch(options.sendUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: formData,
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    setFeedback(options.feedback, data.message || "인증메일 발송에 실패했습니다.");
                    button.disabled = false;
                    return;
                }

                const hasActiveVerification = activeExpiresAtBeforeSend > Date.now();

                isVerificationSent = true;
                isVerificationChecked = false;

                verificationExpiresAt = hasActiveVerification
                    ? activeExpiresAtBeforeSend
                    : data.expires_at
                        ? Number(data.expires_at) * 1000
                        : Date.now() + 5 * 60 * 1000;

                startVerificationTimer();
                startResendCooldown(button);
                setFeedback(options.feedback, data.message || "인증번호를 이메일로 발송했습니다.", "success");
            } catch (error) {
                setFeedback(options.feedback, "인증메일 발송 중 오류가 발생했습니다.");
                button.disabled = false;
            }
        }

        async function check() {
            const inputCode = options.input.value.trim();

            if (!isVerificationSent) {
                setFeedback(options.feedback, "인증번호를 먼저 전송해주세요.");
                return;
            }

            if (Date.now() > verificationExpiresAt) {
                expireVerification();
                setFeedback(options.feedback, "인증번호가 만료되었습니다. 다시 전송해주세요.");
                return;
            }

            if (!inputCode) {
                setFeedback(options.feedback, "인증번호 입력해주세요");
                return;
            }

            const formData = new FormData();
            formData.append("email", options.emailInput.value.trim());
            formData.append("code", inputCode);
            formData.append("purpose", options.purpose);

            try {
                const response = await fetch(options.verifyUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: formData,
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    isVerificationChecked = false;
                    setFeedback(options.feedback, data.message || "인증번호가 일치하지 않습니다.");
                    return;
                }

                isVerificationChecked = true;
                window.clearInterval(verificationTimerInterval);
                options.timer.textContent = "";
                options.timer.classList.remove("is-expired");
                setFeedback(options.feedback, data.message || "인증번호 확인 성공", "success");
            } catch (error) {
                isVerificationChecked = false;
                setFeedback(options.feedback, "인증번호 확인 중 오류가 발생했습니다.");
            }
        }

        function reset() {
            window.clearInterval(resendCooldownInterval);
            window.clearInterval(verificationTimerInterval);
            isVerificationSent = false;
            isVerificationChecked = false;
            verificationExpiresAt = 0;

            sendButtons.forEach((button) => {
                button.disabled = false;
                button.textContent = button.dataset.defaultText || button.textContent;
            });

            options.timer.textContent = "";
            options.timer.classList.remove("is-expired");
        }

        sendButtons.forEach((button) => {
            button.dataset.defaultText = button.textContent;
            button.addEventListener("click", () => send(button));
        });
        options.checkButton?.addEventListener("click", check);

        return {
            isSent: () => isVerificationSent,
            isChecked: () => isVerificationChecked,
            reset,
        };
    }

    document.querySelectorAll("[data-login-form]").forEach((form) => {
        const usernameInput = form.querySelector("[data-login-username]");
        const passwordInput = form.querySelector("[data-login-password]");
        const feedback = form.querySelector("[data-login-feedback]");
        const submitButton = form.querySelector('button[type="submit"]');

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            setFeedback(feedback, "");

            if (!usernameInput.value.trim() || !passwordInput.value.trim()) {
                setFeedback(feedback, "이메일과 비밀번호를 입력해주세요.");
                return;
            }

            try {
                submitButton.disabled = true;
                const response = await fetch(form.action, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: new FormData(form),
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    setFeedback(feedback, data.message || "이메일 또는 비밀번호가 일치하지 않습니다.");
                    return;
                }

                window.location.href = data.redirect_url || "/";
            } catch (error) {
                setFeedback(feedback, "로그인 중 오류가 발생했습니다.");
            } finally {
                submitButton.disabled = false;
            }
        });
    });

    document.querySelectorAll("[data-signup-form]").forEach((form) => {
        const sendVerificationButton = form.querySelector("[data-send-verification-btn]");
        const verificationTimer = form.querySelector("[data-verification-timer]");

        const agreeAllCheckbox = form.querySelector("[data-agree-all]");
        const agreeItemCheckboxes = Array.from(form.querySelectorAll("[data-agree-item]"));

        function syncAgreeAllCheckbox() {
            if (!agreeAllCheckbox || agreeItemCheckboxes.length === 0) {
                return;
            }

            agreeAllCheckbox.checked = agreeItemCheckboxes.every((checkbox) => checkbox.checked);
        }

        if (agreeAllCheckbox && agreeItemCheckboxes.length > 0) {
            agreeAllCheckbox.addEventListener("change", () => {
                agreeItemCheckboxes.forEach((checkbox) => {
                    checkbox.checked = agreeAllCheckbox.checked;
                });
            });

            agreeItemCheckboxes.forEach((checkbox) => {
                checkbox.addEventListener("change", syncAgreeAllCheckbox);
            });
        }

        const emailInput = form.querySelector("[data-signup-email]");
        const usernameInput = form.querySelector("[data-signup-username]");
        const emailFeedback = form.querySelector("[data-signup-email-feedback]");
        const duplicateButton = form.querySelector("[data-check-duplicate-btn]");
        const verificationInput = form.querySelector("[data-signup-verification]");
        const verificationFeedback = form.querySelector("[data-signup-verification-feedback]");
        const verificationCheckButton = form.querySelector("[data-check-verification-btn]");
        const passwordInput = form.querySelector("[data-signup-password]");
        const passwordFeedback = form.querySelector("[data-signup-password-feedback]");
        const passwordConfirmInput = form.querySelector("[data-signup-password-confirm]");
        const passwordConfirmFeedback = form.querySelector("[data-signup-password-confirm-feedback]");
        const agreementFeedback = form.querySelector("[data-signup-agreement-feedback]");
        let isEmailChecked = false;

        function isValidEmail(value) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }

        function isValidPassword(value) {
            return /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/.test(value);
        }

        const verificationController = createEmailVerificationController({
            sendButtons: [sendVerificationButton],
            checkButton: verificationCheckButton,
            input: verificationInput,
            emailInput,
            timer: verificationTimer,
            feedback: verificationFeedback,
            sendUrl: form.dataset.sendVerificationUrl,
            verifyUrl: form.dataset.verifyEmailUrl,
            purpose: "signup",
            beforeSend: () => {
                if (!isEmailChecked) {
                    alert("이메일 중복 확인 먼저해주세요.");
                    return false;
                }

                return true;
            },
        });

        const signupModal = form.closest(".custom-modal-backdrop");
        if (signupModal) {
            signupModal.addEventListener("modal:close", verificationController.reset);
        }

        emailInput?.addEventListener("input", () => {
            isEmailChecked = false;
            verificationController.reset();

            if (duplicateButton) {
                duplicateButton.disabled = false;
            }

            setFeedback(emailFeedback, "");
            setFeedback(verificationFeedback, "");
        });

        duplicateButton?.addEventListener("click", async () => {
            const email = emailInput.value.trim();
            isEmailChecked = false;

            if (!isValidEmail(email)) {
                setFeedback(emailFeedback, "이메일 형식이 맞지 않습니다");
                return;
            }

            try {
                duplicateButton.disabled = true;

                const response = await fetch(
                    `${duplicateButton.dataset.checkEmailUrl}?email=${encodeURIComponent(email)}`,
                );
                const data = await response.json();

                isEmailChecked = Boolean(data.available);
                duplicateButton.disabled = isEmailChecked;
                setFeedback(emailFeedback, data.message, data.available ? "success" : "error");
            } catch (error) {
                duplicateButton.disabled = false;
                setFeedback(emailFeedback, "이메일 중복 확인 중 오류가 발생했습니다.");
            }
        });

        passwordInput?.addEventListener("input", () => {
            setFeedback(
                passwordFeedback,
                passwordInput.value && !isValidPassword(passwordInput.value)
                    ? "잘못된 형식입니다 (8~16자, 영어 대소문자, 숫자, 특수문자)"
                    : "",
            );
        });

        passwordConfirmInput?.addEventListener("input", () => {
            setFeedback(
                passwordConfirmFeedback,
                passwordConfirmInput.value && passwordInput.value !== passwordConfirmInput.value
                    ? "비밀번호가 일치하지 않습니다"
                    : "",
            );
        });

        form.addEventListener("submit", (event) => {
            let isValid = true;

            if (!isEmailChecked) {
                alert("이메일 중복 확인 먼저해주세요.");
                isValid = false;
            }

            if (!verificationController.isSent() || !verificationController.isChecked()) {
                alert("이메일 인증은 필수입니다.");
                isValid = false;
            }

            if (!isValidPassword(passwordInput.value)) {
                setFeedback(passwordFeedback, "잘못된 형식입니다 (8~16자, 영어 대소문자, 숫자, 특수문자)");
                isValid = false;
            }

            if (passwordInput.value !== passwordConfirmInput.value) {
                setFeedback(passwordConfirmFeedback, "비밀번호가 일치하지 않습니다");
                isValid = false;
            }

            if (!agreeItemCheckboxes.every((checkbox) => checkbox.checked)) {
                alert("이용약관 동의, 개인정보수집 동의 필수입니다.");
                setFeedback(agreementFeedback, "이용약관 동의, 개인정보수집 동의 필수입니다.");
                isValid = false;
            } else {
                setFeedback(agreementFeedback, "");
            }

            if (!isValid) {
                event.preventDefault();
                return;
            }

            if (usernameInput) {
                usernameInput.value = emailInput.value.trim();
            }
        });
    });

    document.querySelectorAll("#accountPasswordChangeModal form").forEach((form) => {
        const currentPassword = form.querySelector('input[name="current_password"]');
        const newPassword = form.querySelector('input[name="new_password"]');
        const newPasswordConfirm = form.querySelector('input[name="new_password_confirm"]');
        const currentPasswordError = document.getElementById("accountCurrentPasswordError");
        const newPasswordError = document.getElementById("accountNewPasswordError");
        const newPasswordConfirmError = document.getElementById("accountNewPasswordConfirmError");

        function isValidPassword(value) {
            return /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/.test(value);
        }

        function setError(element, message) {
            if (element) element.textContent = message;
        }

        form.addEventListener("submit", (event) => {
            let isValid = true;

            setError(currentPasswordError, "");
            setError(newPasswordError, "");
            setError(newPasswordConfirmError, "");

            if (!currentPassword.value.trim()) {
                setError(currentPasswordError, "현재 비밀번호를 입력해주세요.");
                isValid = false;
            }

            if (!isValidPassword(newPassword.value)) {
                setError(newPasswordError, "비밀번호 형식을 다시 확인해주세요.");
                isValid = false;
            }

            if (newPassword.value !== newPasswordConfirm.value) {
                setError(newPasswordConfirmError, "비밀번호가 일치하지 않습니다.");
                isValid = false;
            }

            if (!isValid) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("[data-withdraw-verify-form]").forEach((form) => {
        const passwordInput = form.querySelector("[data-withdraw-password]");
        const passwordError = form.querySelector("[data-withdraw-password-error]");
        const nextButton = form.querySelector("[data-withdraw-verify-next]");

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            if (!passwordInput.value.trim()) {
                passwordError.textContent = "비밀번호를 입력하세요.";
                return;
            }

            try {
                nextButton.disabled = true;
                const response = await fetch(form.action, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: new FormData(form),
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    passwordError.textContent = data.message || "비밀번호가 일치하지 않습니다.";
                    return;
                }

                passwordError.textContent = "";
                closeModal(form.closest(".custom-modal-backdrop"), false);
                openModalById("accountWithdrawConfirmModal", nextButton);
            } catch (error) {
                passwordError.textContent = "비밀번호 확인 중 오류가 발생했습니다.";
            } finally {
                nextButton.disabled = false;
            }
        });
    });

    document.querySelectorAll("[data-password-reset-form]").forEach((form) => {
        const verifyStep = form.querySelector('[data-reset-step="verify"]');
        const passwordStep = form.querySelector('[data-reset-step="password"]');
        const emailInput = form.querySelector("[data-reset-email]");
        const emailFeedback = form.querySelector("[data-reset-email-feedback]");
        const sendCodeButton = form.querySelector("[data-reset-send-code]");
        const verificationInput = form.querySelector("[data-reset-verification]");
        const verificationTimer = form.querySelector("[data-reset-verification-timer]");
        const verificationFeedback = form.querySelector("[data-reset-verification-feedback]");
        const resendButton = form.querySelector("[data-reset-resend]");
        const verificationCheckButton = form.querySelector("[data-reset-verification-check]");
        const nextButton = form.querySelector("[data-reset-next]");
        const passwordInput = form.querySelector("[data-reset-password]");
        const passwordFeedback = form.querySelector("[data-reset-password-feedback]");
        const passwordConfirmInput = form.querySelector("[data-reset-password-confirm]");
        const passwordConfirmFeedback = form.querySelector("[data-reset-password-confirm-feedback]");

        function isValidEmail(value) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }

        function isValidPassword(value) {
            return /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/.test(value);
        }

        const verificationController = createEmailVerificationController({
            sendButtons: [sendCodeButton, resendButton],
            checkButton: verificationCheckButton,
            input: verificationInput,
            emailInput,
            timer: verificationTimer,
            feedback: verificationFeedback,
            sendUrl: form.dataset.sendVerificationUrl,
            verifyUrl: form.dataset.verifyEmailUrl,
            purpose: "password_reset",
            beforeSend: async () => {
                const email = emailInput.value.trim();

                if (!email) {
                    setFeedback(emailFeedback, "이메일을 입력해주세요.");
                    return false;
                }

                if (!isValidEmail(email)) {
                    setFeedback(emailFeedback, "등록되어있지 않은 이메일입니다.");
                    return false;
                }

                try {
                    const response = await fetch(`${sendCodeButton.dataset.checkEmailUrl}?email=${encodeURIComponent(email)}`);
                    const data = await response.json();

                    if (data.available) {
                        setFeedback(emailFeedback, "등록되어있지 않은 이메일입니다.");
                        return false;
                    }
                } catch (error) {
                    setFeedback(emailFeedback, "이메일 확인 중 오류가 발생했습니다.");
                    return false;
                }

                setFeedback(emailFeedback, "");
                return true;
            },
        });

        const resetModal = form.closest(".custom-modal-backdrop");
        if (resetModal) {
            resetModal.addEventListener("modal:close", verificationController.reset);
        }

        emailInput?.addEventListener("input", () => {
            verificationController.reset();
            setFeedback(emailFeedback, "");
            setFeedback(verificationFeedback, "");
        });

        nextButton?.addEventListener("click", () => {
            if (!verificationController.isSent()) {
                setFeedback(emailFeedback, "인증번호를 발송해주세요.");
                return;
            }

            if (!verificationController.isChecked()) {
                setFeedback(verificationFeedback, "인증번호 입력해주세요");
                return;
            }

            verifyStep.classList.add("hidden");
            passwordStep.classList.remove("hidden");
        });

        passwordInput?.addEventListener("input", () => {
            setFeedback(
                passwordFeedback,
                passwordInput.value && !isValidPassword(passwordInput.value)
                    ? "비밀번호 형식을 다시 확인해주세요."
                    : "",
            );
        });

        passwordConfirmInput?.addEventListener("input", () => {
            setFeedback(
                passwordConfirmFeedback,
                passwordConfirmInput.value && passwordInput.value !== passwordConfirmInput.value
                    ? "비밀번호 번호가 일치하지 않습니다."
                    : "",
            );
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            if (!verificationController.isChecked()) {
                setFeedback(verificationFeedback, "이메일 인증을 완료해주세요.");
                return;
            }

            if (!isValidPassword(passwordInput.value)) {
                setFeedback(passwordFeedback, "비밀번호 형식을 다시 확인해주세요.");
                return;
            }

            if (passwordInput.value !== passwordConfirmInput.value) {
                setFeedback(passwordConfirmFeedback, "비밀번호 번호가 일치하지 않습니다.");
                return;
            }

            try {
                const response = await fetch(form.dataset.passwordResetUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: new FormData(form),
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    alert(data.message || "비밀번호 재설정에 실패했습니다.");
                    setFeedback(passwordConfirmFeedback, data.message || "비밀번호 재설정에 실패했습니다.");
                    return;
                }

                alert(data.message);
                form.reset();
                verificationController.reset();
                verifyStep.classList.remove("hidden");
                passwordStep.classList.add("hidden");
                openModalById("loginModal");
            } catch (error) {
                setFeedback(passwordConfirmFeedback, "비밀번호 재설정 중 오류가 발생했습니다.");
            }
        });
    });

    console.log("Visa la Vista initialized successfully!");
})();
