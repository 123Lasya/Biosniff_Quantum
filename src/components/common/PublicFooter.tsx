import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { BioSniffLogo } from './BioSniffLogo';

export const PublicFooter: React.FC = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      setSubscribed(true);
      setEmail('');
    }
  };

  return (
    <footer className="bg-[#0A261B] text-white pt-16 pb-12 border-t border-emerald-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-16 border-b border-emerald-900/60">
          {/* Col 1: Brand info */}
          <div className="lg:col-span-2 space-y-4">
            <BioSniffLogo variant="light" size="lg" />
            <p className="text-emerald-200/80 text-sm max-w-sm leading-relaxed mt-4">
              Intelligent crop health monitoring for a more sustainable tomorrow. Powered by VOC biosensing and field-level localization.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noreferrer"
                className="w-9 h-9 rounded-full bg-emerald-900/60 hover:bg-emerald-700/60 flex items-center justify-center text-emerald-300 transition"
              >
                <span className="text-xs font-bold">in</span>
              </a>
              <a
                href="https://youtube.com"
                target="_blank"
                rel="noreferrer"
                className="w-9 h-9 rounded-full bg-emerald-900/60 hover:bg-emerald-700/60 flex items-center justify-center text-emerald-300 transition"
              >
                <span className="text-xs font-bold">YT</span>
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noreferrer"
                className="w-9 h-9 rounded-full bg-emerald-900/60 hover:bg-emerald-700/60 flex items-center justify-center text-emerald-300 transition"
              >
                <span className="text-xs font-bold">X</span>
              </a>
            </div>
          </div>

          {/* Col 2: Platform */}
          <div>
            <h4 className="text-sm font-semibold tracking-wider text-emerald-300 uppercase mb-4">
              Platform
            </h4>
            <ul className="space-y-2.5 text-sm text-emerald-100/70">
              <li><Link to="/farmer/overview" className="hover:text-white transition">Overview</Link></li>
              <li><Link to="/about" className="hover:text-white transition">Features</Link></li>
              <li><Link to="/impact" className="hover:text-white transition">Pricing</Link></li>
              <li><Link to="/about" className="hover:text-white transition">Case Studies</Link></li>
            </ul>
          </div>

          {/* Col 3: Company */}
          <div>
            <h4 className="text-sm font-semibold tracking-wider text-emerald-300 uppercase mb-4">
              Company
            </h4>
            <ul className="space-y-2.5 text-sm text-emerald-100/70">
              <li><Link to="/about" className="hover:text-white transition">About</Link></li>
              <li><Link to="/about" className="hover:text-white transition">Careers</Link></li>
              <li><Link to="/about" className="hover:text-white transition">News & Insights</Link></li>
              <li><Link to="/support" className="hover:text-white transition">Contact</Link></li>
            </ul>
          </div>

          {/* Col 4: Resources & Subscribe */}
          <div>
            <h4 className="text-sm font-semibold tracking-wider text-emerald-300 uppercase mb-4">
              Resources
            </h4>
            <ul className="space-y-2.5 text-sm text-emerald-100/70 mb-6">
              <li><Link to="/support" className="hover:text-white transition">Blogs</Link></li>
              <li><Link to="/about" className="hover:text-white transition">Research</Link></li>
              <li><Link to="/support" className="hover:text-white transition">Farmer Guides</Link></li>
              <li><Link to="/support" className="hover:text-white transition">Help Center</Link></li>
            </ul>

            <div className="space-y-2">
              <span className="text-xs font-semibold text-emerald-200 block">Subscribe to our updates</span>
              {subscribed ? (
                <div className="flex items-center gap-2 text-xs text-emerald-400 py-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Thank you for subscribing!</span>
                </div>
              ) : (
                <form onSubmit={handleSubscribe} className="flex items-center">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    required
                    className="w-full bg-white text-gray-900 px-3.5 py-2 text-xs rounded-l-lg focus:outline-hidden"
                  />
                  <button
                    type="submit"
                    className="bg-emerald-600 hover:bg-emerald-500 px-3 py-2 rounded-r-lg text-white transition flex items-center justify-center"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </form>
              )}
              <p className="text-[11px] text-emerald-300/60 leading-tight">
                Stay informed about our latest developments and stories from the field.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-emerald-300/60 gap-4">
          <p>© 2025 Bio-Sniff. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link to="/support" className="hover:text-emerald-200 transition">Privacy Policy</Link>
            <Link to="/support" className="hover:text-emerald-200 transition">Terms of Service</Link>
            <Link to="/support" className="hover:text-emerald-200 transition">Cookies</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
