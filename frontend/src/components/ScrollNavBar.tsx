import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export function ScrollNavBar() {
  const [isVisible, setIsVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        transform: isVisible ? 'translateY(0)' : 'translateY(-100%)',
        opacity: isVisible ? 1 : 0,
        transition: 'transform 0.3s ease, opacity 0.3s ease',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(234, 234, 234, 0.8)',
        padding: '1rem 2rem',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
      }}
    >
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Link
          to="/"
          style={{
            fontWeight: '700',
            fontSize: '1.25rem',
            color: '#0a0a0a',
            letterSpacing: '-0.02em',
            textDecoration: 'none'
          }}
        >
          E-KYC Check
        </Link>

        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <Link
            to="/dashboard"
            style={{
              fontSize: '0.9375rem',
              color: '#737373',
              textDecoration: 'none',
              fontWeight: '500',
              transition: 'color 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#0070f3'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#737373'}
          >
            Dashboard
          </Link>
          <Link
            to="/verify/individual"
            style={{
              fontSize: '0.9375rem',
              color: '#737373',
              textDecoration: 'none',
              fontWeight: '500',
              transition: 'color 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#0070f3'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#737373'}
          >
            Verify
          </Link>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
            style={{
              fontSize: '0.875rem',
              padding: '0.625rem 1.25rem'
            }}
          >
            Get Started
          </button>
        </div>
      </div>
    </nav>
  );
}
