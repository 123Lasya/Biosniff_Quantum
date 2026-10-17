import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Search, Menu, X } from 'lucide-react';
import { BioSniffLogo } from './BioSniffLogo';

export const PublicHeader: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const navLinks = [
    { name: 'Home', to: '/' },
    { name: 'Technology', to: '/about' },
    { name: 'Impact', to: '/impact' },
    { name: 'About', to: '/about' },
    { name: 'Resources', to: '/support' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center">
            <BioSniffLogo variant="dark" size="md" />
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <NavLink
                key={link.name}
                to={link.to}
                className={({ isActive }) =>
                  `text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-emerald-800 font-semibold'
                      : 'text-gray-600 hover:text-emerald-700'
                  }`
                }
              >
                {link.name}
              </NavLink>
            ))}
          </nav>

          {/* Right Action Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <button
              onClick={() => navigate('/support')}
              className="p-2 text-gray-500 hover:text-emerald-700 transition"
              title="Search"
            >
              <Search className="w-4 h-4" />
            </button>
            <Link
              to="/signin"
              className="text-sm font-semibold text-gray-700 hover:text-emerald-800 px-3 py-2 transition"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="text-sm font-semibold text-white bg-[#0F3D2E] hover:bg-[#14523E] px-5 py-2.5 rounded-xl shadow-xs transition-all"
            >
              Get Started
            </Link>
          </div>

          {/* Mobile hamburger */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-gray-600 hover:bg-gray-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-gray-200 bg-white px-4 pt-2 pb-6 space-y-3">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.to}
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-base font-medium text-gray-700 hover:text-emerald-700"
            >
              {link.name}
            </Link>
          ))}
          <div className="pt-4 border-t border-gray-100 flex flex-col gap-2">
            <Link
              to="/signin"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full text-center py-2.5 font-semibold text-gray-800 border border-gray-200 rounded-xl"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full text-center py-2.5 font-semibold text-white bg-[#0F3D2E] rounded-xl"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
