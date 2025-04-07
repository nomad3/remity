import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-section">
          <h4>Remity.io</h4>
          <p>Fast, secure, and affordable international money transfers.</p>
        </div>
        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><a href="/about">About Us</a></li>
            <li><a href="/help">Help & Support</a></li>
            <li><a href="/careers">Careers</a></li>
            <li><a href="/blog">Blog</a></li>
          </ul>
        </div>
        <div className="footer-section">
          <h4>Legal</h4>
          <ul>
            <li><a href="/terms">Terms of Service</a></li>
            <li><a href="/privacy">Privacy Policy</a></li>
            <li><a href="/licenses">Licenses</a></li>
          </ul>
        </div>
        <div className="footer-section">
          <h4>Follow Us</h4>
          {/* Add social media links/icons here */}
          <div className="social-links">
            {/* Replace # with actual or example URLs */}
            <a href="https://facebook.com/remityio" target="_blank" rel="noopener noreferrer">Facebook</a> | <a href="https://twitter.com/remityio" target="_blank" rel="noopener noreferrer">Twitter</a> | <a href="https://linkedin.com/company/remityio" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; {currentYear} Remity.io. All rights reserved.</p>
        {/* Add address or regulatory info if required */}
      </div>
    </footer>
  );
};

export default Footer;
