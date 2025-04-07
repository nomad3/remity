import React, { useState, useEffect } from 'react';
import './PendingTransactions.css';
// TODO: Import API service functions
// import { getPendingTransactions, approveTransaction, rejectTransaction } from '../../services/adminApi';
// TODO: Import Transaction type/interface (should match backend schema)
// import { Transaction } from '../../types';

// Placeholder type
interface Transaction {
  id: string;
  user_id: string;
  recipient_id: string;
  status: string;
  source_currency: string;
  target_currency: string;
  source_amount: number | string; // Use string if dealing with Decimal from backend
  target_amount: number | string;
  exchange_rate: number | string;
  created_at: string; // Use string for simplicity, format later
  // Add other relevant fields: reviewed_by_user_id, reviewed_at, failure_reason etc.
}

// Placeholder API functions
const getPendingTransactions = async (): Promise<Transaction[]> => {
  console.log("Fetching pending transactions...");
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  // Return mock data
  return [
    { id: 'uuid-1', user_id: 'user-a', recipient_id: 'rec-x', status: 'PENDING_APPROVAL', source_currency: 'USD', target_currency: 'MXN', source_amount: '1000.00', target_amount: '19500.00', exchange_rate: '19.50', created_at: new Date().toISOString() },
    { id: 'uuid-2', user_id: 'user-b', recipient_id: 'rec-y', status: 'PENDING_APPROVAL', source_currency: 'EUR', target_currency: 'PHP', source_amount: '500.00', target_amount: '29000.00', exchange_rate: '58.00', created_at: new Date().toISOString() },
  ];
};
const approveTransaction = async (id: string): Promise<Transaction> => {
    console.log(`Approving transaction ${id}...`);
    await new Promise(resolve => setTimeout(resolve, 300));
    // Find and update mock data (in real app, API returns updated object)
    const updatedTx = mockTransactions.find(tx => tx.id === id);
    if (updatedTx) updatedTx.status = 'PROCESSING'; // Simulate status change
    return updatedTx || {} as Transaction; // Return updated or empty
};
const rejectTransaction = async (id: string, reason: string): Promise<Transaction> => {
    console.log(`Rejecting transaction ${id} with reason: ${reason}...`);
    await new Promise(resolve => setTimeout(resolve, 300));
    const updatedTx = mockTransactions.find(tx => tx.id === id);
    if (updatedTx) updatedTx.status = 'MANUALLY_REJECTED'; // Simulate status change
    return updatedTx || {} as Transaction;
};
// Mock data store for placeholders
let mockTransactions: Transaction[] = [
    { id: 'uuid-1', user_id: 'user-a', recipient_id: 'rec-x', status: 'PENDING_APPROVAL', source_currency: 'USD', target_currency: 'MXN', source_amount: '1000.00', target_amount: '19500.00', exchange_rate: '19.50', created_at: new Date().toISOString() },
    { id: 'uuid-2', user_id: 'user-b', recipient_id: 'rec-y', status: 'PENDING_APPROVAL', source_currency: 'EUR', target_currency: 'PHP', source_amount: '500.00', target_amount: '29000.00', exchange_rate: '58.00', created_at: new Date().toISOString() },
];
// --- End Placeholder API ---


const PendingTransactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<{ [key: string]: string }>({}); // Store reason per transaction ID

  const fetchTransactions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getPendingTransactions();
      setTransactions(data);
      // Update mock data store if using placeholders
      mockTransactions = data;
    } catch (err) {
      console.error("Failed to fetch pending transactions:", err);
      setError("Failed to load transactions. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleApprove = async (id: string) => {
    // TODO: Add confirmation dialog
    setIsLoading(true); // Consider per-row loading state
    try {
      await approveTransaction(id);
      // Refresh list after action
      fetchTransactions();
    } catch (err) {
      console.error(`Failed to approve transaction ${id}:`, err);
      setError(`Failed to approve transaction ${id}.`);
      setIsLoading(false); // Reset global loading if needed
    }
  };

  const handleReject = async (id: string) => {
    const reason = rejectReason[id];
    if (!reason) {
        alert("Please provide a reason for rejection.");
        return;
    }
    // TODO: Add confirmation dialog
    setIsLoading(true);
    try {
      await rejectTransaction(id, reason);
      setRejectReason(prev => ({ ...prev, [id]: '' })); // Clear reason input
      fetchTransactions(); // Refresh list
    } catch (err) {
      console.error(`Failed to reject transaction ${id}:`, err);
      setError(`Failed to reject transaction ${id}.`);
      setIsLoading(false);
    }
  };

  const handleReasonChange = (id: string, value: string) => {
    setRejectReason(prev => ({ ...prev, [id]: value }));
  };


  return (
    <div className="admin-page pending-transactions">
      <h2>Pending Transaction Approval</h2>

      {isLoading && <p>Loading transactions...</p>}
      {error && <p className="error-message">{error}</p>}

      {!isLoading && transactions.length === 0 && <p>No transactions are currently pending approval.</p>}

      {!isLoading && transactions.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Created</th>
              <th>User ID</th>
              <th>Amount (Source)</th>
              <th>Amount (Target)</th>
              <th>Rate</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr key={tx.id}>
                <td>{tx.id.substring(0, 8)}...</td>
                <td>{new Date(tx.created_at).toLocaleString()}</td>
                <td>{tx.user_id.substring(0, 8)}...</td>
                <td>{tx.source_amount} {tx.source_currency}</td>
                <td>{tx.target_amount} {tx.target_currency}</td>
                <td>{tx.exchange_rate}</td>
                <td className="action-cell">
                  <button
                    className="btn btn-success btn-small"
                    onClick={() => handleApprove(tx.id)}
                    disabled={isLoading}
                  >
                    Approve
                  </button>
                  <div className="reject-group">
                    <input
                      type="text"
                      placeholder="Rejection Reason"
                      value={rejectReason[tx.id] || ''}
                      onChange={(e) => handleReasonChange(tx.id, e.target.value)}
                      disabled={isLoading}
                      className="reject-reason-input"
                    />
                    <button
                      className="btn btn-danger btn-small"
                      onClick={() => handleReject(tx.id)}
                      disabled={isLoading || !rejectReason[tx.id]}
                    >
                      Reject
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default PendingTransactions;
