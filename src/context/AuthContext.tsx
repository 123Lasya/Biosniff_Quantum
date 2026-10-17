import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, LoginParams } from '../services/authService';
import { farmService } from '../services/farmService';
import { UserOut, TokenResponse, FarmOut } from '../types/api';

interface AuthContextType {
  user: UserOut | TokenResponse | null;
  role: 'farmer' | 'admin' | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  farmerId: number | null;
  primaryFarmId: number | null;
  farms: FarmOut[];
  login: (credentials: LoginParams) => Promise<TokenResponse>;
  logout: () => void;
  refreshSession: () => Promise<void>;
  setPrimaryFarmId: (id: number) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserOut | TokenResponse | null>(() => authService.getStoredUser());
  const [token, setTokenState] = useState<string | null>(() => localStorage.getItem('biosniff_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [farmerId, setFarmerId] = useState<number | null>(() => {
    const stored = authService.getStoredUser();
    return stored?.farmer_id || null;
  });
  const [primaryFarmId, setPrimaryFarmId] = useState<number | null>(() => {
    const savedId = localStorage.getItem('biosniff_farm_id');
    return savedId ? parseInt(savedId, 10) : null;
  });
  const [farms, setFarms] = useState<FarmOut[]>([]);

  const loadFarmerFarms = async (userFarmerId: number | null) => {
    try {
      const userFarms = await farmService.getFarms();
      setFarms(userFarms);
      if (userFarms.length > 0) {
        const defaultFarm = userFarms[0];
        setPrimaryFarmId(defaultFarm.farm_id);
        localStorage.setItem('biosniff_farm_id', defaultFarm.farm_id.toString());
      } else {
        // Fallback default farm ID 1
        setPrimaryFarmId(1);
        localStorage.setItem('biosniff_farm_id', '1');
      }
    } catch (err) {
      console.warn('Could not load farmer farms:', err);
      if (!primaryFarmId) {
        setPrimaryFarmId(1);
        localStorage.setItem('biosniff_farm_id', '1');
      }
    }
  };

  const refreshSession = async () => {
    const storedToken = localStorage.getItem('biosniff_token');
    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    try {
      const me = await authService.getMe();
      setUser(me);
      setTokenState(storedToken);
      setFarmerId(me.farmer_id);

      if (me.role === 'farmer') {
        await loadFarmerFarms(me.farmer_id);
      }
    } catch (err) {
      console.warn('Session check failed:', err);
      authService.logout();
      setUser(null);
      setTokenState(null);
      setFarmerId(null);
      setPrimaryFarmId(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshSession();
  }, []);

  const login = async (credentials: LoginParams): Promise<TokenResponse> => {
    setIsLoading(true);
    try {
      const tokenResp = await authService.login(credentials);
      setUser(tokenResp);
      setTokenState(tokenResp.access_token);
      setFarmerId(tokenResp.farmer_id);

      if (tokenResp.role === 'farmer') {
        await loadFarmerFarms(tokenResp.farmer_id);
      }
      return tokenResp;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setTokenState(null);
    setFarmerId(null);
    setPrimaryFarmId(null);
    setFarms([]);
    localStorage.removeItem('biosniff_farm_id');
  };

  const handleSetPrimaryFarmId = (id: number) => {
    setPrimaryFarmId(id);
    localStorage.setItem('biosniff_farm_id', id.toString());
  };

  const role = user?.role || null;
  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        token,
        isAuthenticated,
        isLoading,
        farmerId,
        primaryFarmId,
        farms,
        login,
        logout,
        refreshSession,
        setPrimaryFarmId: handleSetPrimaryFarmId,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
