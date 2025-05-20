import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background-color: #FFE600;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  color: #000;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
`;

const Header = () => {
  return (
    <HeaderContainer>
      <Title>Ierian</Title>
    </HeaderContainer>
  );
};

export default Header; 