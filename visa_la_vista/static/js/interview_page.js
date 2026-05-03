(function () {
    "use strict";
    var profile_context = ""

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
    let lastSessionData = null;
    let recorderState = null;

    // ─── UI helpers ───────────────────────────────────────────────────────────

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

    function setMode(mode) {
        selectedMode = mode;
        modeButtons.forEach((button) => {
            button.classList.toggle("is-active", button.dataset.modeButton === mode);
        });
        modeDescriptionCards.forEach((card) => {
            card.classList.toggle("is-highlighted", card.dataset.modeDescription === mode);
        });
    }

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

    // ─── API ──────────────────────────────────────────────────────────────────

    async function createInterviewSession(requestBody, audioFile = null) {
        let body;
        let headers = {};

        if (audioFile) {
            // Multipart: send payload as form field + audio file
            body = new FormData();
            body.append("payload", JSON.stringify(requestBody));
            body.append("audio_file", audioFile, audioFile.name);
            // DO NOT set Content-Type — browser sets it with boundary automatically

            console.log("audio file name:", audioFile.name);
            console.log("audio file size:", audioFile.size, "bytes");
            console.log("audio file type:", audioFile.type);
            console.log("FormData payload field:", body.get("payload"));
            console.log("FormData audio_file field:", body.get("audio_file"));

        } else {
            // Plain JSON: no audio
            body = JSON.stringify(requestBody);
            headers["Content-Type"] = "application/json";
        }

        const response = await fetch("/service/interview_session_create/", {
            method: "POST",
            headers,
            body,
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = "";

        console.log("--- Stream Started ---");
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            console.log("Received chunk:", chunk);
            fullResponse += chunk;
        }
        console.log("--- Stream Finished ---");

        try {
            return JSON.parse(fullResponse);
        } catch (e) {
            console.error("Failed to parse JSON:", fullResponse);
            return { error: "Invalid JSON", raw: fullResponse };
        }

    }

    // ─── File validation ──────────────────────────────────────────────────────

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

    // ─── Event listeners ──────────────────────────────────────────────────────

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
        if (event.target === uploadModal) closeUploadModal();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !uploadModal.classList.contains("hidden")) closeUploadModal();
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

    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!uploadedFile) {
            alert("PDF파일을 업로드해주세요!");
            return;
        }
        const formData = new FormData();
        formData.append("pdf_file", uploadedFile);
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch("/service/extract-pdf/", {
                method: "POST",
                body: formData,
                headers: { "X-CSRFToken": csrftoken }
            });
            const data = await response.json();
            if (data.status === "success") {
                profile_context = data.text;
                uploadCompleted = true;
                closeUploadModal();
                setMode("practice");
                showPanel("sidebar", "select");
                showPanel("stage", "select");
            } else {
                alert("Extraction failed: " + data.message);
            }
        } catch (error) {
            console.error("Error connecting to server:", error);
            alert("Server error occurred.");
        }
    });

    practiceStartBtn.addEventListener("click", async () => {
        if (!practiceQuestionCount.value) {
            alert("질문 개수를 선택해주세요");
            return;
        }
        practiceStartBtn.disabled = true;
        try {
            const myData = {
                mode: "practice",
                max_q: practiceQuestionCount.value || 3,
                profile_context: profile_context,
                history: [],
                is_over: false,
                user_answer: "",
                current_question: '',
            };
            const data = await createInterviewSession(myData);  // no audio
            console.log("practiceStartBtn data:", data);

            if (data.success) {
                lastSessionData = data.data;  // save for mic round
                const targetElement = document.getElementById("practice-question-text");
                if (targetElement) {
                    targetElement.textContent = data.data.question;
                    alert("Interview Started!");
                }
            }
        } catch (error) {
            console.error("Fetch/Stream Error:", error);
            alert("연습 모드를 시작하지 못했습니다.");
        } finally {
            practiceStartBtn.disabled = false;
        }
    });

    realStartBtn.addEventListener("click", () => {
        realStartBtn.disabled = true;
        createInterviewSession({ mode: "real" })
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

    // ─── Recording ────────────────────────────────────────────────────────────

    micButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            const audioBar = button.closest(".audio-bar");
            const isRecording = button.classList.toggle("is-recording");
            audioBar.classList.toggle("is-recording", isRecording);
            button.setAttribute("aria-label", isRecording ? "Stop Recording" : "Start Recording");

            if (isRecording) {
                try {
                    await startRecording();
                } catch (err) {
                    console.error("Mic access denied:", err);
                    button.classList.remove("is-recording");
                }
            } else {
                await stopAndSend();
                practiceAnswerText.classList.remove("hidden");
                realAnswerAudio.classList.remove("hidden");
            }
        });
    });

    async function startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new AudioContext();
        const sampleRate = audioContext.sampleRate;
        const sourceNode = audioContext.createMediaStreamSource(stream);
        const processorNode = audioContext.createScriptProcessor(4096, 1, 1);
        let chunks = [];

        processorNode.onaudioprocess = (event) => {
            chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));
        };

        sourceNode.connect(processorNode);
        processorNode.connect(audioContext.destination);
        recorderState = { stream, audioContext, processorNode, sourceNode, chunks, sampleRate };
    }

    async function stopAndSend() {       // ← inside the IIFE, has access to everything
        if (!recorderState) return;

        const { chunks, sampleRate, processorNode, sourceNode, audioContext, stream } = recorderState;

        const blob = encodeWav(chunks, sampleRate);
        const file = new File([blob], "answer.wav", { type: "audio/wav" });

        processorNode.disconnect();
        sourceNode.disconnect();
        audioContext.close();
        stream.getTracks().forEach(track => track.stop());

        try {
            const requestBody = {
                mode: "practice",
                max_q: parseInt(practiceQuestionCount.value) || 3,
                profile_context: profile_context,
                history: lastSessionData ? lastSessionData.history : [],
                current_question: lastSessionData ? lastSessionData.question : "",
                is_over: false,
                user_answer: null,
            };

            console.log("stopAndSend payload:", JSON.stringify(requestBody));
            console.log("Audio file size:", file.size, "bytes");

            const data = await createInterviewSession(requestBody, file);  // ← pass file
            console.log("stopAndSend result:", data);

            if (data.success) {
                lastSessionData = data.data;  // save for next round
                // const targetElement = document.getElementById("practice-question-text");
                // if (targetElement) {
                //     targetElement.textContent = data.data.question;
                // }
                const questionEl = document.getElementById("practice-question-text");
                if (questionEl) {
                    questionEl.textContent = data.data.question;
                }

                if (data.data.answer_text) {
                    practiceAnswerText.querySelector("span").textContent = data.data.answer_text;
                    practiceAnswerText.classList.remove("hidden");
                }
            }
        } catch (error) {
            console.error("Upload Error:", error);
            alert("Failed to send recording.");
        } finally {
            recorderState = null;
        }
    }

    // ─── WAV encoding ─────────────────────────────────────────────────────────

    function writeString(view, offset, string) {
        for (let i = 0; i < string.length; i += 1) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }

    function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
        if (outputSampleRate === inputSampleRate) return buffer;
        const ratio = inputSampleRate / outputSampleRate;
        const length = Math.round(buffer.length / ratio);
        const result = new Float32Array(length);
        let inputOffset = 0;
        for (let i = 0; i < length; i += 1) {
            const nextOffset = Math.round((i + 1) * ratio);
            let sum = 0, count = 0;
            for (let j = inputOffset; j < nextOffset && j < buffer.length; j += 1) {
                sum += buffer[j];
                count += 1;
            }
            result[i] = count ? sum / count : 0;
            inputOffset = nextOffset;
        }
        return result;
    }

    function encodeWav(buffers, inputSampleRate) {
        const samples = mergeBuffers(buffers);
        const outputSampleRate = 16000;
        const resampled = downsampleBuffer(samples, inputSampleRate, outputSampleRate);
        const buffer = new ArrayBuffer(44 + resampled.length * 2);
        const view = new DataView(buffer);
        writeString(view, 0, "RIFF");
        view.setUint32(4, 36 + resampled.length * 2, true);
        writeString(view, 8, "WAVE");
        writeString(view, 12, "fmt ");
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 1, true);
        view.setUint32(24, outputSampleRate, true);
        view.setUint32(28, outputSampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(view, 36, "data");
        view.setUint32(40, resampled.length * 2, true);
        let offset = 44;
        for (let i = 0; i < resampled.length; i += 1) {
            const sample = Math.max(-1, Math.min(1, resampled[i]));
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
            offset += 2;
        }
        return new Blob([view], { type: "audio/wav" });
    }

    function mergeBuffers(buffers) {
        const length = buffers.reduce((total, buffer) => total + buffer.length, 0);
        const result = new Float32Array(length);
        let offset = 0;
        buffers.forEach((buffer) => {
            result.set(buffer, offset);
            offset += buffer.length;
        });
        return result;
    }

    // ─── Init ─────────────────────────────────────────────────────────────────

    setMode("practice");
    makeWaveforms();
    openUploadModal("practice");

})();