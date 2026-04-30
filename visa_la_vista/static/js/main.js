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

    document.querySelectorAll("[data-signup-form]").forEach((form) => {
        const sendVerificationButton = form.querySelector("[data-send-verification-btn]");
        const verificationTimer = form.querySelector("[data-verification-timer]");
        let resendCooldownInterval = null;
        let verificationTimerInterval = null;

        function formatVerificationTime(totalSeconds) {
            const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
            const seconds = String(totalSeconds % 60).padStart(2, "0");

            return `${minutes}:${seconds}`;
        }

        function startResendCooldown() {
            let remainingSeconds = 30;

            window.clearInterval(resendCooldownInterval);
            sendVerificationButton.disabled = true;
            sendVerificationButton.textContent = `재전송`;

            resendCooldownInterval = window.setInterval(() => {
                remainingSeconds -= 1;

                if (remainingSeconds <= 0) {
                    window.clearInterval(resendCooldownInterval);
                    sendVerificationButton.disabled = false;
                    sendVerificationButton.textContent = "재전송";
                    return;
                }

                sendVerificationButton.textContent = `재전송`;
            }, 1000);
        }

        function startVerificationTimer() {
            let remainingSeconds = 5 * 60;

            window.clearInterval(verificationTimerInterval);
            verificationTimer.textContent = formatVerificationTime(remainingSeconds);
            verificationTimer.classList.remove("is-expired");

            verificationTimerInterval = window.setInterval(() => {
                remainingSeconds -= 1;

                if (remainingSeconds <= 0) {
                    window.clearInterval(verificationTimerInterval);
                    verificationTimer.textContent = "만료";
                    verificationTimer.classList.add("is-expired");
                    return;
                }

                verificationTimer.textContent = formatVerificationTime(remainingSeconds);
            }, 1000);
        }

        function stopVerificationTimers() {
            window.clearInterval(resendCooldownInterval);
            window.clearInterval(verificationTimerInterval);

            if (sendVerificationButton) {
                sendVerificationButton.disabled = false;
                sendVerificationButton.textContent = "전송";
            }

            if (verificationTimer) {
                verificationTimer.textContent = "";
                verificationTimer.classList.remove("is-expired");
            }
        }

        const signupModal = form.closest(".custom-modal-backdrop");
        if (signupModal) {
            signupModal.addEventListener("modal:close", stopVerificationTimers);
        }

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
        let isVerificationSent = false;
        let isVerificationChecked = false;

        function setFeedback(element, message, type = "error") {
            if (!element) return;
            element.textContent = message;
            element.classList.remove("success", "error");
            if (message) element.classList.add(type);
        }

        function isValidEmail(value) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }

        function isValidPassword(value) {
            return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$/.test(value);
        }

        duplicateButton?.addEventListener("click", () => {
            const email = emailInput.value.trim();
            isEmailChecked = false;

            if (!isValidEmail(email)) {
                setFeedback(emailFeedback, "이메일 형식이 맞지 않습니다");
                return;
            }

            isEmailChecked = true;
            setFeedback(emailFeedback, "사용 가능한 이메일입니다", "success");
        });

        if (sendVerificationButton && verificationTimer) {
            sendVerificationButton.addEventListener("click", () => {
                if (!isEmailChecked) {
                    alert("이메일 중복 확인 먼저해주세요.");
                    return;
                }

                isVerificationSent = true;
                isVerificationChecked = false;
                startResendCooldown();
                startVerificationTimer();
                alert("인증번호를 이메일로 발송했습니다. 이메일을 확인해 주세요.\n메일이 보이지 않을 경우 스팸함도 확인해 주세요.");
            });
        }

        verificationCheckButton?.addEventListener("click", () => {
            if (!verificationInput.value.trim()) {
                setFeedback(verificationFeedback, "인증번호 입력해주세요");
                return;
            }

            isVerificationChecked = true;
            setFeedback(verificationFeedback, "인증번호 확인 성공", "success");
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

            if (!isVerificationSent || !isVerificationChecked) {
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

    document.querySelectorAll("[data-password-reset-form]").forEach((form) => {
        const verifyStep = form.querySelector('[data-reset-step="verify"]');
        const passwordStep = form.querySelector('[data-reset-step="password"]');
        const emailInput = form.querySelector("[data-reset-email]");
        const emailFeedback = form.querySelector("[data-reset-email-feedback]");
        const emailCheckButton = form.querySelector("[data-reset-email-check]");
        const verificationInput = form.querySelector("[data-reset-verification]");
        const verificationFeedback = form.querySelector("[data-reset-verification-feedback]");
        const resendButton = form.querySelector("[data-reset-resend]");
        const verificationCheckButton = form.querySelector("[data-reset-verification-check]");
        const nextButton = form.querySelector("[data-reset-next]");
        const passwordInput = form.querySelector("[data-reset-password]");
        const passwordFeedback = form.querySelector("[data-reset-password-feedback]");
        const passwordConfirmInput = form.querySelector("[data-reset-password-confirm]");
        const passwordConfirmFeedback = form.querySelector("[data-reset-password-confirm-feedback]");
        let isEmailChecked = false;
        let isVerificationChecked = false;

        function setFeedback(element, message, type = "error") {
            if (!element) return;
            element.textContent = message;
            element.classList.remove("success", "error");
            if (message) element.classList.add(type);
        }

        function isValidEmail(value) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }

        function isValidPassword(value) {
            return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$/.test(value);
        }

        emailCheckButton?.addEventListener("click", () => {
            if (!isValidEmail(emailInput.value.trim())) {
                setFeedback(emailFeedback, "이미 등록되어있는 이메일입니다");
                isEmailChecked = false;
                return;
            }

            isEmailChecked = true;
            setFeedback(emailFeedback, "");
        });

        resendButton?.addEventListener("click", () => {
            if (!isEmailChecked) {
                setFeedback(emailFeedback, "이미 등록되어있는 이메일입니다");
                return;
            }

            alert("인증번호를 이메일로 발송했습니다. 이메일을 확인해 주세요.");
        });

        verificationCheckButton?.addEventListener("click", () => {
            if (!verificationInput.value.trim()) {
                setFeedback(verificationFeedback, "인증번호 입력해주세요");
                isVerificationChecked = false;
                return;
            }

            isVerificationChecked = true;
            setFeedback(verificationFeedback, "인증번호 확인 성공", "success");
        });

        nextButton?.addEventListener("click", () => {
            if (!isEmailChecked) {
                setFeedback(emailFeedback, "이미 등록되어있는 이메일입니다");
                return;
            }

            if (!isVerificationChecked) {
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

        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (!isValidPassword(passwordInput.value)) {
                setFeedback(passwordFeedback, "비밀번호 형식을 다시 확인해주세요.");
                return;
            }

            if (passwordInput.value !== passwordConfirmInput.value) {
                setFeedback(passwordConfirmFeedback, "비밀번호 번호가 일치하지 않습니다.");
                return;
            }

            alert("비밀번호가 재설정되었습니다.");
            openModalById("loginModal");
        });
    });

    console.log("Chatwise initialized successfully!");
})();
