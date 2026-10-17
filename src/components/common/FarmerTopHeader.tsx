import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bell, ChevronDown, LogOut } from 'lucide-react';
import { BioSniffLogo } from './BioSniffLogo';
import { useAuth } from '../../context/AuthContext';

interface FarmerTopHeaderProps {
  farmerName?: string;
  farmName?: string;
  onNotificationClick?: () => void;
}

export const FarmerTopHeader: React.FC<FarmerTopHeaderProps> = ({
  farmerName,
  farmName,
}) => {
  const navigate = useNavigate();
  const { user, logout, farms, primaryFarmId } = useAuth();
  const [menuOpen, setMenuOpen] = React.useState(false);

  const displayFarmerName = farmerName || (user as any)?.full_name || user?.username || 'Farmer';
  const currentFarm = farms.find((f) => f.farm_id === primaryFarmId);
  const displayFarmName = farmName || currentFarm?.farm_name || (farms.length > 0 ? farms[0].farm_name : 'Registered Farm');

  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  const profileImgUrl = (user as any)?.profile_image_url;
  const backendBase = (import.meta.env.VITE_API_BASE_URL as string)?.replace('/api', '') || 'http://localhost:8000';
  const avatarSrc = profileImgUrl
    ? (profileImgUrl.startsWith('http') ? profileImgUrl : `${backendBase}${profileImgUrl}`)
    : null;

  const initials = displayFarmerName
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'BS';

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200/90 px-6 py-3.5 shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-6">
          <Link to="/farmer/overview">
            <BioSniffLogo variant="dark" size="md" />
          </Link>

          {/* Farm indicator pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-medium text-emerald-900">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Farm: <strong>{displayFarmName}</strong></span>
          </div>
        </div>

        {/* Right tools & profile */}
        <div className="flex items-center gap-4">
          {/* Notification bell */}
          <button
            onClick={() => navigate('/farmer/overview')}
            className="relative p-2 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition"
            title="System Alerts"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full ring-2 ring-white" />
          </button>

          {/* User profile dropdown */}
          <div className="relative">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex items-center gap-3 p-1.5 rounded-xl hover:bg-gray-50 transition"
            >
              {avatarSrc ? (
                <img
                  src={avatarSrc}
                  alt="Farmer Avatar"
                  className="w-9 h-9 rounded-full object-cover border border-emerald-300 ring-2 ring-emerald-50"
                />
              ) : (
                <div className="w-9 h-9 rounded-full bg-emerald-800 text-white font-bold text-xs flex items-center justify-center border border-emerald-600 ring-2 ring-emerald-50 shadow-xs">
                  {initials}
                </div>
              )}
              <div className="hidden md:block text-left">
                <div className="text-xs font-bold text-gray-900 leading-tight">{displayFarmerName}</div>
                <div className="text-[11px] text-emerald-700 font-medium leading-tight">Farmer Account</div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
            </button>

            {menuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl border border-gray-200 bg-white py-1.5 shadow-xl z-50">
                <div className="px-3.5 py-2 border-b border-gray-100 text-xs">
                  <p className="font-bold text-gray-900">{displayFarmerName}</p>
                  <p className="text-gray-500 text-[11px] truncate">{user?.email || ''}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full text-left px-3.5 py-2 text-xs text-red-600 hover:bg-red-50"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
