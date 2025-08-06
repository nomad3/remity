import React from 'react';
import { Link } from 'react-router-dom';
import CalculatorSection from '../components/CalculatorSection';
import './LandingPage.css';

const LandingPage: React.FC = () => {
    return (
        <div className="landing-page">
            <header className="header">
                <div className="logo">Remity</div>
                <nav className="nav">
                    <Link to="/login" className="nav-link">Log in</Link>
                    <Link to="/register" className="nav-link-primary">Register</Link>
                </nav>
            </header>
            <main className="main-content">
                <div className="hero-section">
                    <div className="hero-text">
                        <h1 className="hero-title">The cheap, fast way to send money abroad.</h1>
                        <p className="hero-subtitle">Join over 10 million people who get the real exchange rate with Remity.</p>
                    </div>
                    <div className="hero-image">
                        <img src="/assets/hero-image.jpg" alt="Global Money Transfer Network" />
                    </div>
                </div>
            </main>
            <CalculatorSection />
            <section className="features-section">
                <div className="feature">
                    <div className="feature-icon">
                        <img src="/assets/dollar-sign-icon.svg" alt="Transparency" />
                    </div>
                    <h3>Radical transparency</h3>
                    <p>We're committed to showing you the full cost of your transfer upfront.</p>
                </div>
                <div className="feature">
                    <div className="feature-icon">
                        <img src="/assets/award-icon.svg" alt="Investors" />
                    </div>
                    <h3>Backed by the best</h3>
                    <p>We're backed by some of the world's leading investors.</p>
                </div>
                <div className="feature">
                    <div className="feature-icon">
                        <img src="/assets/shield-icon.svg" alt="Security" />
                    </div>
                    <h3>Bank-level security</h3>
                    <p>We use the same encryption and security standards as your bank.</p>
                </div>
            </section>
            <section className="testimonials">
                <h2 className="section-title">Join 10+ million people and businesses</h2>
                <div className="testimonial-cards">
                    <div className="testimonial-card">
                        <div className="testimonial-icon">
                            <img src="/assets/users-icon.svg" alt="Users" />
                        </div>
                        <p>"I've been using Remity for a few months now and I'm very impressed. The transfers are fast and the fees are very low."</p>
                        <h4>- Sarah, Freelancer</h4>
                    </div>
                    <div className="testimonial-card">
                        <div className="testimonial-icon">
                            <img src="/assets/check-circle-icon.svg" alt="Success" />
                        </div>
                        <p>"Remity is a game-changer. I can now send money to my family back home without having to worry about high fees."</p>
                        <h4>- John, Small Business Owner</h4>
                    </div>
                    <div className="testimonial-card">
                        <div className="testimonial-icon">
                            <img src="/assets/zap-icon.svg" alt="Fast" />
                        </div>
                        <p>"I love the transparency of Remity. I always know exactly how much I'm paying and how much my recipient will receive."</p>
                        <h4>- Jane, Student</h4>
                    </div>
                </div>
            </section>
            <section className="security-section">
                <h2 className="section-title">Your money is safe with us</h2>
                <div className="security-features">
                    <div className="security-feature">
                        <div className="security-icon">
                            <img src="/assets/shield-icon.svg" alt="Security" />
                        </div>
                        <h3>Bank-level security</h3>
                        <p>We use the same encryption and security standards as your bank.</p>
                    </div>
                    <div className="security-feature">
                        <div className="security-icon">
                            <img src="/assets/award-icon.svg" alt="Regulation" />
                        </div>
                        <h3>Regulated by the FCA</h3>
                        <p>We're regulated by the Financial Conduct Authority in the UK.</p>
                    </div>
                    <div className="security-feature">
                        <div className="security-icon">
                            <img src="/assets/lock-icon.svg" alt="Data Protection" />
                        </div>
                        <h3>Data protection</h3>
                        <p>We're committed to protecting your personal data.</p>
                    </div>
                </div>
            </section>
            <section className="how-it-works">
                <h2 className="section-title">How it works</h2>
                <div className="steps">
                    <div className="step">
                        <div className="step-icon">1</div>
                        <h3>Register in minutes</h3>
                        <p>Sign up online or in our app for free.</p>
                    </div>
                    <div className="step">
                        <div className="step-icon">2</div>
                        <h3>Set up your transfer</h3>
                        <p>Add the recipient's details and the amount you want to send.</p>
                    </div>
                    <div className="step">
                        <div className="step-icon">3</div>
                        <h3>Make your payment</h3>
                        <p>Pay for your transfer with a bank transfer, or a debit or credit card.</p>
                    </div>
                    <div className="step">
                        <div className="step-icon">4</div>
                        <h3>You're all done</h3>
                        <p>We'll handle the rest. You can track your transfer in your account.</p>
                    </div>
                </div>
            </section>
            <footer className="footer">
                <p>&copy; 2024 Remity. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default LandingPage;
