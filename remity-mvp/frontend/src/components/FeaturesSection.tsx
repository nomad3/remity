import React from 'react';
import './FeaturesSection.css';

// Placeholder icons (replace with actual icons/images)
const FeatureIcon1 = () => <span>⚡</span>; // Fast
const FeatureIcon2 = () => <span>💲</span>; // Low Cost
const FeatureIcon3 = () => <span>🔒</span>; // Secure

const FeaturesSection: React.FC = () => {
  return (
    <section id="features" className="features-section">
      <div className="features-container">
        <h2>Why Choose Remity.io?</h2>
        <div className="features-grid">
          <div className="feature-item">
            <div className="feature-icon"><FeatureIcon1 /></div>
            <h3>Fast Transfers</h3>
            <p>Send money across borders quickly, often within minutes.</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon"><FeatureIcon2 /></div>
            <h3>Low, Transparent Fees</h3>
            <p>Know exactly what you pay with competitive rates and clear fees.</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon"><FeatureIcon3 /></div>
            <h3>Bank-Level Security</h3>
            <p>Your data and funds are protected with robust security measures.</p>
          </div>
          {/* Add more features as needed */}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
