import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';

// Public Pages
import { LandingPage } from './pages/public/LandingPage';
import { SignInPage } from './pages/public/SignInPage';
import { SignUpPage } from './pages/public/SignUpPage';
import { AboutPage } from './pages/public/AboutPage';
import { ImpactPage } from './pages/public/ImpactPage';
import { SupportPage } from './pages/public/SupportPage';

// Farmer Pages
import { FarmerOverviewPage } from './pages/farmer/FarmerOverviewPage';
import { FarmerDashboardLayout } from './pages/farmer/FarmerDashboardLayout';
import { InspectBioSniffPage } from './pages/farmer/InspectBioSniffPage';
import { NodesPage } from './pages/farmer/NodesPage';
import { NodeDetailsPage } from './pages/farmer/NodeDetailsPage';
import { Connectivity5GPage } from './pages/farmer/Connectivity5GPage';
import { EnvironmentWindPage } from './pages/farmer/EnvironmentWindPage';
import { FarmConfigPage } from './pages/farmer/FarmConfigPage';

// Admin Pages
import { AdminDashboardLayout } from './pages/admin/AdminDashboardLayout';
import { AdminOverviewPage } from './pages/admin/AdminOverviewPage';
import { FarmersManagementPage } from './pages/admin/FarmersManagementPage';
import { FarmerProfilePage } from './pages/admin/FarmerProfilePage';
import { AdminNodesPage } from './pages/admin/AdminNodesPage';
import { AdminSettingsPage } from './pages/admin/AdminSettingsPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/impact" element={<ImpactPage />} />
          <Route path="/support" element={<SupportPage />} />

          {/* Farmer Entry Route: NO SIDEBAR (Strict requirement) */}
          <Route
            path="/farmer/overview"
            element={
              <ProtectedRoute allowedRole="farmer">
                <FarmerOverviewPage />
              </ProtectedRoute>
            }
          />

          {/* Farmer Dashboard Sub-Routes */}
          <Route
            path="/farmer"
            element={
              <ProtectedRoute allowedRole="farmer">
                <FarmerDashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/farmer/overview" replace />} />
            <Route path="system" element={<InspectBioSniffPage />} />
            <Route path="nodes" element={<NodesPage />} />
            <Route path="node/:id" element={<NodeDetailsPage />} />
            <Route path="connectivity" element={<Connectivity5GPage />} />
            <Route path="5g" element={<Connectivity5GPage />} />
            <Route path="environment" element={<EnvironmentWindPage />} />
            <Route path="config" element={<FarmConfigPage />} />
          </Route>

          {/* Admin Dashboard Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminDashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/overview" replace />} />
            <Route path="overview" element={<AdminOverviewPage />} />
            <Route path="farmers" element={<FarmersManagementPage />} />
            <Route path="farmer/:id" element={<FarmerProfilePage />} />
            <Route path="farms" element={<AdminOverviewPage />} />
            <Route path="analytics" element={<AdminOverviewPage />} />
            <Route path="sensors" element={<AdminNodesPage />} />
            <Route path="alerts" element={<AdminOverviewPage />} />
            <Route path="settings" element={<AdminSettingsPage />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}


