import { Link } from 'react-router-dom';
import { Shield, CheckCircle2, Clock, FileText, ArrowRight, Zap } from 'lucide-react';
import { ScrollNavBar } from '@/components/ScrollNavBar';

export function HomePage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      <ScrollNavBar />
      {/* Hero */}
      <section style={{ 
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1.5rem',
        textAlign: 'center',
        backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.6)), url(https://images.unsplash.com/photo-1742134516852-f6b45d8189d7?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        position: 'relative'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            backgroundColor: 'rgba(240, 249, 255, 0.95)',
            borderRadius: '100px',
            marginBottom: '2rem',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#0070f3'
          }}>
            <Zap size={16} />
            Automated KYC verification
          </div>
          
          <h1 style={{ 
            fontSize: 'clamp(2.5rem, 5vw, 4.5rem)',
            fontWeight: '700',
            lineHeight: '1.1',
            letterSpacing: '-0.03em',
            marginBottom: '1.5rem',
            color: '#ffffff'
          }}>
            Verify customer identities in seconds
          </h1>
          
          <p style={{ 
            fontSize: '1.25rem',
            lineHeight: '1.6',
            color: 'rgba(255, 255, 255, 0.95)',
            marginBottom: '3rem',
            maxWidth: '680px',
            margin: '0 auto 3rem'
          }}>
            Instant KYC verification for Nigerian businesses. Check BVN, NIN, and CAC records with enterprise-grade accuracy.
          </p>
          
          <div style={{ 
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to="/dashboard" className="btn-primary" style={{ 
              fontSize: '1rem',
              padding: '1rem 2rem',
              gap: '0.5rem',
              display: 'inline-flex',
              alignItems: 'center',
              boxShadow: '0 4px 16px rgba(0, 112, 243, 0.4)'
            }}>
              Get Started
              <ArrowRight size={18} />
            </Link>
          </div>
          
          {/* Trust badges */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '2rem',
            marginTop: '4rem',
            fontSize: '0.875rem',
            color: 'rgba(255, 255, 255, 0.9)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle2 size={16} style={{ color: '#10b981' }} />
              <span>CBN Compliant</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle2 size={16} style={{ color: '#10b981' }} />
              <span>FATF Standards</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle2 size={16} style={{ color: '#10b981' }} />
              <span>30s Response Time</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ 
        padding: '6rem 1.5rem',
        backgroundColor: '#ffffff'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ 
              fontSize: '2.5rem',
              fontWeight: '700',
              marginBottom: '1rem',
              color: '#0a0a0a',
              letterSpacing: '-0.025em'
            }}>
              Everything you need for KYC compliance
            </h2>
            <p style={{ fontSize: '1.125rem', color: '#525252', maxWidth: '600px', margin: '0 auto' }}>
              Comprehensive verification tools built for Nigerian financial institutions
            </p>
          </div>
          
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem'
          }}>
            {[
              {
                icon: Shield,
                title: 'BVN & NIN Verification',
                description: 'Verify identity documents against NIMC and CBN databases with real-time validation and cross-referencing.'
              },
              {
                icon: FileText,
                title: 'CAC Verification',
                description: 'Check company registration, directors, shareholders, and ultimate beneficial ownership structure.'
              },
              {
                icon: CheckCircle2,
                title: 'Risk Assessment',
                description: 'Automated risk scoring based on CBN/FATF guidelines with PEP screening and adverse media checks.'
              },
              {
                icon: Clock,
                title: 'Instant Reports',
                description: 'Download detailed PDF reports with complete audit trails for regulatory compliance.'
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} style={{
                  padding: '2rem',
                  borderRadius: '12px',
                  border: '1px solid #eaeaea',
                  backgroundColor: '#fafbfc',
                  transition: 'all 0.2s ease'
                }} className="feature-card">
                  <div style={{
                    width: '48px',
                    height: '48px',
                    marginBottom: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #0070f3 0%, #00a8ff 100%)',
                    boxShadow: '0 4px 12px rgba(0, 112, 243, 0.2)'
                  }}>
                    <Icon size={24} strokeWidth={2} style={{ color: 'white' }} />
                  </div>
                  <h3 style={{ 
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    marginBottom: '0.75rem',
                    color: '#0a0a0a'
                  }}>
                    {feature.title}
                  </h3>
                  <p style={{ 
                    color: '#737373',
                    lineHeight: '1.6',
                    fontSize: '0.9375rem'
                  }}>
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{ 
        padding: '6rem 1.5rem',
        backgroundColor: '#fafbfc',
        borderTop: '1px solid #eaeaea'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ 
              fontSize: '2.5rem',
              fontWeight: '700',
              marginBottom: '1rem',
              color: '#0a0a0a',
              letterSpacing: '-0.025em'
            }}>
              Three steps to complete verification
            </h2>
            <p style={{ fontSize: '1.125rem', color: '#525252' }}>
              Fast, automated, and compliant
            </p>
          </div>
          
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '3rem',
            maxWidth: '1000px',
            margin: '0 auto'
          }}>
            {[
              {
                number: '01',
                title: 'Enter customer details',
                description: 'Input BVN, NIN, or RC number. Our system validates format and checks for common errors before processing.'
              },
              {
                number: '02',
                title: 'Automated verification',
                description: 'We query official databases, cross-reference information, and calculate risk scores in under 30 seconds.'
              },
              {
                number: '03',
                title: 'Download report',
                description: 'Get a comprehensive PDF report with verification status, risk assessment, and complete audit trail.'
              }
            ].map((step, index) => (
              <div key={index} style={{ position: 'relative' }}>
                <div style={{ 
                  fontSize: '4rem',
                  fontWeight: '700',
                  color: '#eaeaea',
                  marginBottom: '1rem',
                  lineHeight: '1',
                  letterSpacing: '-0.03em'
                }}>
                  {step.number}
                </div>
                <h3 style={{ 
                  fontSize: '1.25rem',
                  fontWeight: '600',
                  marginBottom: '0.875rem',
                  color: '#0a0a0a'
                }}>
                  {step.title}
                </h3>
                <p style={{ 
                  color: '#737373',
                  lineHeight: '1.6',
                  fontSize: '0.9375rem'
                }}>
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section style={{ 
        padding: '6rem 1.5rem',
        backgroundColor: '#ffffff',
        borderTop: '1px solid #eaeaea'
      }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ 
            fontSize: '2.5rem',
            fontWeight: '700',
            marginBottom: '1rem',
            color: '#0a0a0a',
            letterSpacing: '-0.025em'
          }}>
            Simple, transparent pricing
          </h2>
          <p style={{ fontSize: '1.125rem', color: '#525252', marginBottom: '3rem' }}>
            One flat rate for all verification types
          </p>
          
          <div style={{
            backgroundColor: '#fafbfc',
            border: '1px solid #eaeaea',
            borderRadius: '16px',
            padding: '3.5rem 2.5rem',
            maxWidth: '480px',
            margin: '0 auto',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)'
          }}>
            <div style={{ 
              fontSize: '5rem',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #0070f3 0%, #00a8ff 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: '0.5rem',
              lineHeight: '1',
              letterSpacing: '-0.03em'
            }}>
              ₦1,000
            </div>
            <p style={{ 
              color: '#737373',
              marginBottom: '2.5rem',
              fontSize: '1.125rem',
              fontWeight: '500'
            }}>
              per verification
            </p>
            
            <div style={{ 
              textAlign: 'left',
              marginBottom: '2rem',
              padding: '1.5rem',
              backgroundColor: 'white',
              borderRadius: '12px',
              border: '1px solid #eaeaea'
            }}>
              {['BVN & NIN verification', 'CAC company lookup', 'Risk assessment', 'PDF report generation', 'Complete audit trail'].map((feature, idx) => (
                <div key={idx} style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  marginBottom: idx < 4 ? '1rem' : '0',
                  fontSize: '0.9375rem',
                  color: '#3c4043'
                }}>
                  <CheckCircle2 size={18} style={{ color: '#10b981', flexShrink: 0 }} />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
            
            <Link to="/verify/individual" className="btn-primary" style={{ 
              width: '100%',
              fontSize: '1rem',
              padding: '1rem'
            }}>
              Start verifying
            </Link>
            
            <p style={{ 
              fontSize: '0.875rem',
              color: '#a3a3a3',
              marginTop: '1.5rem'
            }}>
              Test with mock data before going live
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ 
        padding: '8rem 1.5rem',
        background: 'linear-gradient(135deg, #0070f3 0%, #00a8ff 100%)',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h2 style={{ 
            fontSize: '2.75rem',
            fontWeight: '700',
            marginBottom: '1.5rem',
            color: 'white',
            letterSpacing: '-0.025em'
          }}>
            Start verifying customers today
          </h2>
          <p style={{ 
            fontSize: '1.25rem',
            color: 'rgba(255, 255, 255, 0.9)',
            marginBottom: '2.5rem',
            lineHeight: '1.6'
          }}>
            No credit card required. Test with our mock data before connecting to live APIs.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/verify/individual" style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: 'white',
              color: '#0070f3',
              padding: '1rem 2.5rem',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '1rem',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.2s ease'
            }}>
              Get started
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ 
        borderTop: '1px solid #eaeaea',
        backgroundColor: '#fafbfc',
        padding: '4rem 1.5rem 2rem'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '3rem',
            marginBottom: '3rem'
          }}>
            <div>
              <div style={{ 
                fontWeight: '700',
                fontSize: '1.25rem',
                marginBottom: '1rem',
                color: '#0a0a0a'
              }}>
                E-KYC Check
              </div>
              <p style={{ fontSize: '0.9375rem', color: '#737373', lineHeight: '1.6' }}>
                Automated KYC verification for Nigerian businesses
              </p>
            </div>
            
            <div>
              <div style={{ fontWeight: '600', marginBottom: '1rem', color: '#0a0a0a', fontSize: '0.875rem' }}>
                Product
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <Link to="/verify/individual" style={{ fontSize: '0.9375rem', color: '#737373' }}>
                  Individual Verification
                </Link>
                <Link to="/verify/corporate" style={{ fontSize: '0.9375rem', color: '#737373' }}>
                  Corporate Verification
                </Link>
              </div>
            </div>
            
            <div>
              <div style={{ fontWeight: '600', marginBottom: '1rem', color: '#0a0a0a', fontSize: '0.875rem' }}>
                Legal
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ fontSize: '0.9375rem', color: '#737373' }}>Privacy Policy</div>
                <div style={{ fontSize: '0.9375rem', color: '#737373' }}>Terms of Service</div>
              </div>
            </div>
          </div>
          
          <div style={{ 
            paddingTop: '2rem',
            borderTop: '1px solid #eaeaea',
            fontSize: '0.875rem',
            color: '#a3a3a3',
            textAlign: 'center'
          }}>
            © 2026 E-KYC Check. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
