import React, { useState, useEffect, useRef } from 'react';
import './ChatBox.css';

// Function to generate a GUID
function generateGuid(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

interface ChatMessage {
    id: string;
    userMessage: string;
    timestamp: string;
    response?: string;
}

const ChatBox: React.FC = () => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const chatHistoryRef = useRef<HTMLDivElement>(null);

    // Function to scroll to the bottom of the chat history
    const scrollToBottom = () => {
        if (chatHistoryRef.current) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    };

    // Scroll to bottom when chat history changes
    useEffect(() => {
        scrollToBottom();
    }, [chatHistory]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim() || isLoading) return;

        const newMessage: ChatMessage = {
            id: generateGuid(),
            userMessage: message,
            timestamp: new Date().toISOString(),
        };

        setChatHistory((prev) => [...prev, newMessage]);
        setMessage('');
        setIsLoading(true);
        setError(null);

        try {
            // Create an AbortController with a 180 second timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 180000); // 180 seconds timeout
            
            const response = await fetch(`${process.env.REACT_APP_API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: newMessage.id,
                    userMessage: newMessage.userMessage,
                    timestamp: newMessage.timestamp
                }),
                signal: controller.signal
            });
            
            // Clear the timeout since the request completed
            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 408) {
                    throw new Error('Request timed out. Please try again.');
                }
                throw new Error('Failed to send message');
            }

            const data = await response.json();
            setChatHistory((prev) =>
                prev.map((msg) =>
                    msg.id === newMessage.id
                        ? { ...msg, response: data.response }
                        : msg
                )
            );
        } catch (error) {
            if (error instanceof Error && error.name === 'AbortError') {
                setError('Request timed out after 180 seconds. Please try again.');
            } else {
                setError(error instanceof Error ? error.message : 'An error occurred');
            }
            // Remove the message from chat history if it failed
            setChatHistory((prev) => prev.filter(msg => msg.id !== newMessage.id));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-history" ref={chatHistoryRef}>
                {chatHistory.map((msg) => (
                    <div key={msg.id} className="chat-message">
                        <div className="user-message">
                            <strong>You:</strong> {msg.userMessage}
                        </div>
                        {msg.response && (
                            <div className="bot-message">
                                <strong>Emotika:</strong> {msg.response}
                            </div>
                        )}
                    </div>
                ))}
                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}
            </div>
            <form onSubmit={handleSubmit} className="chat-input-form">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                    disabled={isLoading}
                    className="chat-input"
                />
                <button 
                    type="submit" 
                    disabled={isLoading || !message.trim()} 
                    className="chat-submit"
                >
                    {isLoading ? 'Waiting for response...' : 'Send'}
                </button>
            </form>
        </div>
    );
};

export default ChatBox; 