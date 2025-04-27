import React, { useState, useEffect } from 'react';
import './ChatBox.css';

interface ChatMessage {
    id: string;
    userMessage: string;
    timestamp: string;
    response: string | null;
    status: 'Pending' | 'Processing' | 'Completed' | 'Failed';
    errorMessage?: string;
}

const ChatBox: React.FC = () => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const pollMessageStatus = async (messageId: string) => {
        try {
            const response = await fetch(`http://localhost:5000/chat/${messageId}`);
            if (!response.ok) return;
            
            const data: ChatMessage = await response.json();
            setChatHistory(prev => 
                prev.map(msg => msg.id === messageId ? data : msg)
            );

            // Continue polling if message is still processing
            if (data.status === 'Processing' || data.status === 'Pending') {
                setTimeout(() => pollMessageStatus(messageId), 1000);
            }
        } catch (error) {
            console.error('Error polling message status:', error);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(message),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data: ChatMessage = await response.json();
            setChatHistory(prev => [...prev, data]);
            setMessage('');
            
            // Start polling for status updates
            pollMessageStatus(data.id);
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getStatusIndicator = (status: ChatMessage['status']) => {
        switch (status) {
            case 'Pending':
                return '⏳';
            case 'Processing':
                return '🔄';
            case 'Completed':
                return '✅';
            case 'Failed':
                return '❌';
            default:
                return '';
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-history">
                {chatHistory.map((chat) => (
                    <div key={chat.id} className="chat-message">
                        <div className="message-header">
                            <span className="status-indicator">
                                {getStatusIndicator(chat.status)}
                            </span>
                            <span className="timestamp">
                                {new Date(chat.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                        <div className="user-message">
                            <strong>You:</strong> {chat.userMessage}
                        </div>
                        {chat.status === 'Failed' && (
                            <div className="error-message">
                                Error: {chat.errorMessage}
                            </div>
                        )}
                        {chat.response && (
                            <div className="bot-message">
                                <strong>Bot:</strong> {chat.response}
                            </div>
                        )}
                    </div>
                ))}
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
                <button type="submit" disabled={isLoading} className="chat-submit">
                    {isLoading ? 'Sending...' : 'Send'}
                </button>
            </form>
        </div>
    );
};

export default ChatBox; 