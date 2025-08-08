import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../services/api';
import './AdminDashboard.css';

interface Transaction {
  id: number;
  user_id: number;
  amount: number;
  currency_from: string;
  currency_to: string;
  exchange_rate: number;
  fee_amount: number;
  total_amount: number;
  status: string;
  created_at: string;
  user: {
    full_name: string;
    email: string;
  };
  recipient: {
    full_name: string;
    email: string;
  };
}

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [showTransactionModal, setShowTransactionModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [transactionsRes, usersRes] = await Promise.all([
        api.adminListTransactions(),
        api.getUsers()
      ]);
      setTransactions(transactionsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionAction = async (transactionId: number, action: 'approve' | 'reject') => {
    try {
      await api.adminUpdateTransaction(transactionId, { status: action === 'approve' ? 'completed' : 'failed' });
      fetchData();
      setShowTransactionModal(false);
    } catch (error) {
      console.error('Error updating transaction:', error);
    }
  };

  const [editStatus, setEditStatus] = useState('pending');
  const [editNotes, setEditNotes] = useState('');
  const [editProof, setEditProof] = useState('');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'pending': return 'orange';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const pendingTransactions = transactions.filter(t => t.status === 'pending');
  const completedTransactions = transactions.filter(t => t.status === 'completed');
  const totalVolume = transactions.reduce((sum, t) => sum + t.total_amount, 0);

  if (loading) {
    return (
      <div className="admin-dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div className="header-content">
          <div className="header-info">
            <h1>Admin Dashboard</h1>
            <p>Welcome back, {user?.full_name || 'Admin'}!</p>
          </div>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="admin-container">
        <nav className="admin-nav">
          <button
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`nav-tab ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            Transactions
          </button>
          <button
            className={`nav-tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </button>
          <button
            className={`nav-tab ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            Reports
          </button>
        </nav>

        <main className="admin-content">
          {activeTab === 'overview' && (
            <div className="overview-tab">
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Volume</h3>
                  <p className="stat-value">{formatCurrency(totalVolume, 'USD')}</p>
                  <p className="stat-change positive">+15.3% this month</p>
                </div>
                <div className="stat-card">
                  <h3>Pending Approvals</h3>
                  <p className="stat-value">{pendingTransactions.length}</p>
                  <p className="stat-change">Requires attention</p>
                </div>
                <div className="stat-card">
                  <h3>Active Users</h3>
                  <p className="stat-value">{users.filter(u => u.is_active).length}</p>
                  <p className="stat-change">Total: {users.length}</p>
                </div>
                <div className="stat-card">
                  <h3>Success Rate</h3>
                  <p className="stat-value">
                    {transactions.length > 0
                      ? Math.round((completedTransactions.length / transactions.length) * 100)
                      : 0}%
                  </p>
                  <p className="stat-change positive">High performance</p>
                </div>
              </div>

              <div className="quick-actions">
                <h2>Quick Actions</h2>
                <div className="action-buttons">
                  <button
                    className="action-btn primary"
                    onClick={() => setActiveTab('transactions')}
                  >
                    Review Pending
                  </button>
                  <button className="action-btn secondary">
                    Generate Report
                  </button>
                  <button className="action-btn secondary">
                    System Settings
                  </button>
                </div>
              </div>

              <div className="recent-activity">
                <h2>Recent Activity</h2>
                <div className="activity-list">
                  {transactions.slice(0, 5).map((transaction) => (
                    <div key={transaction.id} className="activity-item">
                      <div className="activity-info">
                        <h4>{transaction.user.full_name}</h4>
                        <p>Sent {formatCurrency(transaction.total_amount, transaction.currency_to)} to {transaction.recipient.full_name}</p>
                        <small>{formatDate(transaction.created_at)}</small>
                      </div>
                      <div className="activity-status">
                        <span className={`status ${getStatusColor(transaction.status)}`}>
                          {transaction.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'transactions' && (
            <div className="transactions-tab">
              <div className="transactions-header">
                <h2>Transaction Management</h2>
                <div className="filter-controls">
                  <select className="status-filter">
                    <option value="">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
              </div>

              <div className="transactions-table">
                <table>
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Recipient</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((transaction) => (
                      <tr key={transaction.id}>
                        <td>
                          <div className="user-info">
                            <strong>{transaction.user.full_name}</strong>
                            <small>{transaction.user.email}</small>
                          </div>
                        </td>
                        <td>
                          <div className="recipient-info">
                            <strong>{transaction.recipient.full_name}</strong>
                            <small>{transaction.recipient.email}</small>
                          </div>
                        </td>
                        <td>
                          <div className="amount-info">
                            <strong>{formatCurrency(transaction.total_amount, transaction.currency_to)}</strong>
                            <small>Fee: {formatCurrency(transaction.fee_amount, transaction.currency_from)}</small>
                          </div>
                        </td>
                        <td>
                          <span className={`status-badge ${getStatusColor(transaction.status)}`}>
                            {transaction.status}
                          </span>
                        </td>
                        <td>{formatDate(transaction.created_at)}</td>
                        <td>
                          {transaction.status === 'pending' && (
                            <div className="action-buttons-small">
                              <button
                                className="approve-btn"
                                onClick={() => {
                                  setSelectedTransaction(transaction);
                                  setShowTransactionModal(true);
                                }}
                              >
                                Review
                              </button>
                            </div>
                          )}
                          {transaction.status !== 'pending' && (
                            <button className="view-btn">View</button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="users-tab">
              <div className="users-header">
                <h2>User Management</h2>
                <button className="export-btn">Export Users</button>
              </div>

              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Status</th>
                      <th>Joined</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td>
                          <strong>{user.full_name}</strong>
                        </td>
                        <td>{user.email}</td>
                        <td>
                          <span className={`status-badge ${user.is_active ? 'green' : 'red'}`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>{formatDate(user.created_at)}</td>
                        <td>
                          <div className="action-buttons-small">
                            <button className="view-btn">View</button>
                            <button className="edit-btn">Edit</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="reports-tab">
              <h2>Reports & Analytics</h2>
              <div className="reports-grid">
                <div className="report-card">
                  <h3>Transaction Volume</h3>
                  <p>Monthly transaction volume analysis</p>
                  <button className="generate-btn">Generate Report</button>
                </div>
                <div className="report-card">
                  <h3>User Growth</h3>
                  <p>New user registration trends</p>
                  <button className="generate-btn">Generate Report</button>
                </div>
                <div className="report-card">
                  <h3>Success Rates</h3>
                  <p>Transaction success rate analysis</p>
                  <button className="generate-btn">Generate Report</button>
                </div>
                <div className="report-card">
                  <h3>Revenue Analysis</h3>
                  <p>Fee revenue and profitability</p>
                  <button className="generate-btn">Generate Report</button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {showTransactionModal && selectedTransaction && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Review Transaction</h2>
              <button
                className="close-btn"
                onClick={() => setShowTransactionModal(false)}
              >
                ×
              </button>
            </div>
            <div className="transaction-details">
              <div className="detail-row">
                <label>User:</label>
                <span>{selectedTransaction.user.full_name} ({selectedTransaction.user.email})</span>
              </div>
              <div className="detail-row">
                <label>Recipient:</label>
                <span>{selectedTransaction.recipient.full_name} ({selectedTransaction.recipient.email})</span>
              </div>
              <div className="detail-row">
                <label>Amount:</label>
                <span>{formatCurrency(selectedTransaction.total_amount, selectedTransaction.currency_to)}</span>
              </div>
              <div className="detail-row">
                <label>Date:</label>
                <span>{formatDate(selectedTransaction.created_at)}</span>
              </div>
            </div>
            <div className="editor">
              <div className="form-row">
                <label>Status</label>
                <select value={editStatus} onChange={e => setEditStatus(e.target.value)}>
                  <option value="pending">pending</option>
                  <option value="in_progress">in_progress</option>
                  <option value="completed">completed</option>
                  <option value="failed">failed</option>
                </select>
              </div>
              <div className="form-row">
                <label>Compliance Notes</label>
                <textarea value={editNotes} onChange={e => setEditNotes(e.target.value)} placeholder="Add internal notes"></textarea>
              </div>
              <div className="form-row">
                <label>Proof of Payment URL</label>
                <input value={editProof} onChange={e => setEditProof(e.target.value)} placeholder="https://..." />
              </div>
            </div>
            <div className="modal-actions">
              <button className="reject-btn" onClick={() => handleTransactionAction(selectedTransaction.id, 'reject')}>Reject</button>
              <button className="approve-btn" onClick={() => handleTransactionAction(selectedTransaction.id, 'approve')}>Approve</button>
              <button className="save-btn" onClick={async () => { await api.adminUpdateTransaction(selectedTransaction.id, { status: editStatus, compliance_notes: editNotes, proof_of_payment_url: editProof }); setShowTransactionModal(false); fetchData(); }}>Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
