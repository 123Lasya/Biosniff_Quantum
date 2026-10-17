import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Lock, Mail, Shield, User, AlertCircle, RefreshCw } from 'lucide-react';
import { BioSniffLogo } from '../../components/common/BioSniffLogo';
import { useAuth } from '../../context/AuthContext';

export const SignInPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [role, setRole] = useState<'farmer' | 'admin'>('farmer');
  const [email, setEmail] = useState('ramesh.patil@biosniff.com');
  const [password, setPassword] = useState('Farmer@123456');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const res = await login({ username_or_email: email.trim(), password });
      if (res.role === 'admin') {
        navigate('/admin/overview');
      } else {
        navigate('/farmer/overview');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err?.message || 'Invalid username/email or password');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoLogin = async (demoRole: 'farmer' | 'admin') => {
    setError(null);
    const demoEmail =
      demoRole === 'farmer' ? 'ramesh.patil@biosniff.com' : 'admin@biosniff.gov.in';
    const demoPassword = demoRole === 'farmer' ? 'Farmer@123456' : 'Admin@123456';

    setRole(demoRole);
    setEmail(demoEmail);
    setPassword(demoPassword);
    setIsSubmitting(true);

    try {
      const res = await login({ username_or_email: demoEmail, password: demoPassword });
      if (res.role === 'admin') {
        navigate('/admin/overview');
      } else {
        navigate('/farmer/overview');
      }
    } catch (err: any) {
      console.error('Demo login error:', err);
      setError(err?.message || 'Demo account login failed. Please ensure the backend server and seed script are active.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F6F9F6] flex flex-col justify-center py-8">
      <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-emerald-950/10 grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
          {/* Left Hero Graphic Banner */}
          <div className="lg:col-span-5 bg-[#0C2B1D] text-white p-8 sm:p-12 flex flex-col justify-between relative overflow-hidden">
            <div className="absolute inset-0 bg-radial from-emerald-600/20 via-transparent to-transparent pointer-events-none" />
            <img
              src="https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=800&q=80"
              alt="Farmer in field"
              className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-30"
            />

            <div className="relative z-10">
              <Link to="/">
                <BioSniffLogo variant="light" size="lg" />
              </Link>
              <div className="mt-12 space-y-3">
                <span className="inline-block px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider">
                  Field-Level Intelligence
                </span>
                <h2 className="font-serif-display text-3xl sm:text-4xl font-bold text-white leading-tight">
                  The nose that never sleeps.
                </h2>
                <p className="text-sm text-emerald-200/80 leading-relaxed">
                  Real-time electronic odor monitoring safeguarding millions of acres against unseen fungal outbreaks.
                </p>
              </div>
            </div>

            <div className="relative z-10 pt-8">
              <p className="font-handwritten text-xl text-emerald-200 leading-snug">
                “Healthy fields, brighter tomorrows.”
              </p>
              <p className="text-[11px] text-emerald-300/60 uppercase tracking-widest mt-1">
                Maharashtra • Punjab • Uttar Pradesh
              </p>
            </div>
          </div>

          {/* Right Form Card */}
          <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-center">
            <div className="max-w-md mx-auto w-full space-y-6">
              <div>
                <h3 className="font-serif-display text-3xl font-bold text-[#0F2D1F]">
                  Welcome Back
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Enter your credentials to access real-time telemetry.
                </p>
              </div>

              {/* Role Toggle Tabs */}
              <div className="grid grid-cols-2 p-1 bg-gray-100 rounded-xl">
                <button
                  type="button"
                  onClick={() => {
                    setRole('farmer');
                    setEmail('ramesh.patil@biosniff.com');
                    setPassword('Farmer@123456');
                    setError(null);
                  }}
                  className={`flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-lg transition-all ${
                    role === 'farmer'
                      ? 'bg-white text-emerald-900 shadow-xs ring-1 ring-emerald-200'
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  <User className="w-4 h-4 text-emerald-600" />
                  <span>Farmer Account</span>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setRole('admin');
                    setEmail('admin@biosniff.gov.in');
                    setPassword('Admin@123456');
                    setError(null);
                  }}
                  className={`flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-lg transition-all ${
                    role === 'admin'
                      ? 'bg-white text-emerald-900 shadow-xs ring-1 ring-emerald-200'
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  <Shield className="w-4 h-4 text-emerald-600" />
                  <span>Administrator</span>
                </button>
              </div>

              {/* Error Alert */}
              {error && (
                <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs font-semibold text-red-700 flex items-center gap-2 animate-shake">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                  <span>{error}</span>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                    Email or Username
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                    <input
                      type="text"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="e.g. ramesh.patil@biosniff.com"
                      className="w-full pl-10 pr-4 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden transition font-medium"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                      Password
                    </label>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="••••••••••••"
                      className="w-full pl-10 pr-4 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden transition font-medium"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <label className="flex items-center gap-2 cursor-pointer text-xs text-gray-600">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                    />
                    <span>Keep me logged in</span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-3 px-4 bg-[#0F3D2E] hover:bg-[#14523E] disabled:bg-gray-400 text-white font-semibold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 text-sm mt-2"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Authenticating...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In as {role === 'farmer' ? 'Farmer' : 'Administrator'}</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {/* Direct Demo Access Buttons */}
              <div className="pt-4 border-t border-gray-100 space-y-2">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 block text-center">
                  Instant Seeded Account Access
                </span>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => handleDemoLogin('farmer')}
                    className="w-full text-center py-2 px-2 text-xs font-semibold bg-emerald-50 text-emerald-800 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition"
                  >
                    Farmer (Ramesh Patil)
                  </button>
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => handleDemoLogin('admin')}
                    className="w-full text-center py-2 px-2 text-xs font-semibold bg-gray-100 text-gray-800 hover:bg-gray-200 rounded-lg border border-gray-200 transition"
                  >
                    Admin (National Hub)
                  </button>
                </div>
              </div>

              <div className="text-center pt-2 text-xs text-gray-500">
                Don't have an account yet?{' '}
                <Link to="/signup" className="font-semibold text-emerald-700 hover:underline">
                  Sign Up Here
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
