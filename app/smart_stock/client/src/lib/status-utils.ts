import { 
  Package, AlertTriangle, XCircle, TrendingDown, CheckCircle, 
  Clock, Truck, Package2, Settings 
} from 'lucide-react';

export type StatusVariant = 'default' | 'secondary' | 'destructive' | 'outline';

export interface StatusStyle {
  variant: StatusVariant;
  className: string;
  icon: React.ComponentType<any>;
}

/**
 * Get intuitive color coding for inventory status
 */
export const getInventoryStatusStyle = (status: string): StatusStyle => {
  switch (status.toLowerCase()) {
    case 'in_stock':
      return {
        variant: 'secondary',
        className: 'bg-emerald-100 text-emerald-800 border-emerald-200 hover:bg-emerald-200',
        icon: Package
      };
    case 'low_stock':
      return {
        variant: 'secondary', 
        className: 'bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-200',
        icon: AlertTriangle
      };
    case 'out_of_stock':
      return {
        variant: 'destructive',
        className: 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200',
        icon: XCircle
      };
    case 'reorder_needed':
      return {
        variant: 'secondary',
        className: 'bg-orange-100 text-orange-800 border-orange-200 hover:bg-orange-200',
        icon: TrendingDown
      };
    case 'resolved':
      return {
        variant: 'secondary',
        className: 'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-200',
        icon: CheckCircle
      };
    default:
      return {
        variant: 'secondary',
        className: 'bg-slate-100 text-slate-800 border-slate-200 hover:bg-slate-200',
        icon: Package
      };
  }
};

/**
 * Get intuitive color coding for transaction/order status
 */
export const getTransactionStatusStyle = (status: string): StatusStyle => {
  switch (status.toLowerCase()) {
    case 'pending':
      return {
        variant: 'secondary',
        className: 'bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-200',
        icon: Clock
      };
    case 'approved':
      return {
        variant: 'secondary',
        className: 'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-200',
        icon: CheckCircle
      };
    case 'confirmed':
      return {
        variant: 'secondary',
        className: 'bg-emerald-100 text-emerald-800 border-emerald-200 hover:bg-emerald-200',
        icon: CheckCircle
      };
    case 'processing':
      return {
        variant: 'secondary',
        className: 'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-200',
        icon: Settings
      };
    case 'ordered':
      return {
        variant: 'secondary',
        className: 'bg-indigo-100 text-indigo-800 border-indigo-200 hover:bg-indigo-200',
        icon: Package2
      };
    case 'shipped':
      return {
        variant: 'secondary',
        className: 'bg-purple-100 text-purple-800 border-purple-200 hover:bg-purple-200',
        icon: Truck
      };
    case 'delivered':
      return {
        variant: 'secondary',
        className: 'bg-emerald-100 text-emerald-800 border-emerald-200 hover:bg-emerald-200',
        icon: Package
      };
    case 'received':
      return {
        variant: 'secondary',
        className: 'bg-green-100 text-green-800 border-green-200 hover:bg-green-200',
        icon: CheckCircle
      };
    case 'cancelled':
      return {
        variant: 'destructive',
        className: 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200',
        icon: XCircle
      };
    default:
      return {
        variant: 'secondary',
        className: 'bg-slate-100 text-slate-800 border-slate-200 hover:bg-slate-200',
        icon: Package
      };
  }
};

/**
 * Get formatted status text with proper capitalization
 */
export const formatStatusText = (status: string): string => {
  return status.replace(/_/g, ' ').toLowerCase().split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};
