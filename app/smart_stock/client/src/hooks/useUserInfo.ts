import { useState, useEffect } from 'react';
import { apiClient } from '@/fastapi_client/client';
import type { UserInfo } from '@/fastapi_client';

interface UseUserInfoResult {
  userInfo: UserInfo | null;
  loading: boolean;
  error: string | null;
  displayName: string;
  role: string;
}

export const useUserInfo = (): UseUserInfoResult => {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getUserInfo();
        setUserInfo(data);
      } catch (err) {
        console.warn('Could not fetch user info:', err);
        setError('Failed to load user information');
        // Fallback to default values
        setUserInfo({
          userName: 'user@company.com',
          displayName: 'Elena Rodriguez',
          role: 'Senior Inventory Planner',
          active: true,
          emails: ['user@company.com']
        });
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  const displayName = userInfo?.displayName || 'Elena Rodriguez';
  const role = userInfo?.role || 'Senior Inventory Planner';

  return {
    userInfo,
    loading,
    error,
    displayName,
    role
  };
};
