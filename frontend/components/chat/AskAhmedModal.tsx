'use client';

import { useState, useRef, useEffect } from 'react';
import { XMarkIcon, PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { fetchWithAuth } from '@/lib/auth-utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface AskAhmedModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AskAhmedModal({ isOpen, onClose }: AskAhmedModalProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I'm Ahmed, your AI assistant for the CALIDUS Requirements Management System. I can help you with:\n\n• Finding specific requirements or test cases\n• Analyzing traceability and coverage\n• Generating reports and statistics\n• Providing regulatory guidance (FAA, EASA, UAE GCAA)\n• Identifying gaps or risks\n\nWhat can I help you with today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage, isThinking]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setIsThinking(true);
    setCurrentStreamingMessage('');

    try {
      // Use fetchWithAuth which automatically handles token refresh on 401
      const response = await fetchWithAuth('http://localhost:8000/api/chat', {
        method: 'POST',
        body: JSON.stringify({
          messages: [...messages, userMessage]
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      if (reader) {
        while (true) {
          const { value, done } = await reader.read();

          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);

              try {
                const parsed = JSON.parse(data);

                if (parsed.type === 'content') {
                  // First content received, stop thinking indicator
                  setIsThinking(false);
                  accumulatedText += parsed.text;
                  setCurrentStreamingMessage(accumulatedText);
                } else if (parsed.type === 'done') {
                  // Finalize the message
                  setIsThinking(false);
                  setMessages(prev => [
                    ...prev,
                    { role: 'assistant', content: accumulatedText }
                  ]);
                  setCurrentStreamingMessage('');
                } else if (parsed.type === 'error') {
                  setIsThinking(false);
                  throw new Error(parsed.message);
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.';
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ Error: ${errorMessage}`
        }
      ]);
      setIsThinking(false);
    } finally {
      setIsLoading(false);
      setIsThinking(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed right-0 top-0 h-full w-full md:w-[500px] bg-white z-50 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white bg-opacity-20 rounded-lg">
              <SparklesIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Ask Ahmed</h2>
              <p className="text-sm text-blue-100">AI Requirements Assistant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            <XMarkIcon className="h-6 w-6 text-white" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary-500 text-white'
                    : 'bg-white text-gray-900 shadow-card border border-gray-100'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}

          {/* Thinking indicator */}
          {isThinking && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-2xl px-5 py-3 bg-white text-gray-900 shadow-card border border-gray-100">
                <div className="flex items-center space-x-3">
                  <div className="relative w-6 h-6">
                    {/* Spinning loader */}
                    <div className="absolute inset-0 border-2 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
                  </div>
                  <span className="text-sm text-gray-600 italic">Ahmed is thinking...</span>
                </div>
              </div>
            </div>
          )}

          {/* Streaming message */}
          {currentStreamingMessage && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-2xl px-5 py-3 bg-white text-gray-900 shadow-card border border-gray-100">
                <p className="text-sm whitespace-pre-wrap">{currentStreamingMessage}</p>
                <div className="flex space-x-1 mt-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="flex items-end space-x-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about requirements, tests, compliance..."
              rows={2}
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="p-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-card hover:shadow-card-hover"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </>
  );
}
