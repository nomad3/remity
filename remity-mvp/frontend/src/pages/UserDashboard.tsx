import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../services/api';
import './UserDashboard.css';

interface Transaction {
  id: number;
  amount: number;
  currency_from: string;
  currency_to: string;
  exchange_rate: number;
  fee_amount: number;
  total_amount: number;
  status: string;
  created_at: string;
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
}

const UserDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showNewTransfer, setShowNewTransfer] = useState(false);
  const [transferForm, setTransferForm] = useState({
    amount: '',
    currency_from: 'USD',
    currency_to: 'EUR',
    recipient_name: '',
    recipient_email: '',
    recipient_bank: '',
    recipient_account: ''
  });

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const response = await api.getTransactions();
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTransferSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createTransaction(transferForm);
      setShowNewTransfer(false);
      setTransferForm({
        amount: '',
        currency_from: 'USD',
        currency_to: 'EUR',
        recipient_name: '',
        recipient_email: '',
        recipient_bank: '',
        recipient_account: ''
      });
      fetchTransactions();
    } catch (error) {
      console.error('Error creating transaction:', error);
    }
  };

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

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="user-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Welcome back, {user?.full_name || 'User'}!</h1>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-container">
        <nav className="dashboard-nav">
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
            className={`nav-tab ${activeTab === 'recipients' ? 'active' : ''}`}
            onClick={() => setActiveTab('recipients')}
          >
            Recipients
          </button>
          <button
            className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
        </nav>

        <main className="dashboard-content">
          {activeTab === 'overview' && (
            <div className="overview-tab">
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Sent</h3>
                  <p className="stat-value">$2,450.00</p>
                  <p className="stat-change positive">+12.5% this month</p>
                </div>
                <div className="stat-card">
                  <h3>Active Transfers</h3>
                  <p className="stat-value">{transactions.filter(t => t.status === 'pending').length}</p>
                  <p className="stat-change">Currently processing</p>
                </div>
                <div className="stat-card">
                  <h3>Saved Recipients</h3>
                  <p className="stat-value">8</p>
                  <p className="stat-change">Frequently used</p>
                </div>
                <div className="stat-card">
                  <h3>Exchange Rate</h3>
                  <p className="stat-value">1 USD = 0.85 EUR</p>
                  <p className="stat-change positive">+0.02% today</p>
                </div>
              </div>

              <div className="quick-actions">
                <h2>Quick Actions</h2>
                <div className="action-buttons">
                  <button
                    className="action-btn primary"
                    onClick={() => setShowNewTransfer(true)}
                  >
                    Send Money
                  </button>
                  <button className="action-btn secondary">
                    Add Recipient
                  </button>
                  <button className="action-btn secondary">
                    View Rates
                  </button>
                </div>
              </div>

              <div className="recent-transactions">
                <h2>Recent Transactions</h2>
                <div className="transactions-list">
                  {transactions.slice(0, 5).map((transaction) => (
                    <div key={transaction.id} className="transaction-item">
                      <div className="transaction-info">
                        <h4>{transaction.recipient.full_name}</h4>
                        <p>{formatDate(transaction.created_at)}</p>
                      </div>
                      <div className="transaction-amount">
                        <p className="amount">{formatCurrency(transaction.total_amount, transaction.currency_to)}</p>
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
                <h2>All Transactions</h2>
                <button
                  className="new-transfer-btn"
                  onClick={() => setShowNewTransfer(true)}
                >
                  New Transfer
                </button>
              </div>

              <div className="transactions-table">
                <table>
                  <thead>
                    <tr>
                      <th>Recipient</th>
                      <th>Amount</th>
                      <th>Exchange Rate</th>
                      <th>Status</th>
                      <th>Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((transaction) => (
                      <tr key={transaction.id}>
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
                        <td>{transaction.exchange_rate.toFixed(4)}</td>
                        <td>
                          <span className={`status-badge ${getStatusColor(transaction.status)}`}>
                            {transaction.status}
                          </span>
                        </td>
                        <td>{formatDate(transaction.created_at)}</td>
                        <td>
                          <button className="action-link">View</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'recipients' && (
            <div className="recipients-tab">
              <h2>Saved Recipients</h2>
              <p>Manage your frequently used recipients</p>
              {/* Recipients management will be implemented here */}
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="profile-tab">
              <h2>Profile Settings</h2>
              <div className="profile-form">
                <div className="form-group">
                  <label>Full Name</label>
                  <input type="text" defaultValue={user?.full_name} />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" defaultValue={user?.email} disabled />
                </div>
                <button className="save-btn">Save Changes</button>
              </div>
            </div>
          )}
        </main>
      </div>

      {showNewTransfer && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>New Transfer</h2>
              <button
                className="close-btn"
                onClick={() => setShowNewTransfer(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleTransferSubmit} className="transfer-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Amount</label>
                  <input
                    type="number"
                    value={transferForm.amount}
                    onChange={(e) => setTransferForm({...transferForm, amount: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>From Currency</label>
                  <select
                    value={transferForm.currency_from}
                    onChange={(e) => setTransferForm({...transferForm, currency_from: e.target.value})}
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>To Currency</label>
                  <select
                    value={transferForm.currency_to}
                    onChange={(e) => setTransferForm({...transferForm, currency_to: e.target.value})}
                  >
                    <option value="EUR">EUR</option>
                    <option value="USD">USD</option>
                    <option value="GBP">GBP</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Recipient Name</label>
                <input
                  type="text"
                  value={transferForm.recipient_name}
                  onChange={(e) => setTransferForm({...transferForm, recipient_name: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Recipient Email</label>
                <input
                  type="email"
                  value={transferForm.recipient_email}
                  onChange={(e) => setTransferForm({...transferForm, recipient_email: e.target.value})}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Bank Name</label>
                  <input
                    type="text"
                    value={transferForm.recipient_bank}
                    onChange={(e) => setTransferForm({...transferForm, recipient_bank: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Account Number</label>
                  <input
                    type="text"
                    value={transferForm.recipient_account}
                    onChange={(e) => setTransferForm({...transferForm, recipient_account: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => setShowNewTransfer(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary">
                  Send Transfer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDashboard;
