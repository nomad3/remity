import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import api from '../services/api'; // Assuming api service is set up
import './DashboardPage.css'; // We'll create this CSS file next
import { format } from 'date-fns'; // For formatting dates

// Define an interface for the transaction data expected from the API
interface Transaction {
    id: string;
    user_id: string; // Keep user_id if needed, especially for admin view
    recipient_id: string;
    status: string;
    source_currency: string;
    target_currency: string;
    source_amount: number; // Assuming API returns numbers (or use string if Decimal)
    target_amount: number;
    exchange_rate: number;
    remity_fee: number;
    payment_provider_fee: number;
    estimated_delivery_time?: string;
    onramp_payment_intent_id?: string;
    onramp_payment_status?: string;
    offramp_payout_reference?: string;
    offramp_payout_status?: string;
    failure_reason?: string;
    reviewed_by_user_id?: string;
    reviewed_at?: string;
    created_at: string; // Assuming ISO string format
    updated_at: string;
    // Add recipient details if the backend schema includes them, otherwise fetch separately if needed
    // recipient?: { name: string; country_code: string; ... }
}

const DashboardPage: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const authContext = useContext(AuthContext);

    // Check if user is admin (assuming user info is available in AuthContext)
    const isAdmin = authContext?.user?.is_superuser ?? false;
    const userEmail = authContext?.user?.email ?? 'User';

    useEffect(() => {
        const fetchTransactions = async () => {
            setIsLoading(true);
            setError(null);
            console.log("Fetching transactions..."); // Debug log
            try {
                // The backend endpoint now handles returning all vs. user-specific transactions
                const response = await api.get<Transaction[]>('/transactions/'); // Use GET request
                console.log("Transactions fetched:", response.data); // Debug log
                setTransactions(response.data);
            } catch (err: any) {
                console.error("Error fetching transactions:", err); // Debug log
                setError(err.response?.data?.detail || err.message || 'Failed to fetch transactions.');
            } finally {
                setIsLoading(false);
            }
        };

        // Fetch transactions only if logged in
        if (authContext?.isAuthenticated) {
            fetchTransactions();
        } else {
            setIsLoading(false); // Not logged in, stop loading
        }
    }, [authContext?.isAuthenticated]); // Re-fetch if auth state changes

    const formatCurrency = (amount: number, currency: string) => {
        // Basic currency formatting, consider using a library like Intl.NumberFormat for better localization
        return `${amount.toFixed(2)} ${currency}`;
    };

    const formatDate = (dateString: string) => {
        try {
            return format(new Date(dateString), 'PPpp'); // Format like: Sep 21, 2021, 4:30:56 PM
        } catch {
            return dateString; // Fallback if date is invalid
        }
    };

    if (!authContext?.isAuthenticated) {
        // Or redirect to login
        return <div className="dashboard-container"><p>Please log in to view your dashboard.</p></div>;
    }

    return (
        <div className="dashboard-container">
            <h2>Welcome, {userEmail}!</h2>
            <h3>{isAdmin ? 'All Transactions' : 'Your Transaction History'}</h3>

            {isLoading && <p>Loading transactions...</p>}
            {error && <p className="error-message">Error: {error}</p>}

            {!isLoading && !error && transactions.length === 0 && (
                <p>You have no transactions yet.</p>
            )}

            {!isLoading && !error && transactions.length > 0 && (
                <table className="transactions-table">
                    <thead>
                        <tr>
                            {isAdmin && <th>User ID</th>} {/* Show User ID only for admin */}
                            <th>ID</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Source</th>
                            <th>Target</th>
                            <th>Rate</th>
                            <th>Fees</th>
                            <th>Recipient ID</th>
                            {/* Add more columns as needed */}
                        </tr>
                    </thead>
                    <tbody>
                        {transactions.map((tx) => (
                            <tr key={tx.id}>
                                {isAdmin && <td>{tx.user_id.substring(0, 8)}...</td>} {/* Shorten UUID */}
                                <td>{tx.id.substring(0, 8)}...</td>
                                <td><span className={`status status-${tx.status.toLowerCase()}`}>{tx.status}</span></td>
                                <td>{formatDate(tx.created_at)}</td>
                                <td>{formatCurrency(tx.source_amount, tx.source_currency)}</td>
                                <td>{formatCurrency(tx.target_amount, tx.target_currency)}</td>
                                <td>{tx.exchange_rate.toFixed(4)}</td>
                                <td>{formatCurrency(tx.remity_fee + tx.payment_provider_fee, tx.source_currency)}</td>
                                <td>{tx.recipient_id.substring(0, 8)}...</td>
                                {/* Add more data cells */}
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default DashboardPage;
