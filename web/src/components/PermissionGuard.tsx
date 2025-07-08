'use client';

import { useAuth } from '@/contexts/AuthContext';
import { hasPermission, type Permission } from '@/lib/permissions';
import { ReactNode } from 'react';

interface PermissionGuardProps {
  permission: Permission;
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Component that renders children only if the current user has the required permission
 */
export function PermissionGuard({ permission, children, fallback = null }: PermissionGuardProps) {
  const { user } = useAuth();
  
  if (!user || !hasPermission(user.role as any, permission)) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
}

interface MultiplePermissionGuardProps {
  permissions: Permission[];
  requireAll?: boolean; // true = require ALL permissions, false = require ANY permission
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Component that renders children based on multiple permissions
 */
export function MultiplePermissionGuard({ 
  permissions, 
  requireAll = false, 
  children, 
  fallback = null 
}: MultiplePermissionGuardProps) {
  const { user } = useAuth();
  
  if (!user) {
    return <>{fallback}</>;
  }
  
  const userRole = user.role as any;
  const hasAccess = requireAll 
    ? permissions.every(permission => hasPermission(userRole, permission))
    : permissions.some(permission => hasPermission(userRole, permission));
  
  if (!hasAccess) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
}
