import React from 'react';
import './HeroSection.css';

const HeroSection: React.FC = () => {
  return (
    <section className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <h1>Send Money Smarter, Faster</h1>
          <p>
            Low fees, great exchange rates, and secure transfers to your loved ones.
            Get started in minutes.
          </p>
          {/* Link this button to the calculator or signup */}
          <button className="btn btn-primary btn-large">Send Money Now</button>
        </div>
        <div className="hero-image">
          {/* Placeholder for an illustration or image */}
          {/* Example using a simple placeholder */}
          <img src="https://via.placeholder.com/500x350/007bff/ffffff?text=Remity.io+Illustration" alt="Money Transfer Illustration" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
