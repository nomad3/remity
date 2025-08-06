import React, { useState } from 'react';
import './CalculatorSection.css';

const CalculatorSection: React.FC = () => {
    const [amount, setAmount] = useState(1000);
    const [fromCurrency, setFromCurrency] = useState('USD');
    const [toCurrency, setToCurrency] = useState('EUR');
    const exchangeRate = 0.92; // Example exchange rate

    const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setAmount(Number(e.target.value));
    };

    return (
        <div className="calculator-section">
            <div className="calculator-card">
                <div className="currency-input">
                    <input type="number" value={amount} onChange={handleAmountChange} />
                    <select value={fromCurrency} onChange={(e) => setFromCurrency(e.target.value)}>
                        <option value="USD">USD</option>
                        <option value="GBP">GBP</option>
                    </select>
                </div>
                <div className="rate-info">
                    <span>- 3.69 USD (fee)</span>
                    <span>x 0.92 (rate)</span>
                </div>
                <div className="currency-output">
                    <input type="number" value={(amount - 3.69) * exchangeRate} readOnly />
                    <select value={toCurrency} onChange={(e) => setToCurrency(e.target.value)}>
                        <option value="EUR">EUR</option>
                        <option value="NGN">NGN</option>
                    </select>
                </div>
                <button className="cta-button-primary">Compare price</button>
            </div>
        </div>
    );
};

export default CalculatorSection;
