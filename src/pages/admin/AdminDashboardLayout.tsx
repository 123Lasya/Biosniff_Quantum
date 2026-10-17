import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { AdminSidebar } from '../../components/common/AdminSidebar';
import { Bell, ChevronDown, LogOut, ShieldCheck, User as UserIcon } from 'lucide-react';
import { authService } from '../../services/authService';

export const AdminDashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [profileOpen, setProfileOpen] = React.useState(false);

  const currentUser = authService.getStoredUser();
  const userName = currentUser?.full_name || currentUser?.username || 'Admin Console';
  const avatarUrl = currentUser?.profile_image_url;

  const handleLogout = () => {
    authService.logout();
    navigate('/signin');
  };

  return (
    <div className="min-h-screen bg-[#F4F7F5] text-gray-900 flex font-sans">
      {/* Admin Sidebar */}
      <AdminSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Admin Top Header */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200 px-6 py-3.5 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-xs font-bold text-[#0F3D2E] bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>BIO-SNIFF National Telemetry Console</span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Link
                to="/farmer/overview"
                className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-emerald-800 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition"
              >
                <span>Farmer App</span>
              </Link>

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
                    <div className="w-8 h-8 rounded-full bg-emerald-900 text-white font-bold flex items-center justify-center text-xs border border-emerald-700">
                      {userName.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div className="hidden sm:block text-left text-xs">
                    <span className="font-bold text-gray-900 block leading-tight">{userName}</span>
                    <span className="text-[10px] text-gray-500 leading-tight">System Super-Admin</span>
                  </div>
                  <ChevronDown className="w-3 h-3 text-gray-400" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-52 rounded-xl border border-gray-200 bg-white py-1.5 shadow-xl z-50 text-xs">
                    <div className="px-3.5 py-2 border-b border-gray-100">
                      <p className="font-bold text-gray-900">{userName}</p>
                      <p className="text-gray-500 text-[11px]">{currentUser?.email || 'admin@biosniff.gov.in'}</p>
                    </div>
                    <Link
                      to="/admin/overview"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      National Dashboard
                    </Link>
                    <Link
                      to="/admin/farmers"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      Farmers Directory
                    </Link>
                    <div className="border-t border-gray-100 my-1" />
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 w-full text-left px-3.5 py-2 text-red-600 hover:bg-red-50 font-semibold"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Log Out Admin</span>
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
