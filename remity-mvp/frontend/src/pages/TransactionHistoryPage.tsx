import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/api';
// TODO: Import Transaction type/interface
// import { Transaction } from '../types';

// Placeholder type
interface Transaction {
  id: string;
  status: string;
  source_currency: string;
  target_currency: string;
  source_amount: number | string;
  target_amount: number | string;
  created_at: string;
  // Add other fields as needed
}

const TransactionHistoryPage: React.FC = () => {
  const { user, isLoading: isAuthLoading } = useAuth(); // Get user info and auth loading state
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      // Ensure user is loaded and authenticated before fetching
      if (!user) {
          console.log("User not available yet for fetching history.");
          // Optionally show a message or rely on ProtectedRoute handling
          return;
      }

      setIsLoading(true);
      setError(null);
      try {
        let response;
        // NOTE: Admin users currently see ALL transactions via the /admin/transactions endpoint.
        // This page uses the standard /transactions endpoint which shows ONLY the logged-in user's transactions.
        // If admins should see ALL transactions here too, the logic needs adjustment.
        response = await apiClient.get('/transactions/'); // Use user endpoint
        setTransactions(response.data);
      } catch (err) {
        console.error("Failed to fetch transaction history:", err);
        setError("Failed to load transaction history.");
      } finally {
        setIsLoading(false);
      }
    };

    // Fetch only if auth check is complete and user is available
    if (!isAuthLoading) {
        fetchHistory();
    }

  }, [user, isAuthLoading]); // Re-fetch if user or auth loading state changes

  // Handle the case where auth is still loading
  if (isAuthLoading) {
      return <div>Loading user data...</div>;
  }

  return (
    <div style={{ padding: '30px' }}>
      <h2>Transaction History</h2>

      {isLoading && <p>Loading history...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!isLoading && transactions.length === 0 && <p>No transactions found.</p>}

      {!isLoading && transactions.length > 0 && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>ID</th>
              <th style={tableHeaderStyle}>Date</th>
              <th style={tableHeaderStyle}>Status</th>
              <th style={tableHeaderStyle}>Send</th>
              <th style={tableHeaderStyle}>Receive</th>
              {/* Add more columns if needed */}
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr key={tx.id}>
                <td style={tableCellStyle}>{tx.id.substring(0, 8)}...</td>
                <td style={tableCellStyle}>{new Date(tx.created_at).toLocaleString()}</td>
                <td style={tableCellStyle}>{tx.status}</td>
                <td style={tableCellStyle}>{tx.source_amount} {tx.source_currency}</td>
                <td style={tableCellStyle}>{tx.target_amount} {tx.target_currency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

// Basic inline styles for table (move to CSS later)
const tableHeaderStyle: React.CSSProperties = { border: '1px solid #ccc', padding: '8px', textAlign: 'left', backgroundColor: '#f2f2f2' };
const tableCellStyle: React.CSSProperties = { border: '1px solid #ccc', padding: '8px' };


export default TransactionHistoryPage;
