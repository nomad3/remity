import React, { useMemo, useState } from 'react';
import { createRecipient, createTransaction } from '../services/api';
import './CalculatorSection.css';

const CalculatorSection: React.FC = () => {
    const [amount, setAmount] = useState(1000);
    const [fromCurrency, setFromCurrency] = useState('USD');
    const [toCurrency, setToCurrency] = useState('EUR');
    const [showRecipient, setShowRecipient] = useState(false);
    const [recipient, setRecipient] = useState({
        full_name: '',
        email: '',
        bank_name: '',
        account_number: '',
        country: 'US',
    });
    const exchangeRate = 0.92; // Example

    const fee = useMemo(() => Math.max(1, amount * 0.01), [amount]);
    const receiveAmount = useMemo(() => (amount - fee) * exchangeRate, [amount, fee]);

    const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setAmount(Number(e.target.value));
    };

    const startTransfer = () => {
        const token = localStorage.getItem('token');
        if (!token) {
            localStorage.setItem('draftTransfer', JSON.stringify({ amount, fromCurrency, toCurrency }));
            window.location.href = '/login';
            return;
        }
        setShowRecipient(true);
    };

    const submitTransfer = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const rcpt = await createRecipient(recipient);
            const payload = {
                recipient_id: rcpt.data.id,
                amount,
                currency_from: fromCurrency,
                currency_to: toCurrency,
                exchange_rate: exchangeRate,
                fee_amount: fee,
                total_amount: amount + fee,
                payment_method: 'bank_transfer',
            };
            await createTransaction(payload);
            setShowRecipient(false);
            alert('Transfer created! Track it in your dashboard.');
            window.location.href = '/dashboard';
        } catch (err) {
            console.error('Create transfer failed', err);
            alert('Failed to create transfer. Please check details or login again.');
        }
    };

    return (
        <div className="calculator-section">
            <div className="calculator-card">
                <div className="currency-input">
                    <input type="number" value={amount} onChange={handleAmountChange} />
                    <select value={fromCurrency} onChange={(e) => setFromCurrency(e.target.value)}>
                        <option value="USD">USD</option>
                        <option value="EUR">EUR</option>
                        <option value="GBP">GBP</option>
                    </select>
                </div>
                <div className="rate-info">
                    <span>- {fee.toFixed(2)} {fromCurrency} (fee)</span>
                    <span>x {exchangeRate} (rate)</span>
                </div>
                <div className="currency-output">
                    <input type="number" value={receiveAmount.toFixed(2)} readOnly />
                    <select value={toCurrency} onChange={(e) => setToCurrency(e.target.value)}>
                        <option value="EUR">EUR</option>
                        <option value="USD">USD</option>
                        <option value="NGN">NGN</option>
                    </select>
                </div>
                <div style={{display:'flex', gap:12}}>
                    <button className="cta-button-primary" onClick={startTransfer}>Send now</button>
                    <button className="cta-button-secondary">Compare price</button>
                </div>
            </div>

            {showRecipient && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>Add recipient</h3>
                        <form onSubmit={submitTransfer}>
                            <div className="form-row">
                                <label>Full name</label>
                                <input value={recipient.full_name} onChange={e => setRecipient({...recipient, full_name: e.target.value})} required />
                            </div>
                            <div className="form-row">
                                <label>Email</label>
                                <input type="email" value={recipient.email} onChange={e => setRecipient({...recipient, email: e.target.value})} />
                            </div>
                            <div className="form-row">
                                <label>Bank name</label>
                                <input value={recipient.bank_name} onChange={e => setRecipient({...recipient, bank_name: e.target.value})} />
                            </div>
                            <div className="form-row">
                                <label>Account number</label>
                                <input value={recipient.account_number} onChange={e => setRecipient({...recipient, account_number: e.target.value})} />
                            </div>
                            <div className="actions">
                                <button type="submit" className="primary">Create transfer</button>
                                <button type="button" onClick={() => setShowRecipient(false)}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CalculatorSection;
