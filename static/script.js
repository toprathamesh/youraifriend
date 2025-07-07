document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const messagesList = document.getElementById('messages-list');
    const inputForm = document.getElementById('input-form');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typing-indicator');
    const personalitySelector = document.getElementById('personality');
    
    // Memory Sidebar
    const memoryToggle = document.querySelector('.memory-toggle');
    const sidebar = document.querySelector('.sidebar');
    const closeSidebarBtn = document.getElementById('closeSidebar');
    const memoryList = document.querySelector('.memory-list');
    const addMemoryForm = document.querySelector('.add-memory-form');
    const addMemoryKeyInput = document.getElementById('add-memory-key');
    const addMemoryValueInput = document.getElementById('add-memory-value');
    
    // Edit Modal
    const editModal = document.getElementById('edit-modal');
    const editKeyInput = document.getElementById('edit-key-input');
    const editValueInput = document.getElementById('edit-value-input');
    const confirmEditBtn = document.getElementById('confirm-edit-btn');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');

    let currentEditKey = null;

    // --- Utility Functions ---
    const getCsrfToken = () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    const scrollToBottom = () => chatContainer.scrollTop = chatContainer.scrollHeight;

    const showTypingIndicator = (show) => {
        typingIndicator.classList.toggle('show', show);
        if (show) scrollToBottom();
    };

    const escapeHTML = (str) => {
        const p = document.createElement('p');
        p.appendChild(document.createTextNode(str));
        return p.innerHTML;
    };
    
    const formatTimestamp = (isoString) => {
        return new Date(isoString).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    };

    // --- Message Rendering ---
    const createMessageHTML = (sender, message, avatarInitial) => {
        const safeMessage = escapeHTML(message);
        const senderClass = sender === 'user' ? 'user-message' : 'assistant-message';
        const avatarClass = sender === 'user' ? 'user-avatar' : 'assistant-avatar';
        const avatarContent = sender === 'user' ? 'U' : 'AI';

        return `
            <div class="message-group ${senderClass}">
                <div class="message-bubble">
                    ${safeMessage.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    };

    const addMessageToList = (sender, message) => {
        const messageHTML = createMessageHTML(sender, message);
        messagesList.insertAdjacentHTML('beforeend', messageHTML);
        scrollToBottom();
    };

    // --- Chat History ---
    const loadChatHistory = async () => {
        try {
            const response = await fetch('/history');
            if (!response.ok) throw new Error('Failed to fetch history');
            const data = await response.json();
            
            messagesList.innerHTML = '';
            data.history.forEach(item => {
                if (item.user_message) addMessageToList('user', item.user_message);
                if (item.assistant_response) addMessageToList('assistant', item.assistant_response);
            });
            scrollToBottom();
        } catch (error) {
            console.error('Error loading chat history:', error);
            addMessageToList('assistant', 'Sorry, I couldn\'t load our past conversations.');
        }
    };
    
    // --- Memory Management ---
    const loadMemory = async () => {
        try {
            const response = await fetch('/memory');
            if (!response.ok) throw new Error('Failed to fetch memory');
            const data = await response.json();
            
            memoryList.innerHTML = '';
            Object.entries(data.memory).forEach(([key, value]) => {
                const memoryItemHTML = `
                    <div class="memory-item" data-key="${escapeHTML(key)}">
                        <div class="memory-item-content">
                            <div>
                                <div class="memory-key">${escapeHTML(key)}</div>
                                <div class="memory-value">${escapeHTML(value)}</div>
                            </div>
                            <div class="memory-actions">
                                <button class="edit-memory-btn" title="Edit">✏️</button>
                                <button class="delete-memory-btn" title="Delete">🗑️</button>
                            </div>
                        </div>
                    </div>
                `;
                memoryList.insertAdjacentHTML('beforeend', memoryItemHTML);
            });
        } catch (error) {
            console.error('Error loading memory:', error);
        }
    };
    
    const handleAddMemory = async (event) => {
        event.preventDefault();
        const key = addMemoryKeyInput.value.trim();
        const value = addMemoryValueInput.value.trim();

        if (!key || !value) {
            alert('Both key and value are required.');
            return;
        }

        try {
            const response = await fetch('/memory', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key, value }),
            });

            if (!response.ok) throw new Error('Failed to add memory');
            
            addMemoryKeyInput.value = '';
            addMemoryValueInput.value = '';
            await loadMemory();
        } catch (error) {
            console.error('Error adding memory:', error);
            alert('Failed to add memory. Please try again.');
        }
    };
    
    const handleMemoryAction = async (event) => {
        const target = event.target;
        const memoryItem = target.closest('.memory-item');
        if (!memoryItem) return;

        const key = memoryItem.dataset.key;

        if (target.classList.contains('delete-memory-btn')) {
            if (!confirm(`Are you sure you want to delete the memory item: "${key}"?`)) return;

            try {
                const response = await fetch('/memory', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key }),
                });

                if (!response.ok) throw new Error('Failed to delete memory');
                await loadMemory();
            } catch (error) {
                console.error('Error deleting memory:', error);
                alert('Failed to delete memory. Please try again.');
            }
        } else if (target.classList.contains('edit-memory-btn')) {
            const value = memoryItem.querySelector('.memory-value').textContent;
            currentEditKey = key;
            editKeyInput.value = key;
            editValueInput.value = value;
            editModal.style.display = 'block';
        }
    };

    const handleConfirmEdit = async () => {
        const newKey = editKeyInput.value.trim();
        const newValue = editValueInput.value.trim();

        if (!newKey || !newValue) {
            alert('Both key and value must be filled.');
            return;
        }

        try {
            const response = await fetch('/memory/edit', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_key: currentEditKey, new_key: newKey, new_value: newValue }),
            });
            
            if (!response.ok) {
                 const errorData = await response.json();
                 throw new Error(errorData.error || 'Failed to edit memory');
            }

            editModal.style.display = 'none';
            await loadMemory();
        } catch (error) {
            console.error('Error editing memory:', error);
            alert(`Failed to edit memory: ${error.message}`);
        }
    };
    
    // --- Main Chat Logic ---
    const handleFormSubmit = async (event) => {
        event.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        addMessageToList('user', message);
        userInput.value = '';
        userInput.style.height = '50px';
        sendButton.disabled = true;
        showTypingIndicator(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    personality: personalitySelector.value,
                }),
            });

            if (!response.ok) throw new Error('Server returned an error');
            const data = await response.json();
            
            addMessageToList('assistant', data.response);
            if(data.memory_updated) await loadMemory();

        } catch (error) {
            console.error('Error during chat:', error);
            addMessageToList('assistant', "Sorry, something went wrong. I can't talk right now.");
        } finally {
            showTypingIndicator(false);
            sendButton.disabled = false;
            userInput.focus();
        }
    };

    // --- Event Listeners ---
    inputForm.addEventListener('submit', handleFormSubmit);
    sendButton.addEventListener('click', handleFormSubmit);
    
    userInput.addEventListener('input', () => {
        sendButton.disabled = userInput.value.trim().length === 0;
        // Auto-resize textarea
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleFormSubmit(e);
        }
    });

    // Sidebar and Memory Listeners
    memoryToggle.addEventListener('click', () => {
        sidebar.classList.toggle('show');
        memoryToggle.classList.toggle('active');
        if (sidebar.classList.contains('show')) {
            loadMemory();
        }
    });

    closeSidebarBtn.addEventListener('click', () => {
        sidebar.classList.remove('show');
        memoryToggle.classList.remove('active');
    });

    addMemoryForm.addEventListener('submit', handleAddMemory);
    memoryList.addEventListener('click', handleMemoryAction);

    // Modal Listeners
    confirmEditBtn.addEventListener('click', handleConfirmEdit);
    cancelEditBtn.addEventListener('click', () => editModal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target == editModal) {
            editModal.style.display = 'none';
        }
    });

    // --- Initialization ---
    loadChatHistory();
    sendButton.disabled = true;
}); 