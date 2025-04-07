import React from 'react';
import { Outlet, Link } from 'react-router-dom'; // Import Outlet and Link
import './AdminLayout.css'; // Add basic styling

// TODO: Implement proper layout, navigation, and content for admin panel
const AdminLayout: React.FC = () => {
  // TODO: Add check here to ensure user is an authenticated admin
  // If not, redirect to login or show an unauthorized message

  return (
    <div className="admin-layout">
      <nav className="admin-sidebar">
        <h2>Admin Menu</h2>
        <ul>
          <li><Link to="/admin/pending-transactions">Pending Approval</Link></li>
          <li><Link to="/admin/transactions">All Transactions</Link></li>
          <li><Link to="/admin/users">User Management</Link></li>
          {/* Add more admin links */}
        </ul>
      </nav>
      <main className="admin-content">
        {/* Outlet renders the matched nested route component */}
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
