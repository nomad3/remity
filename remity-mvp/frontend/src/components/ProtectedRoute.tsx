import React, { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
  adminOnly?: boolean; // Optional flag for admin-only routes
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, adminOnly = false }) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // Show a loading indicator while checking auth status
    return <div>Loading authentication status...</div>;
  }

  if (!isAuthenticated) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to. This allows us to send them along to that page after they login,
    // which is a nicer user experience than dropping them off on the home page.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (adminOnly && !user?.is_superuser) {
     // If route requires admin and user is not admin, redirect or show forbidden
     console.warn("Non-admin user tried to access admin route:", location.pathname);
     // Redirect to dashboard or show a 'Forbidden' component
     // For now, redirecting to home page as dashboard doesn't exist
     return <Navigate to="/" replace />; // Or show a 403 component
  }

  return <>{children}</>; // Render the child component if authenticated (and authorized if adminOnly)
};

export default ProtectedRoute;
