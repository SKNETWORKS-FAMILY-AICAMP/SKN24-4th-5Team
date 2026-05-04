(function () {
    "use strict";

    let controller = null;

    const chatPage = document.getElementById("chat-page");
    const assistantIconUrl = chatPage.dataset.assistantIcon;
    const chatMessageUrl = chatPage.dataset.chatMessageUrl;
    const defaultAssistantMessage = "궁금한 입시 정보를 입력해보세요.";

    const pageData = JSON.parse(document.getElementById("chat-page-data").textContent);

    let messages = (pageData.messages || []).map((m) => ({
        ...m,
        timestamp: new Date(m.timestamp),
    }));

    if (!messages.length) {
        messages = [
            {
                id: "sample",
                role: "assistant",
                content: defaultAssistantMessage,
                timestamp: new Date(),
            },
        ];
    }

    let conversations = pageData.conversations || [];
    let activeConversation = pageData.activeConversationId || (conversations[0] && conversations[0].id) || null;

    const chatMessagesContainer = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const conversationsList = document.getElementById("conversations-list");
    const newChatBtn = document.getElementById("new-chat-btn");
    const chatTitleDisplay = document.getElementById("chat-title-display");

    function escapeHtml(v) {
        return v
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function formatTime(date) {
        return new Date(date).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function getCsrfToken() {
        const cookie = document.cookie.split("; ").find((r) => r.startsWith("csrftoken="));
        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    // =========================
    // MESSAGES (UI 안정화)
    // =========================
    function renderMessages() {
        chatMessagesContainer.innerHTML = "";

        const container = document.createElement("div");
        container.className = "messages-container";

        messages.forEach((msg) => {
            const el = document.createElement("div");
            const isUser = msg.role === "user";

            el.className = `message ${msg.role}`;

            el.innerHTML = `
                <div class="message-avatar">
                    ${isUser ? "U" : `<img src="${assistantIconUrl}">`}
                </div>
                <div class="message-content">
                    <p class="message-text">${escapeHtml(msg.content)}</p>
                    <p class="message-time">${formatTime(msg.timestamp)}</p>
                </div>
            `;

            container.appendChild(el);
        });

        chatMessagesContainer.appendChild(container);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    // =========================
    // CONVERSATIONS (기존 UI 유지 + 제목 sync)
    // =========================
    function renderConversations() {
        conversationsList.innerHTML = "";

        // 최신순 정렬
        const sorted = [...conversations].sort((a, b) => {
            const aTime = a.messages?.length ? new Date(a.messages[a.messages.length - 1].timestamp) : 0;
            const bTime = b.messages?.length ? new Date(b.messages[b.messages.length - 1].timestamp) : 0;
            return bTime - aTime;
        });

        const groups = [...new Set(sorted.map((c) => c.group || "오늘"))];

        groups.forEach((group) => {
            const groupEl = document.createElement("div");
            groupEl.className = "conversation-group";
            groupEl.innerHTML = `<p class="conversation-group-title">${group}</p>`;

            sorted
            .filter((c) => (c.group || "오늘") === group)
                .forEach((conv) => {
                    const item = document.createElement("div");
                    item.style.cssText = "display:flex; align-items:center; width:100%; margin:0; padding:0;";

                    item.innerHTML = `
            <button type="button"
                class="conversation-btn ${conv.id === activeConversation ? "active" : ""}"
                data-conversation-id="${conv.id}"
                style="flex:1; margin:0; padding:8px 12px; text-align:left; overflow:hidden;">
                <span class="conversation-title" style="display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    ${escapeHtml(conv.title || "새 채팅")}
                </span>
            </button>
            <button type="button"
                class="conversation-delete-btn"
                data-delete-conversation-id="${conv.id}"
                ${conv.isTemporary ? 'data-temporary-conversation="true"' : ""}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
            </button>
        `;

                    groupEl.appendChild(item);
                });

            conversationsList.appendChild(groupEl);
        });

        const active = conversations.find((c) => c.id === activeConversation);
        if (active) chatTitleDisplay.innerText = active.title || "새 채팅";
    }
    // =========================
    // SWITCH CHAT (🔥 핵심 수정)
    // =========================
    function setActiveConversation(id) {
        const conv = conversations.find((c) => c.id === id);
        if (!conv) return;

        activeConversation = id;

        messages = (conv.messages || []).map((m) => ({
            ...m,
            timestamp: new Date(m.timestamp),
        }));

        if (!messages.length) {
            messages = [
                {
                    id: "empty",
                    role: "assistant",
                    content: defaultAssistantMessage,
                    timestamp: new Date(),
                },
            ];
        }

        renderMessages();
        renderConversations();
    }

    // =========================
    // DELETE
    // =========================
    async function deleteConversation(id) {
        const target = conversations.find((c) => c.id === id);

        if (target && !target.isTemporary) {
            await fetch(`/service/api/chat/conversations/${id}/delete`, {
                method: "POST",
                headers: { "X-CSRFToken": getCsrfToken() },
            });
        }

        const isActive = activeConversation === id;
        conversations = conversations.filter((c) => c.id !== id);

        if (!conversations.length) {
            startNewChat();
            return;
        }

        if (isActive) {
            setActiveConversation(conversations[0].id);
        } else {
            renderConversations();
        }
    }

    // =========================
    // SEND (스트리밍 유지)
    // =========================
    async function sendMessage(content) {
        if (!content.trim()) return;
        if (controller) controller.abort();
        controller = new AbortController();

        messages = messages.filter((msg) => msg.id !== "sample" && msg.id !== "empty");

        messages.push({
            id: Date.now().toString(),
            role: "user",
            content,
            timestamp: new Date(),
        });

        let assistantMsg = { id: "stream", role: "assistant", content: "", timestamp: new Date() };
        messages.push(assistantMsg);
        renderMessages();
        messageInput.value = "";

        const res = await fetch(chatMessageUrl, {
            method: "POST",
            signal: controller.signal,
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
            body: JSON.stringify({
                conversation_id: conversations.find((c) => c.id === activeConversation)?.isTemporary
                    ? null
                    : activeConversation,
                content,
            }),
        });

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let full = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            for (let line of chunk.split("\n")) {
                if (!line.startsWith("data:")) continue;
                const data = line.replace("data:", "").trim();
                if (data === "[DONE]") break;

                try {
                    const json = JSON.parse(data);

                    // 대화방 메타 정보 처리
                    if (json.type === "meta") {
                        const activeConv = conversations.find((c) => c.id === activeConversation);
                        const existingConv = conversations.find((c) => c.id === json.conversation_id);

                        if (!existingConv) {
                            if (activeConv?.isTemporary) {
                                activeConv.id = json.conversation_id;
                                activeConv.title = json.title || activeConv.title;
                                activeConv.group = json.group || "오늘";
                                activeConv.isTemporary = false;
                            } else {
                                conversations.unshift({
                                    id: json.conversation_id,
                                    title: json.title,
                                    group: json.group || "오늘",
                                    messages: [],
                                    isTemporary: false,
                                });
                            }
                        }
                        activeConversation = json.conversation_id;
                        renderConversations();
                        continue;
                    }

                    // LLM 토큰 처리
                    if (json.token) {
                        full += json.token;
                        assistantMsg.content = full;
                        renderMessages();
                    }
                } catch (e) {}
            }
        }

        // 대화방 메시지 업데이트
        const conv = conversations.find((c) => c.id === activeConversation);
        if (conv) {
            if (conv.title === "새 채팅") conv.title = content.slice(0, 40);
            conv.messages = [...messages];
        }
        renderConversations();
    }

    // =========================
    // NEW CHAT
    // =========================
    function startNewChat() {
        const newConv = {
            id: `temp-${Date.now()}`,
            title: "새 채팅",
            group: "오늘",
            messages: [],
            isTemporary: true,
        };

        conversations.unshift(newConv);
        setActiveConversation(newConv.id);
    }

    // =========================
    // EVENTS (🔥 엔터 수정 핵심)
    // =========================
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        sendMessage(messageInput.value);
    });

    // 🔥 FIX: Enter 줄바꿈 완전 차단
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.requestSubmit();
        }
    });

    conversationsList.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-conversation-id]");
        if (btn) setActiveConversation(btn.dataset.conversationId);

        const del = e.target.closest("[data-delete-conversation-id]");
        if (del) deleteConversation(del.dataset.deleteConversationId);
    });

    newChatBtn.addEventListener("click", startNewChat);

    if (!conversations.length) {
        startNewChat();
    } else {
        renderConversations();
        renderMessages();
    }
})();
