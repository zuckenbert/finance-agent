import React from 'react';
import styled from 'styled-components';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';

const AppContainer = styled.div`
  min-height: 100vh;
  background-color: #FFFFFF;
  font-family: 'Poppins', sans-serif;
`;

const MainContent = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

function App() {
  return (
    <AppContainer>
      <Header />
      <MainContent>
        <ChatInterface />
      </MainContent>
    </AppContainer>
  );
}

export default App; 