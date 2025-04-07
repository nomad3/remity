import React, { useState } from 'react';
import './CalculatorSection.css';

const CalculatorSection: React.FC = () => {
  // Basic state for the calculator inputs
  const [sendAmount, setSendAmount] = useState<string>('1000');
  const [receiveAmount, setReceiveAmount] = useState<string>(''); // To be calculated
  const [sendCurrency, setSendCurrency] = useState<string>('USD');
  const [receiveCurrency, setReceiveCurrency] = useState<string>('MXN');

  // TODO: Implement actual API call to /quote endpoint
  // TODO: Handle loading state and error messages
  // TODO: Debounce API calls if user types quickly
  const handleCalculate = () => {
    console.log('Calculating:', { sendAmount, sendCurrency, receiveCurrency });
    // Placeholder calculation
    const rate = 19.85; // Fetch this from API
    const fee = 10; // Fetch this from API
    const calculatedReceive = (parseFloat(sendAmount) - fee) * rate;
    setReceiveAmount(calculatedReceive > 0 ? calculatedReceive.toFixed(2) : '0.00');
  };

  // Placeholder effect to calculate on initial load or currency change
  React.useEffect(() => {
    if (sendAmount) {
      handleCalculate();
    } else {
      setReceiveAmount('');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sendAmount, sendCurrency, receiveCurrency]); // Recalculate if inputs change


  return (
    <section id="calculator" className="calculator-section">
      <div className="calculator-container">
        <h2>Quick Calculator</h2>
        <div className="calculator-box">
          <div className="calculator-row">
            <div className="input-group">
              <label htmlFor="sendAmount">You send exactly</label>
              <input
                type="number"
                id="sendAmount"
                value={sendAmount}
                onChange={(e) => setSendAmount(e.target.value)}
                placeholder="1000"
              />
            </div>
            <div className="currency-select">
              <select value={sendCurrency} onChange={(e) => setSendCurrency(e.target.value)}>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                {/* Add more supported currencies */}
              </select>
            </div>
          </div>

          {/* Placeholder for Fee/Rate display */}
          <div className="calculator-details">
            <span>Fee: ~$10.00</span> {/* Placeholder */}
            <span>Rate: ~19.85</span> {/* Placeholder */}
          </div>

          <div className="calculator-row">
            <div className="input-group">
              <label htmlFor="receiveAmount">Recipient gets</label>
              <input
                type="text" // Display only, calculated value
                id="receiveAmount"
                value={receiveAmount}
                readOnly
                placeholder="Calculation..."
              />
            </div>
            <div className="currency-select">
              <select value={receiveCurrency} onChange={(e) => setReceiveCurrency(e.target.value)}>
                <option value="MXN">MXN</option>
                <option value="PHP">PHP</option>
                {/* Add more supported currencies */}
              </select>
            </div>
          </div>
          <button className="btn btn-primary btn-large btn-calculator">
            Get Started
          </button>
        </div>
      </div>
    </section>
  );
};

export default CalculatorSection;
