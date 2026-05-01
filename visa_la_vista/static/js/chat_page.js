(function () {
    "use strict";

    const chatPage = document.getElementById("chat-page");
    const assistantIconUrl = chatPage.dataset.assistantIcon;
    const chatMessageUrl = chatPage.dataset.chatMessageUrl;
    const defaultAssistantMessage = "Hello! I'm here to help you. What would you like to talk about today?";
    const pageData = JSON.parse(document.getElementById("chat-page-data").textContent);
    let messages = (pageData.messages || []).map((message) => ({
        ...message,
        timestamp: new Date(message.timestamp),
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
    const sendBtn = document.getElementById("send-btn");
    const conversationsList = document.getElementById("conversations-list");
    const newChatBtn = document.getElementById("new-chat-btn");
    const chatTitleDisplay = document.getElementById("chat-title-display");

    function escapeHtml(value) {
        return value
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    function initChat() {
        const conversation = conversations.find((conv) => conv.id === activeConversation);
        if (conversation) {
            chatTitleDisplay.innerText = conversation.title;
        }
        renderMessages();
        renderConversations();
        updateSendButton();
    }

    function renderMessages() {
        chatMessagesContainer.innerHTML = "";
        const container = document.createElement("div");
        container.className = "messages-container";

        messages.forEach((msg) => {
            const messageEl = document.createElement("div");
            const isUser = msg.role === "user";
            messageEl.className = `message ${msg.role}`;
            messageEl.innerHTML = `
                    <div class="message-avatar">${isUser ? "U" : `<img src="${assistantIconUrl}" alt="">`}</div>
                    <div class="message-content">
                        <p class="message-text">${escapeHtml(msg.content)}</p>
                        <p class="message-time">${formatTime(msg.timestamp)}</p>
                    </div>`;
            container.appendChild(messageEl);
        });

        chatMessagesContainer.appendChild(container);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    function renderConversations() {
        conversationsList.innerHTML = "";

        const groups = [...new Set(conversations.map((conv) => conv.group))];
        groups.forEach((group) => {
            const groupEl = document.createElement("div");
            groupEl.className = "conversation-group";
            groupEl.innerHTML = `<p class="conversation-group-title">${group}</p>`;

            conversations
                .filter((conv) => conv.group === group)
                .forEach((conv) => {
                    const item = document.createElement("div");
                    item.className = `conversation-item ${conv.id === activeConversation ? "is-active" : ""}`;
                    item.innerHTML = `
                            <button type="button" class="conversation-btn ${conv.id === activeConversation ? "active" : ""}" data-conversation-id="${conv.id}">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                    <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
                                </svg>
                                <span class="conversation-title">${escapeHtml(conv.title)}</span>
                            </button>
                            <button type="button" class="conversation-delete-btn" data-delete-conversation-id="${conv.id}" aria-label="${escapeHtml(conv.title)} 대화 삭제">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true">
                                    <line x1="18" y1="6" x2="6" y2="18" />
                                    <line x1="6" y1="6" x2="18" y2="18" />
                                </svg>
                            </button>`;
                    groupEl.appendChild(item);
                });

            conversationsList.appendChild(groupEl);
        });
    }

    function setActiveConversation(conversationId) {
        const conversation = conversations.find((conv) => conv.id === conversationId);
        if (!conversation) return;

        activeConversation = conversationId;
        chatTitleDisplay.innerText = conversation.title;
        messages = (conversation.messages || []).map((message) => ({
            ...message,
            timestamp: new Date(message.timestamp),
        }));
        renderConversations();
        renderMessages();
    }

    function deleteConversation(conversationId) {
        const deletedActiveConversation = activeConversation === conversationId;
        conversations = conversations.filter((conv) => conv.id !== conversationId);

        if (!conversations.length) {
            startNewChat();
            return;
        }

        if (deletedActiveConversation) {
            messages = [
                {
                    id: "1",
                    role: "assistant",
                    content: defaultAssistantMessage,
                    timestamp: new Date(),
                },
            ];
            setActiveConversation(conversations[0].id);
            renderMessages();
        } else {
            renderConversations();
        }
    }

async function sendMessage(content) {
    if (!content.trim()) return;

    // ✅ 1. conversation 없으면 먼저 생성
    if (!activeConversation) {
        const res = await fetch("/api/chat/create-conversation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ content: content.trim() }),
        });

        const data = await res.json();

        activeConversation = data.conversation_id;

        // 👉 사이드바에 추가
        const newConv = {
            id: data.conversation_id,
            title: data.title,
            group: "오늘",
            messages: [],
        };

        conversations.unshift(newConv);
        chatTitleDisplay.innerText = data.title;

        renderConversations();
    }

    // ✅ 2. 사용자 메시지 추가
    const userMessage = {
        id: Date.now().toString(),
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
    };

    messages.push(userMessage);
    renderMessages();

    messageInput.value = "";
    updateSendButton();

    // ✅ 3. assistant placeholder (스트리밍용)
    let assistantMessage = {
        id: "stream",
        role: "assistant",
        content: "",
        timestamp: new Date(),
    };

    messages.push(assistantMessage);
    renderMessages();

    // ✅ 4. 스트리밍 요청
    const response = await fetch(chatMessageUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
            conversation_id: activeConversation,
            content: content.trim(),
        }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let fullText = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (let line of lines) {
            if (line.startsWith("data:")) {
                const data = line.replace("data:", "").trim();

                if (data === "[DONE]") {
                    return;
                }

                try {
                    const json = JSON.parse(data);
                    const token = json.token;

                    fullText += token;

                    // ✅ 스트리밍 업데이트
                    assistantMessage.content = fullText;
                    renderMessages();

                } catch (e) {}
            }
        }
    }
}
    // function sendMessage(content) {
    //     if (!content.trim()) return;

    //     const userMessage = {
    //         id: Date.now().toString(),
    //         role: "user",
    //         content: content.trim(),
    //         timestamp: new Date(),
    //     };
    //     messages.push(userMessage);
    //     renderMessages();
    //     messageInput.value = "";
    //     updateSendButton();

    //     fetch(chatMessageUrl, {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json",
    //             "X-CSRFToken": getCsrfToken(),
    //         },
    //         body: JSON.stringify({
    //             conversation_id: activeConversation,
    //             content: content.trim(),
    //         }),
    //     })
    //         .then((response) => (response.ok ? response.json() : Promise.reject(response)))
    //         .then((data) => {
    //             const exists = conversations.some((conversation) => conversation.id === data.conversation.id);
    //             if (!exists) {
    //                 conversations = [data.conversation, ...conversations];
    //             }

    //             activeConversation = data.conversation.id;
    //             chatTitleDisplay.innerText = data.conversation.title;
    //             messages = messages.filter((message) => message.id !== userMessage.id);
    //             data.messages.forEach((message) => {
    //                 messages.push({
    //                     ...message,
    //                     timestamp: new Date(message.timestamp),
    //                 });
    //             });
    //             const savedConversation = conversations.find(
    //                 (conversation) => conversation.id === data.conversation.id,
    //             );
    //             if (savedConversation) {
    //                 savedConversation.messages = messages.map((message) => ({
    //                     ...message,
    //                     timestamp: message.timestamp.toISOString(),
    //                 }));
    //             }
    //             renderMessages();
    //             renderConversations();
    //         })
    //         .catch(() => {
    //             messages.push({
    //                 id: Date.now().toString(),
    //                 role: "assistant",
    //                 content: "메시지를 저장하지 못했습니다. 잠시 후 다시 시도해주세요.",
    //                 timestamp: new Date(),
    //             });
    //             renderMessages();
    //         });
    // }

    function getCsrfToken() {
        const cookie = document.cookie.split("; ").find((row) => row.startsWith("csrftoken="));

        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    function updateSendButton() {
        const hasText = messageInput.value.trim().length > 0;
    }

    function startNewChat() {
        const newConversation = {
            id: Date.now().toString(),
            title: "새 채팅",
            group: "오늘",
        };

        conversations = [newConversation, ...conversations];
        activeConversation = newConversation.id;
        chatTitleDisplay.innerText = newConversation.title;
        messages = [
            {
                id: "1",
                role: "assistant",
                content: defaultAssistantMessage,
                timestamp: new Date(),
            },
        ];
        renderMessages();
        renderConversations();
        messageInput.value = "";
        updateSendButton();
        messageInput.focus();
    }

    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();
        sendMessage(messageInput.value);
    });

    messageInput.addEventListener("input", updateSendButton);
    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            chatForm.requestSubmit();
        }
    });

    conversationsList.addEventListener("click", (event) => {
        const deleteButton = event.target.closest("[data-delete-conversation-id]");
        if (deleteButton) {
            deleteConversation(deleteButton.dataset.deleteConversationId);
            return;
        }

        const conversationButton = event.target.closest("[data-conversation-id]");
        if (conversationButton) {
            setActiveConversation(conversationButton.dataset.conversationId);
        }
    });

    newChatBtn.addEventListener("click", startNewChat);

    initChat();
})();
