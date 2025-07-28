import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  test('renders the health check component', () => {
    render(<App />);
    const linkElement = screen.getByText(/health check/i);
    expect(linkElement).toBeInTheDocument();
  });

  test('renders the main heading', () => {
    render(<App />);
    const headingElement = screen.getByRole('heading', { name: /welcome to the app/i });
    expect(headingElement).toBeInTheDocument();
  });
});