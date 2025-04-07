import React from 'react';
import { render, screen } from '@testing-library/react';
import Header from './Header';

// Basic test to check if the component renders without crashing
test('renders Header component', () => {
  render(<Header />);

  // Check if the logo is present
  const logoElement = screen.getByText(/Remity.io/i);
  expect(logoElement).toBeInTheDocument();

  // Check if navigation links are present (example)
  const featuresLink = screen.getByText(/Features/i);
  expect(featuresLink).toBeInTheDocument();
  expect(featuresLink).toHaveAttribute('href', '#features');

  // Check if auth buttons are present (initial state: logged out)
  const loginButton = screen.getByRole('button', { name: /Log In/i });
  expect(loginButton).toBeInTheDocument();
  const signupButton = screen.getByRole('button', { name: /Sign Up/i });
  expect(signupButton).toBeInTheDocument();

  // Example: Test logged-in state (would require mocking context/state)
  // const isLoggedIn = true; // Simulate logged in
  // render(<Header />); // Re-render or pass props/context
  // const accountButton = screen.getByRole('button', { name: /My Account/i });
  // expect(accountButton).toBeInTheDocument();
  // expect(screen.queryByRole('button', { name: /Log In/i })).not.toBeInTheDocument();

});

// Add more tests for navigation clicks, auth state changes, etc.
