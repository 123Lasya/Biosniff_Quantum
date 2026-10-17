import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { FarmerSidebar } from '../../components/common/FarmerSidebar';
import { Bell, ShieldCheck, ChevronDown, LogOut, ArrowLeft, User as UserIcon } from 'lucide-react';
import { authService } from '../../services/authService';

export const FarmerDashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [profileOpen, setProfileOpen] = React.useState(false);

  const currentUser = authService.getStoredUser();
  const userName = currentUser?.full_name || currentUser?.username || 'Farmer';
  const avatarUrl = currentUser?.profile_image_url;

  const handleLogout = () => {
    authService.logout();
    navigate('/signin');
  };

  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex font-sans">
      {/* Farmer Sidebar (Appears after Inspect Bio-Sniff) */}
      <FarmerSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Top bar inside the dashboard */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200/90 px-6 py-3 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link
                to="/farmer/overview"
                className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-emerald-800 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition"
                title="Back to Farm Overview Map"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Farm Map</span>
              </Link>
              <div className="h-4 w-px bg-gray-200" />
              <div className="text-xs text-gray-500 font-medium">
                Active Telemetry Account: <strong className="text-gray-900">{userName}</strong>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {currentUser?.role === 'admin' && (
                <Link
                  to="/admin/overview"
                  className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-900 text-emerald-100 text-xs font-medium hover:bg-emerald-800 transition"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Admin Console</span>
                </Link>
              )}

              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-gray-100 transition"
                >
                  {avatarUrl ? (
                    <img
                      src={avatarUrl}
                      alt={userName}
                      className="w-8 h-8 rounded-full object-cover border border-emerald-300"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-xs border border-emerald-300">
                      {userName.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div className="hidden sm:block text-left text-xs">
                    <span className="font-bold text-gray-900 block leading-tight">{userName}</span>
                    <span className="text-[10px] text-gray-500 leading-tight">Bio-Sniff Farmer</span>
                  </div>
                  <ChevronDown className="w-3 h-3 text-gray-400" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-xl border border-gray-200 bg-white py-1.5 shadow-xl z-50 text-xs">
                    <Link
                      to="/farmer/overview"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      Farmer Overview
                    </Link>
                    <Link
                      to="/farmer/system"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      System Telemetry
                    </Link>
                    {currentUser?.role === 'admin' && (
                      <Link
                        to="/admin/overview"
                        onClick={() => setProfileOpen(false)}
                        className="block px-3.5 py-2 text-emerald-700 font-semibold hover:bg-emerald-50"
                      >
                        Admin Network
                      </Link>
                    )}
                    <div className="border-t border-gray-100 my-1" />
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 w-full text-left px-3.5 py-2 text-red-600 hover:bg-red-50 font-semibold"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Log Out</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Nested Route Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
