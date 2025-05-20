import React, { useState } from 'react';
import styled from 'styled-components';

const ChatContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
`;

const InputContainer = styled.div`
  border-top: 1px solid #eee;
  padding: 20px;
  background: white;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
`;

const InputForm = styled.form`
  display: flex;
  gap: 10px;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #FFE600;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  outline: none;
  
  &:focus {
    border-color: #FFE600;
    box-shadow: 0 0 0 2px rgba(255, 230, 0, 0.2);
  }
`;

const SendButton = styled.button`
  background: #FFE600;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #FFD700;
  }
`;

const Message = styled.div`
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 70%;
  ${props => props.isUser ? `
    background: #FFE600;
    margin-left: auto;
  ` : `
    background: #f0f0f0;
    margin-right: auto;
  `}
`;

const TypingIndicator = styled.div`
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 70%;
  background: #f0f0f0;
  margin-right: auto;
  display: flex;
  gap: 4px;
  align-items: center;

  span {
    width: 8px;
    height: 8px;
    background: #666;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out;

    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }

  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
  }
`;

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Make API call to your AI backend
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data = await response.json();
      
      // Add AI response
      setMessages(prev => [...prev, { text: data.response, isUser: false }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: error.message || "Sorry, I couldn't process your request at the moment.", 
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.map((message, index) => (
          <Message key={index} isUser={message.isUser}>
            {message.text}
          </Message>
        ))}
        {isLoading && (
          <TypingIndicator>
            <span></span>
            <span></span>
            <span></span>
          </TypingIndicator>
        )}
      </MessagesContainer>
      <InputContainer>
        <InputForm onSubmit={handleSubmit}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <SendButton type="submit" disabled={isLoading}>
            Send
          </SendButton>
        </InputForm>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface; 