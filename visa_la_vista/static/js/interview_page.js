(function () {
    "use strict";

    const interviewPage = document.getElementById("interview-page");
    const pageData = JSON.parse(document.getElementById("interview-page-data").textContent);
    const interviewSessionUrl = interviewPage.dataset.interviewSessionUrl;
    const fileInput = document.getElementById("visa-pdf-input");
    const fileNameDisplay = document.getElementById("selected-file-name");
    const dropzone = document.getElementById("upload-dropzone");
    const uploadForm = document.getElementById("interview-upload-form");
    const uploadModal = document.getElementById("upload-modal");
    const uploadModalClose = document.getElementById("upload-modal-close");
    const practiceQuestionCount = document.getElementById("practice-question-count");
    const practiceStartBtn = document.getElementById("practice-start-btn");
    const realStartBtn = document.getElementById("real-start-btn");
    const realTimer = document.getElementById("real-timer");
    const realQuestionLine = document.getElementById("real-question-line");
    const practiceAnswerText = document.getElementById("practice-answer-text");
    const realAnswerAudio = document.getElementById("real-answer-audio");
    const modeButtons = document.querySelectorAll("[data-mode-button]");
    const modeDescriptionCards = document.querySelectorAll("[data-mode-description]");
    const endButtons = document.querySelectorAll("[data-end-interview]");
    const micButtons = document.querySelectorAll("[data-mic-button]");

    const interviewQuestions = pageData.questions || { practice: [], real: [] };

    let selectedMode = "practice";
    let uploadedFile = null;
    let uploadCompleted = false;
    let realTimerId = null;
    let remainingSeconds = 7 * 60;

    function makeWaveforms() {
        document.querySelectorAll(".waveform").forEach((waveform) => {
            waveform.innerHTML = "";

            for (let index = 0; index < 54; index += 1) {
                const bar = document.createElement("span");
                const height = 5 + ((index * 11) % 28);
                bar.style.setProperty("--wave-height", `${height}px`);
                bar.style.setProperty("--wave-index", index);
                waveform.appendChild(bar);
            }
        });
    }

    function showPanel(type, panelName) {
        document.querySelectorAll(`[data-${type}-panel]`).forEach((panel) => {
            panel.classList.toggle("is-active", panel.dataset[`${type}Panel`] === panelName);
        });
    }

    // 선택 중인 모드와 같은 설명 카드만 강조합니다.
    function setMode(mode) {
        selectedMode = mode;
        modeButtons.forEach((button) => {
            button.classList.toggle("is-active", button.dataset.modeButton === mode);
        });
        modeDescriptionCards.forEach((card) => {
            card.classList.toggle("is-highlighted", card.dataset.modeDescription === mode);
        });
    }

    // 시작 후에는 선택 화면을 숨기고 해당 모드 진행 화면으로 전환합니다.
    function showInterviewMode(mode) {
        setMode(mode);
        showPanel("sidebar", mode);
        showPanel("stage", mode);
        renderQuestion(mode);
    }

    function openUploadModal(mode) {
        setMode(mode);
        uploadModal.classList.remove("hidden");
        uploadModalClose.focus();
    }

    // 파일 업로드 전에는 모달을 먼저 열고, 업로드 후에는 바로 모드로 진입합니다.
    function selectInterviewMode(mode) {
        if (!uploadCompleted) {
            openUploadModal(mode);
            return;
        }

        showInterviewMode(mode);
    }

    function closeUploadModal() {
        uploadModal.classList.add("hidden");
    }

    function resetInterview() {
        window.clearInterval(realTimerId);
        realTimerId = null;
        remainingSeconds = 7 * 60;
        realTimer.textContent = "07 : 00";
        realQuestionLine.textContent = "";
        practiceAnswerText.classList.add("hidden");
        realAnswerAudio.classList.add("hidden");
        document.querySelectorAll(".audio-bar").forEach((bar) => bar.classList.remove("is-recording"));
        micButtons.forEach((button) => {
            button.classList.remove("is-recording");
            button.setAttribute("aria-label", "답변 녹음 시작");
        });
    }

    function formatTimer(totalSeconds) {
        const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
        const seconds = String(totalSeconds % 60).padStart(2, "0");

        return `${minutes} : ${seconds}`;
    }

    function getCsrfToken() {
        const cookie = document.cookie.split("; ").find((row) => row.startsWith("csrftoken="));

        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    function renderQuestion(mode) {
        const [question] = interviewQuestions[mode] || [];
        if (!question) return;

        if (mode === "practice") {
            document.getElementById("practice-question-text").textContent = question.text;
            practiceAnswerText.querySelector("span").textContent = question.text;
        }

        if (mode === "real") {
            realQuestionLine.textContent = question.text;
        }
    }

    function createInterviewSession(mode) {
        return fetch(interviewSessionUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({
                mode: mode,
                uploaded_file_name: uploadedFile ? uploadedFile.name : "",
                question_count: mode === "practice" ? practiceQuestionCount.value : null,
            }),
        }).then((response) => (response.ok ? response.json() : Promise.reject(response)));
    }

    function validateFile(file) {
        if (!file) {
            alert("PDF파일을 업로드해주세요");
            return false;
        }

        if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
            alert("파일형식이 올바르지 않습니다. PDF형식 의 파일인지 확인하세요.");
            return false;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert("파일 크기는 5MB 이하여야 합니다.");
            return false;
        }

        return true;
    }

    function setUploadedFile(file) {
        if (!validateFile(file)) {
            fileInput.value = "";
            uploadedFile = null;
            fileNameDisplay.textContent = "";
            return;
        }

        uploadedFile = file;
        fileNameDisplay.textContent = file.name;
    }

    modeButtons.forEach((button) => {
        button.addEventListener("mouseenter", () => setMode(button.dataset.modeButton));
        button.addEventListener("focus", () => setMode(button.dataset.modeButton));
        button.addEventListener("click", () => selectInterviewMode(button.dataset.modeButton));
    });

    modeDescriptionCards.forEach((card) => {
        card.addEventListener("mouseenter", () => setMode(card.dataset.modeDescription));
        card.addEventListener("focus", () => setMode(card.dataset.modeDescription));
        card.addEventListener("click", () => selectInterviewMode(card.dataset.modeDescription));
    });

    uploadModalClose.addEventListener("click", closeUploadModal);
    uploadModal.addEventListener("click", (event) => {
        if (event.target === uploadModal) {
            closeUploadModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !uploadModal.classList.contains("hidden")) {
            closeUploadModal();
        }
    });

    fileInput.addEventListener("change", () => {
        const [file] = fileInput.files;
        setUploadedFile(file);
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add("is-dragging");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove("is-dragging");
        });
    });

    dropzone.addEventListener("drop", (event) => {
        const files = Array.from(event.dataTransfer.files);
        if (files.length > 1) {
            alert("PDF파일을 하나만 올려주세요");
            return;
        }

        setUploadedFile(files[0]);
    });

    uploadForm.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!uploadedFile) {
            alert("PDF파일을 업로드해주세요");
            return;
        }

        uploadCompleted = true;
        closeUploadModal();
        setMode("practice");
        showPanel("sidebar", "select");
        showPanel("stage", "select");
    });

    practiceStartBtn.addEventListener("click", () => {
        if (!practiceQuestionCount.value) {
            alert("질문 개수를 선택해주세요");
            return;
        }

        practiceStartBtn.disabled = true;
        createInterviewSession("practice")
            .then((data) => {
                if (data.question) {
                    document.getElementById("practice-question-text").textContent = data.question.text;
                }
            })
            .catch(() => {
                practiceStartBtn.disabled = false;
                alert("연습 모드를 시작하지 못했습니다.");
            });
    });

    realStartBtn.addEventListener("click", () => {
        realStartBtn.disabled = true;

        createInterviewSession("real")
            .then((data) => {
                if (data.question) {
                    realQuestionLine.textContent = data.question.text;
                }

                window.clearInterval(realTimerId);
                realTimerId = window.setInterval(() => {
                    remainingSeconds -= 1;
                    realTimer.textContent = formatTimer(remainingSeconds);

                    if (remainingSeconds <= 0) {
                        window.clearInterval(realTimerId);
                        realTimerId = null;
                    }
                }, 1000);
            })
            .catch(() => {
                realStartBtn.disabled = false;
                alert("실전 모드를 시작하지 못했습니다.");
            });
    });

    endButtons.forEach((button) => {
        button.addEventListener("click", () => {
            resetInterview();
            practiceStartBtn.disabled = false;
            realStartBtn.disabled = false;
            showPanel("sidebar", "select");
            showPanel("stage", "select");
        });
    });

    micButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const audioBar = button.closest(".audio-bar");
            const isRecording = button.classList.toggle("is-recording");
            audioBar.classList.toggle("is-recording", isRecording);
            button.setAttribute("aria-label", isRecording ? "녹음 중단" : "답변 녹음 시작");

            if (!isRecording) {
                practiceAnswerText.classList.remove("hidden");
                realAnswerAudio.classList.remove("hidden");
            }
        });
    });

    setMode("practice");
    makeWaveforms();
    openUploadModal("practice");
})();
