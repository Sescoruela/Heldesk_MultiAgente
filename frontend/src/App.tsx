import React, { useState, useRef, useEffect } from 'react';
import './index.css';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

import { apiRequest } from './api/client';
import { ENDPOINTS } from './api/endpoints';

const App: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [apiKey, setApiKey] = useState(localStorage.getItem('GOOGLE_API_KEY') || '');
    const [loading, setLoading] = useState(false);
    const [sessionId] = useState(() => crypto.randomUUID());

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    useEffect(() => {
        localStorage.setItem('GOOGLE_API_KEY', apiKey);
    }, [apiKey]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;
        if (!apiKey) {
            alert('Por favor, introduce tu Google API Key en la barra lateral.');
            return;
        }

        const userMessage: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const data = await apiRequest(ENDPOINTS.CHAT, {
                method: 'POST',
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId,
                    api_key: apiKey
                }),
            });

            const assistantMessage: Message = { role: 'assistant', content: data.response };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error(error);
            const errorMessage: Message = {
                role: 'assistant',
                content: '❌ Lo siento, ha ocurrido un error al procesar tu solicitud.'
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-container">
            {/* Sidebar */}
            <aside className="sidebar">
                <h2>🛠️ Helpdesk</h2>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Sistema multi-agente potenciado por Google ADK y Gemini 2.0.
                </p>

                <div className="agent-list">
                    <div className="agent-card">
                        <h3>🔍 DiagnosticAgent</h3>
                        <p>Análisis de causa raíz</p>
                    </div>
                    <div className="agent-card">
                        <h3>🚦 TriageAgent</h3>
                        <p>Priorización y asignación</p>
                    </div>
                    <div className="agent-card">
                        <h3>📋 DocumentationAgent</h3>
                        <p>Tickets y postmortems</p>
                    </div>
                </div>

                <div className="api-key-input">
                    <label>Google API Key</label>
                    <input
                        type="password"
                        placeholder="AIza..."
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                    />
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="chat-area">
                <div className="messages">
                    {messages.length === 0 && (
                        <div style={{ marginTop: 'auto', marginBottom: 'auto', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <h3>¡Hola! Soy tu asistente de Helpdesk.</h3>
                            <p>Describe un incidente técnico para comenzar.</p>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div key={i} className={`message ${msg.role}`}>
                            {msg.content}
                        </div>
                    ))}

                    {loading && (
                        <div className="message assistant">
                            <div className="typing-indicator">
                                <div className="dot"></div>
                                <div className="dot"></div>
                                <div className="dot"></div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="input-area">
                    <div className="input-wrapper">
                        <input
                            type="text"
                            placeholder="Escribe tu mensaje aquí..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        />
                        <button
                            className="send-btn"
                            onClick={handleSend}
                            disabled={loading || !input.trim()}
                        >
                            Enviar
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default App;
