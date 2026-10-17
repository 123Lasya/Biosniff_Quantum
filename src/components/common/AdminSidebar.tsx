import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Home,
  Users,
  Cpu,
  Sliders,
  LogOut,
} from 'lucide-react';
import { BioSniffLogo } from './BioSniffLogo';
import { useAuth } from '../../context/AuthContext';

export const AdminSidebar: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const navItems = [
    { name: 'Overview', to: '/admin/overview', icon: Home },
    { name: 'Farmers', to: '/admin/farmers', icon: Users },
    { name: 'Sensor Nodes', to: '/admin/sensors', icon: Cpu },
    { name: 'System Settings', to: '/admin/settings', icon: Sliders },
  ];


  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  return (
    <aside className="w-64 shrink-0 bg-[#0C2B1D] text-white flex flex-col justify-between border-r border-emerald-950/40 min-h-screen">
      <div>
        {/* Logo */}
        <div className="p-5 border-b border-emerald-900/40">
          <NavLink to="/admin/overview" className="block">
            <BioSniffLogo variant="light" size="md" />
          </NavLink>
        </div>

        {/* Navigation */}
        <nav className="p-3 space-y-0.5">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#184833] text-emerald-300 font-semibold shadow-inner'
                    : 'text-emerald-100/75 hover:bg-[#123927] hover:text-white'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <item.icon className="w-4 h-4 text-emerald-400" />
                <span>{item.name}</span>
              </div>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom Quote & Logout */}
      <div className="p-4 space-y-3">
        <div className="relative overflow-hidden rounded-xl border border-emerald-800/40 bg-gradient-to-b from-[#133F2B] to-[#0A2318] p-3 text-xs">
          <p className="font-handwritten text-lg text-emerald-200 leading-snug">
            “Healthy fields, brighter tomorrows.”
          </p>
          <div className="w-8 h-0.5 bg-emerald-500/50 mt-1 mb-2" />
          <p className="text-[10px] text-emerald-300/60 uppercase tracking-widest font-semibold">
            Farmers today. Healthier tomorrows.
          </p>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-2.5 w-full px-3 py-2 text-xs font-medium text-emerald-200/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4 text-emerald-400" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};
