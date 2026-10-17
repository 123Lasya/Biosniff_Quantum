import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { RefreshCw } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRole?: 'farmer' | 'admin';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRole,
}) => {
  const { isAuthenticated, isLoading, role } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F6F9F6] flex items-center justify-center">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-md text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Authenticating BIO-SNIFF Session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  if (allowedRole && role !== allowedRole) {
    // Role mismatch -> redirect to appropriate home
    if (role === 'farmer') {
      return <Navigate to="/farmer/overview" replace />;
    } else if (role === 'admin') {
      return <Navigate to="/admin/overview" replace />;
    } else {
      return <Navigate to="/signin" replace />;
    }
  }

  return <>{children}</>;
};
