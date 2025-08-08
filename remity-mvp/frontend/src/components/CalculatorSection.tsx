import React, { useMemo, useState } from 'react';
import { createRecipient, createTransaction } from '../services/api';
import './CalculatorSection.css';

type Phase = 'calc' | 'recipient' | 'payment';

const CalculatorSection: React.FC = () => {
    const [amount, setAmount] = useState(1000);
    const [fromCurrency, setFromCurrency] = useState('USD');
    const [toCurrency, setToCurrency] = useState('EUR');
    const [phase, setPhase] = useState<Phase>('calc');
    const [recipient, setRecipient] = useState({
        full_name: '',
        email: '',
        bank_name: '',
        account_number: '',
        country: 'US',
    });
    const [paymentMethod, setPaymentMethod] = useState<'bank_transfer'>('bank_transfer');

    const exchangeRate = 0.92; // placeholder

    const fee = useMemo(() => Math.max(1, amount * 0.01), [amount]);
    const receiveAmount = useMemo(() => (amount - fee) * exchangeRate, [amount, fee]);

    const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = Number(e.target.value);
        setAmount(Number.isFinite(val) ? val : 0);
    };

    const goRecipient = () => {
        setPhase('recipient');
    };

    const goPayment = (e: React.FormEvent) => {
        e.preventDefault();
        setPhase('payment');
    };

    const submitTransfer = async () => {
        const draft = {
            amount,
            fromCurrency,
            toCurrency,
            exchangeRate,
            fee,
            paymentMethod,
            recipient,
        };
        const token = localStorage.getItem('token');
        if (!token) {
            localStorage.setItem('draftTransferFull', JSON.stringify(draft));
            window.location.href = '/register';
            return;
        }
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
                payment_method: paymentMethod,
            };
            await createTransaction(payload);
            alert('Transfer created! Track it in your dashboard.');
            window.location.href = '/dashboard';
        } catch (err) {
            console.error('Create transfer failed', err);
            alert('Failed to create transfer. Please try again.');
        }
    };

    return (
        <div className="calculator-section">
            <div className="calculator-card">
                {phase === 'calc' && (
                    <>
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
                            <button className="cta-button-primary" onClick={goRecipient}>Continue</button>
                            <button className="cta-button-secondary">Compare price</button>
                        </div>
                    </>
                )}

                {phase === 'recipient' && (
                    <div className="modal-content">
                        <h3>Add recipient</h3>
                        <form onSubmit={goPayment}>
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
                                <button type="submit" className="primary">Continue</button>
                                <button type="button" onClick={() => setPhase('calc')}>Back</button>
                            </div>
                        </form>
                    </div>
                )}

                {phase === 'payment' && (
                    <div className="modal-content">
                        <h3>Payment method</h3>
                        <div className="form-row">
                            <label>Method</label>
                            <select value={paymentMethod} onChange={e => setPaymentMethod(e.target.value as any)}>
                                <option value="bank_transfer">Bank transfer</option>
                            </select>
                        </div>
                        <div className="form-row">
                            <small>Amount: {amount.toFixed(2)} {fromCurrency} → You receive: {receiveAmount.toFixed(2)} {toCurrency}</small>
                        </div>
                        <div className="actions">
                            <button className="primary" onClick={submitTransfer}>Create transfer</button>
                            <button onClick={() => setPhase('recipient')}>Back</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CalculatorSection;
