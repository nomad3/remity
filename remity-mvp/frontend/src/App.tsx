import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css'; // Basic styling
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import FeaturesSection from './components/FeaturesSection';
import CalculatorSection from './components/CalculatorSection';
import Footer from './components/Footer';
// Placeholder components for other pages
// Import pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import TransactionHistoryPage from './pages/TransactionHistoryPage'; // Import History Page
// import DashboardPage from './pages/DashboardPage'; // Placeholder
import AdminLayout from './pages/admin/AdminLayout';
import PendingTransactions from './pages/admin/PendingTransactions';
import ProtectedRoute from './components/ProtectedRoute'; // Import ProtectedRoute

// Simple component for the homepage content
const HomePage: React.FC = () => (
  <>
    <HeroSection />
    <CalculatorSection />
    <FeaturesSection />
    {/* Add other sections like Testimonials, How it Works, etc. */}
  </>
);

// Placeholder for other Admin sections
const AdminUsersPlaceholder: React.FC = () => <h2>Admin User Management</h2>;
const AdminAllTransactionsPlaceholder: React.FC = () => <h2>Admin All Transactions</h2>;


function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            {/* TODO: Add protected route for dashboard */}
            {/* <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} /> */}
            <Route path="/history" element={<ProtectedRoute><TransactionHistoryPage /></ProtectedRoute>} /> {/* Add History Route */}

            {/* Admin Panel Routes - Wrapped in ProtectedRoute */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute adminOnly={true}> {/* Ensure only admins access */}
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
                {/* Define nested routes relative to /admin */}
                <Route index element={<PendingTransactions />} /> {/* Default admin page */}
                <Route path="pending-transactions" element={<PendingTransactions />} />
                <Route path="users" element={<AdminUsersPlaceholder />} />
                <Route path="transactions" element={<AdminAllTransactionsPlaceholder />} />
                {/* Add more admin routes here */}
            </Route>

            {/* Add a 404 Not Found route */}
            <Route path="*" element={<h2>404: Page Not Found</h2>} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
