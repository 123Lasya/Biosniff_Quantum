import React from 'react';
import { NavLink, useNavigate, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  Wifi,
  Compass,
  Sliders,
  HelpCircle,
  LogOut,
  Headphones,
  ArrowRight,
} from 'lucide-react';
import { BioSniffLogo } from './BioSniffLogo';
import { useAuth } from '../../context/AuthContext';

interface FarmerSidebarProps {
  activeTab?: string;
  onSelectTab?: (tab: string) => void;
}

export const FarmerSidebar: React.FC<FarmerSidebarProps> = ({ activeTab }) => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const navItems = [
    { name: 'Overview', to: '/farmer/system', icon: LayoutDashboard },
    { name: 'Nodes', to: '/farmer/nodes', icon: Cpu },
    { name: '5G Connectivity', to: '/farmer/5g', icon: Wifi },
    { name: 'Environment', to: '/farmer/environment', icon: Compass },
    { name: 'Farm Configuration', to: '/farmer/config', icon: Sliders },
    { name: 'Support', to: '/support', icon: HelpCircle },
  ];

  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  return (
    <aside className="w-64 shrink-0 bg-[#0C2B1D] text-white flex flex-col justify-between border-r border-emerald-950/40 min-h-screen">
      <div>
        {/* Top Logo */}
        <div className="p-5 border-b border-emerald-900/40">
          <NavLink to="/farmer/overview" className="block">
            <BioSniffLogo variant="light" size="md" />
          </NavLink>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive || activeTab === item.name.toLowerCase()
                    ? 'bg-[#184833] text-emerald-300 font-semibold shadow-inner'
                    : 'text-emerald-100/70 hover:bg-[#123927] hover:text-white'
                }`
              }
            >
              <item.icon className="w-4 h-4 text-emerald-400" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom Help Card & Logout */}
      <div className="p-4 space-y-3">
        <div className="p-3.5 bg-[#0A261A] border border-emerald-900/80 rounded-2xl space-y-3 text-xs">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-emerald-800/60 border border-emerald-600/40 flex items-center justify-center text-emerald-300 shrink-0">
              <Headphones className="w-4 h-4 text-emerald-300" />
            </div>
            <div>
              <h4 className="font-bold text-white text-xs">Need Help?</h4>
              <p className="text-[11px] text-emerald-300/70 leading-tight">
                Our support team is always here for you.
              </p>
            </div>
          </div>
          <Link
            to="/support"
            className="flex items-center justify-between w-full px-3 py-2 bg-[#0E3524] hover:bg-[#144731] border border-emerald-700/50 rounded-xl text-emerald-200 text-xs font-medium transition"
          >
            <span>Contact Support</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
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
