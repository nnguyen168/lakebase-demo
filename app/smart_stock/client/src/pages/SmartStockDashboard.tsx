import React, { useEffect, useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DatePicker } from '@/components/ui/date-picker';
import { Label } from '@/components/ui/label';
import Pagination, { PaginationMeta } from '@/components/ui/pagination';
import {
  AlertTriangle, Package, TrendingUp, TrendingDown, Clock, Truck,
  CheckCircle, Factory, ArrowUp, ArrowDown, ArrowRight,
  Activity, ShoppingCart, Loader2, ArrowUpDown, ChevronUp, ChevronDown, ChevronsUpDown, RefreshCw, BarChart3, Filter, X
} from 'lucide-react';
import { apiClient } from '@/fastapi_client/client';
import { TransactionResponse, TransactionManagementKPI, InventoryForecastResponse, Product, Warehouse, TransactionStatus, TransactionType } from '@/fastapi_client';
import { TransactionManagement } from '@/components/TransactionManagement';
import ForecastModal from '@/components/ForecastModal';
import CreateOrderModal from '@/components/CreateOrderModal';
import OrderSuccessModal from '@/components/OrderSuccessModal';
import { useUserInfo } from '@/hooks/useUserInfo';
import { getTransactionStatusStyle, getInventoryStatusStyle, formatStatusText } from '@/lib/status-utils';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Checkbox } from '@/components/ui/checkbox';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

// Elena's KPIs
interface ElenaKPIs {
  onTimeProductionRate: number;
  onTimeProductionRatePrev: number;
  onTimeProductionChange: number;
  onTimeProductionTrend: string;
  inventoryTurnoverRatio: number;
  inventoryTurnoverPrev: number;
  inventoryTurnoverChange: number;
  inventoryTurnoverTrend: string;
  expeditedShipmentsCost: number;
  daysOfStockOnHand: number;
}

interface WarehouseData {
  name: string;
  location: string;
  transactionCount: number;
  inboundUnits: number;
  salesUnits: number;
  capacityUsed: number;
  lastAudit: string;
  activeProducts: number;
}

const SmartStockDashboard: React.FC = () => {
  const { displayName, role } = useUserInfo();
  const [activeTab, setActiveTab] = useState('transactions');
  const [kpis, setKpis] = useState<ElenaKPIs>({
    onTimeProductionRate: 94.5,
    onTimeProductionRatePrev: 92.3,
    onTimeProductionChange: 2.2,
    onTimeProductionTrend: '↑',
    inventoryTurnoverRatio: 8.2,
    inventoryTurnoverPrev: 7.8,
    inventoryTurnoverChange: 0.4,
    inventoryTurnoverTrend: '↑',
    expeditedShipmentsCost: 12500,
    daysOfStockOnHand: 18
  });
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [warehouses, setWarehouses] = useState<WarehouseData[]>([]);
  const [forecast, setForecast] = useState<InventoryForecastResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [kpisLoading, setKpisLoading] = useState(false);
  const [otprLoading, setOtprLoading] = useState(false);
  const [turnoverLoading, setTurnoverLoading] = useState(false);
  const [expeditedLoading, setExpeditedLoading] = useState(false);
  const [daysOfStockLoading, setDaysOfStockLoading] = useState(false);

  // Filter state
  const [products, setProducts] = useState<Product[]>([]);
  const [warehousesList, setWarehousesList] = useState<Warehouse[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [selectedWarehouses, setSelectedWarehouses] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);
  const [selectedTransactionTypes, setSelectedTransactionTypes] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState<Date | null>(null);
  const [dateTo, setDateTo] = useState<Date | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [shouldReloadAfterClear, setShouldReloadAfterClear] = useState(false);
  const [transactionKpi, setTransactionKpi] = useState<TransactionManagementKPI | null>(null);
  const [alertCounts, setAlertCounts] = useState({ critical: 0, warning: 0, total: 0 });

  // Transaction sort state
  type TransactionSortKey = 'product' | 'warehouse' | 'transaction_timestamp';
  const [transactionSort, setTransactionSort] = useState<{key: TransactionSortKey, order: 'asc' | 'desc'}>({
    key: 'transaction_timestamp',
    order: 'desc'
  });
  type ForecastSortKey = 'severity' | 'stock' | 'forecast' | 'product';
  interface ForecastSortState {
    key: ForecastSortKey;
    direction: 'asc' | 'desc';
  }
  const [forecastSort, setForecastSort] = useState<ForecastSortState>({ key: 'severity', direction: 'asc' });
  
  // Pagination state
  const [transactionsPagination, setTransactionsPagination] = useState<PaginationMeta>({
    total: 0,
    limit: 20,
    offset: 0,
    has_next: false,
    has_prev: false
  });
  const [forecastPagination, setForecastPagination] = useState<PaginationMeta>({
    total: 0,
    limit: 20,
    offset: 0,
    has_next: false,
    has_prev: false
  });
  const [forecastModalOpen, setForecastModalOpen] = useState(false);
  const [selectedForecastItem, setSelectedForecastItem] = useState<InventoryForecastResponse | null>(null);
  const [createOrderModalOpen, setCreateOrderModalOpen] = useState(false);
  const [selectedOrderItem, setSelectedOrderItem] = useState<InventoryForecastResponse | null>(null);
  const [orderSuccessModalOpen, setOrderSuccessModalOpen] = useState(false);
  const [successOrderData, setSuccessOrderData] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
    loadFilterOptions();
  }, []);

  useEffect(() => {
    // Reload forecast when sort changes
    loadForecast(forecastPagination.offset, forecastPagination.limit);
    loadAlertCounts();
  }, [forecastSort.key, forecastSort.direction]);

  useEffect(() => {
    // Reload transactions when sort changes
    loadTransactions(transactionsPagination.offset, transactionsPagination.limit);
  }, [transactionSort.key, transactionSort.order]);

  useEffect(() => {
    // Reload transactions after clearing filters
    if (shouldReloadAfterClear) {
      loadTransactions(0, transactionsPagination.limit);
      setShouldReloadAfterClear(false);
    }
  }, [shouldReloadAfterClear]);

  // Removed sortForecastItems since we use server-side sorting

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadTransactions(transactionsPagination.offset, transactionsPagination.limit),
        loadForecast(forecastPagination.offset, forecastPagination.limit),
        loadKpis(),
        loadAlertCounts()
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadFilterOptions = async () => {
    try {
      const [productsResponse, warehousesResponse] = await Promise.all([
        apiClient.getProducts(),
        apiClient.getWarehouses({ limit: 100, offset: 0 })
      ]);

      if (productsResponse) {
        setProducts(productsResponse.items || []);
      }
      if (warehousesResponse) {
        setWarehousesList(warehousesResponse.items || []);
      }
    } catch (error) {
      console.error('Error loading filter options:', error);
    }
  };

  const loadTransactions = async (offset: number = 0, limit: number = 20) => {
    try {
      setTransactionsLoading(true);

      // Load transactions with pagination, filters, and sorting
      const transactionsResponse = await apiClient.getTransactions(
        selectedStatuses.length > 0 ? selectedStatuses : undefined,
        selectedWarehouses.length > 0 ? selectedWarehouses.map(w => parseInt(w)) : undefined,
        selectedProducts.length > 0 ? selectedProducts.map(p => parseInt(p)) : undefined,
        selectedTransactionTypes.length > 0 ? selectedTransactionTypes : undefined,
        dateFrom ? dateFrom.toISOString() : undefined,
        dateTo ? dateTo.toISOString() : undefined,
        transactionSort.key,
        transactionSort.order,
        limit,
        offset
      );
      
      if (transactionsResponse) {
        const transactions = transactionsResponse.items;
        setTransactions(transactions);
        setTransactionsPagination(transactionsResponse.pagination);

        // Only process warehouse data on initial load or when loading first page
        if (offset === 0) {
          // Process warehouse data from transactions
          const warehouseMap = new Map<string, WarehouseData>();
          const productsByWarehouse = new Map<string, Set<string>>();

          transactions.forEach((t: TransactionResponse) => {
            if (!warehouseMap.has(t.warehouse)) {
              warehouseMap.set(t.warehouse, {
                name: t.warehouse,
                location: getWarehouseLocation(t.warehouse),
                transactionCount: 0,
                inboundUnits: 0,
                salesUnits: 0,
                capacityUsed: Math.floor(Math.random() * 35) + 45, // Simulated
                lastAudit: getLastAudit(t.warehouse),
                activeProducts: 0
              });
              productsByWarehouse.set(t.warehouse, new Set());
            }

            const wh = warehouseMap.get(t.warehouse)!;
            wh.transactionCount++;

            if (t.transaction_type === 'inbound') {
              wh.inboundUnits += Math.abs(t.quantity_change);
            } else if (t.transaction_type === 'sale') {
              wh.salesUnits += Math.abs(t.quantity_change);
            }

            productsByWarehouse.get(t.warehouse)!.add(t.product);
          });

          // Update active products count
          warehouseMap.forEach((wh, name) => {
            wh.activeProducts = productsByWarehouse.get(name)?.size || 0;
          });

          setWarehouses(Array.from(warehouseMap.values()));
        }
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setTransactionsLoading(false);
    }
  };

  const loadForecast = async (offset: number = 0, limit: number = 20) => {
    try {
      setForecastLoading(true);
      
      // Load forecast data with pagination and server-side sorting
      const forecastResponse = await apiClient.getInventoryForecast(
        undefined, // warehouseId
        undefined, // status
        limit,
        offset,
        forecastSort.key,
        forecastSort.direction
      );
      
      if (forecastResponse) {
        setForecast(forecastResponse.items);
        setForecastPagination(forecastResponse.pagination);
      }
    } catch (error) {
      console.error('Error loading forecast:', error);
    } finally {
      setForecastLoading(false);
    }
  };

  const loadKpis = async () => {
    console.log('loadKpis called - VERSION 2.0 WITH DB VIEWS - starting to load KPIs...');
    setKpisLoading(true);
    try {
      // Load KPIs
      const kpiResponse = await apiClient.getTransactionKpi();
      if (kpiResponse) {
        setTransactionKpi(kpiResponse);
      }

      // Load OTPR metrics from database view
      console.log('Fetching OTPR data...');
      try {
        const response = await fetch('/api/otpr/');
        console.log('OTPR response status:', response.status);
        if (response.ok) {
          const otprData = await response.json();
          console.log('OTPR Data from API:', otprData);
          setKpis(prev => {
            const newKpis = {
              ...prev,
              onTimeProductionRate: otprData.otpr_last_30d ?? 94.5,
              onTimeProductionRatePrev: otprData.otpr_prev_30d ?? 92.3,
              onTimeProductionChange: otprData.change_ppt ?? 2.2,
              onTimeProductionTrend: otprData.trend ?? '↑'
            };
            console.log('Updated KPIs after OTPR:', newKpis);
            return newKpis;
          });
        }
      } catch (otprError) {
        console.error('Error loading OTPR metrics:', otprError);
      }

      // Load Inventory Turnover metrics from database view
      console.log('Fetching Inventory Turnover data...');
      try {
        const response = await fetch('/api/inventory-turnover/');
        console.log('Inventory Turnover response status:', response.status);
        if (response.ok) {
          const turnoverData = await response.json();
          console.log('Inventory Turnover Data from API:', turnoverData);
          const currentTurnover = turnoverData.overall_inventory_turnover ?? 8.2;

          setKpis(prev => {
            const newKpis = {
              ...prev,
              inventoryTurnoverRatio: currentTurnover,
              inventoryTurnoverPrev: 0,
              inventoryTurnoverChange: 0,
              inventoryTurnoverTrend: '→',
              daysOfStockOnHand: turnoverData.overall_days_on_hand ?? 18
            };
            console.log('Updated KPIs after Inventory Turnover:', newKpis);
            return newKpis;
          });
        }
      } catch (turnoverError) {
        console.error('Error loading Inventory Turnover metrics:', turnoverError);
      }

      // Transaction KPI is already set above, no need to override anything here
    } catch (error) {
      console.error('Error loading KPIs:', error);
    } finally {
      setKpisLoading(false);
    }
  };

  const refreshOTPR = async () => {
    setOtprLoading(true);
    try {
      const response = await fetch('/api/otpr/');
      if (response.ok) {
        const otprData = await response.json();
        setKpis(prev => ({
          ...prev,
          onTimeProductionRate: otprData.otpr_last_30d ?? 94.5,
          onTimeProductionRatePrev: otprData.otpr_prev_30d ?? 92.3,
          onTimeProductionChange: otprData.change_ppt ?? 2.2,
          onTimeProductionTrend: otprData.trend ?? '↑'
        }));
      }
    } catch (error) {
      console.error('Error refreshing OTPR:', error);
    } finally {
      setOtprLoading(false);
    }
  };

  const refreshInventoryTurnover = async () => {
    setTurnoverLoading(true);
    try {
      const response = await fetch('/api/inventory-turnover/');
      if (response.ok) {
        const turnoverData = await response.json();
        const currentTurnover = turnoverData.overall_inventory_turnover ?? 8.2;
        setKpis(prev => ({
          ...prev,
          inventoryTurnoverRatio: currentTurnover,
          daysOfStockOnHand: turnoverData.overall_days_on_hand ?? 18
        }));
      }
    } catch (error) {
      console.error('Error refreshing Inventory Turnover:', error);
    } finally {
      setTurnoverLoading(false);
    }
  };

  const refreshExpeditedCosts = async () => {
    setExpeditedLoading(true);
    try {
      // Simulated refresh for expedited costs
      // In production, this would fetch from an actual endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Keep the same value for now
    } catch (error) {
      console.error('Error refreshing expedited costs:', error);
    } finally {
      setExpeditedLoading(false);
    }
  };

  const refreshDaysOfStock = async () => {
    setDaysOfStockLoading(true);
    try {
      const response = await fetch('/api/inventory-turnover/');
      if (response.ok) {
        const turnoverData = await response.json();
        setKpis(prev => ({
          ...prev,
          daysOfStockOnHand: turnoverData.overall_days_on_hand ?? 18
        }));
      }
    } catch (error) {
      console.error('Error refreshing days of stock:', error);
    } finally {
      setDaysOfStockLoading(false);
    }
  };

  const loadAlertCounts = async () => {
    try {
      let allItems: any[] = [];
      let offset = 0;
      const limit = 500; // Maximum allowed by API
      let hasMore = true;

      // Paginate through all items to get accurate counts with current sorting
      while (hasMore) {
        const response = await apiClient.getInventoryForecast(
          undefined, // warehouseId
          undefined, // status
          limit,
          offset,
          forecastSort.key,
          forecastSort.direction
        );
        
        if (response && response.items.length > 0) {
          allItems.push(...response.items);
          hasMore = response.pagination.has_next;
          offset += limit;
        } else {
          hasMore = false;
        }
      }
      
      // Count different types of alerts
      const critical = allItems.filter(f => f.status === 'out_of_stock' || f.status === 'reorder_needed').length;
      const warning = allItems.filter(f => f.status === 'low_stock').length;
      const total = allItems.length;
      
      setAlertCounts({ critical, warning, total });
    } catch (error) {
      console.error('Error loading alert counts:', error);
    }
  };

  const getWarehouseLocation = (name: string): string => {
    const locations: Record<string, string> = {
      'Lyon Main Warehouse': 'Zone Industrielle, 69007 Lyon, France',
      'Hamburg Distribution Center': 'Hafencity, 20457 Hamburg, Germany',
      'Milan Assembly Hub': 'Via Industriale, 20090 Segrate MI, Italy'
    };
    return locations[name] || 'Europe';
  };

  const getLastAudit = (warehouse: string): string => {
    if (warehouse.includes('Lyon')) return '2 days ago';
    if (warehouse.includes('Hamburg')) return '5 days ago';
    return '1 week ago';
  };

  const getStatusBadge = (status: string) => {
    const statusStyle = getTransactionStatusStyle(status);
    const StatusIcon = statusStyle.icon;

    return (
      <Badge 
        variant={statusStyle.variant} 
        className={`${statusStyle.className} flex items-center gap-1`}
      >
        <StatusIcon className="h-3 w-3" />
        {formatStatusText(status)}
      </Badge>
    );
  };

  const getTransactionIcon = (type: string) => {
    if (type === 'inbound') return <ArrowDown className="w-4 h-4 text-green-600" />;
    if (type === 'sale') return <ArrowUp className="w-4 h-4 text-red-600" />;
    return <Activity className="w-4 h-4 text-gray-600" />;
  };

  const getCriticalAlerts = () => {
    return alertCounts.critical;
  };

  const handleViewForecast = (item: InventoryForecastResponse) => {
    setSelectedForecastItem(item);
    setForecastModalOpen(true);
  };

  const closeForecastModal = () => {
    setForecastModalOpen(false);
    setSelectedForecastItem(null);
  };

  const handleCreateOrder = (item: InventoryForecastResponse) => {
    setSelectedOrderItem(item);
    setCreateOrderModalOpen(true);
  };

  const handleCreateOrderFromForecast = (item: InventoryForecastResponse) => {
    // Close forecast modal and open create order modal
    setForecastModalOpen(false);
    setSelectedForecastItem(null);
    handleCreateOrder(item);
  };

  const closeCreateOrderModal = () => {
    setCreateOrderModalOpen(false);
    setSelectedOrderItem(null);
  };

  const handleOrderCreated = () => {
    // Refresh dashboard data after order creation
    loadDashboardData();
  };

  const handleOrderSuccess = (orderData: any) => {
    // Show success modal with order data
    setSuccessOrderData(orderData);
    setOrderSuccessModalOpen(true);
    
    // Refresh all relevant data since order creation affects multiple views
    loadForecast(forecastPagination.offset, forecastPagination.limit);
    loadTransactions(transactionsPagination.offset, transactionsPagination.limit);
    loadAlertCounts();
  };

  // Pagination handlers
  const handleTransactionsPageChange = (offset: number, limit: number) => {
    loadTransactions(offset, limit);
  };

  const handleForecastPageChange = (offset: number, limit: number) => {
    loadForecast(offset, limit);
  };

  // Filter handlers
  const handleApplyFilters = () => {
    loadTransactions(0, transactionsPagination.limit);
  };

  const handleClearFilters = () => {
    setSelectedProducts([]);
    setSelectedWarehouses([]);
    setSelectedStatuses([]);
    setSelectedTransactionTypes([]);
    setDateFrom(null);
    setDateTo(null);
    // Trigger reload after state updates
    setShouldReloadAfterClear(true);
  };

  const hasActiveFilters = () => {
    return selectedProducts.length > 0 || selectedWarehouses.length > 0 || selectedStatuses.length > 0 ||
           selectedTransactionTypes.length > 0 || dateFrom || dateTo;
  };

  const handleTransactionSort = (key: TransactionSortKey) => {
    setTransactionSort(prev => ({
      key,
      order: prev.key === key && prev.order === 'desc' ? 'asc' : 'desc'
    }));
  };

  const handleForecastSort = (key: ForecastSortKey) => {
    setForecastSort((prev) => {
      if (prev.key === key) {
        return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      // Severity default to ascending (critical first), others descending
      const defaultDirection = key === 'severity' ? 'asc' : 'desc';
      return { key, direction: defaultDirection };
    });
  };

  const getSortIcon = (key: ForecastSortKey) => {
    if (forecastSort.key !== key) {
      return <ArrowUpDown className="h-3 w-3 ml-1 text-slate-400" />;
    }
    return forecastSort.direction === 'asc'
      ? <ChevronUp className="h-3 w-3 ml-1 text-blue-600" />
      : <ChevronDown className="h-3 w-3 ml-1 text-blue-600" />;
  };


  const closeOrderSuccessModal = () => {
    setOrderSuccessModalOpen(false);
    setSuccessOrderData(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Package className="w-12 h-12 mx-auto mb-4 animate-pulse" />
          <p>Loading inventory data...</p>
        </div>
      </div>
    );
  }

  const criticalAlerts = getCriticalAlerts();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Factory className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SmartStock</h1>
                <p className="text-sm text-gray-600">VulcanTech Manufacturing · Lyon, France</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="px-3 py-1">
                <Clock className="w-3 h-3 mr-1" />
                Last updated: {new Date().toLocaleTimeString()}
              </Badge>
              <div className="text-right">
                <p className="text-sm font-medium">{displayName}</p>
                <p className="text-xs text-gray-600">{role}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Critical Alerts Section */}
      {criticalAlerts > 0 && (
        <div className="container mx-auto px-4 py-4">
          <Alert className="bg-red-50 border-red-200">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertTitle className="text-red-900">Action Required</AlertTitle>
            <AlertDescription className="text-red-700">
              {criticalAlerts} components need immediate attention{alertCounts.warning > 0 && ` and ${alertCounts.warning} require monitoring`} - check the forecast tab for details
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* KPI Cards - Elena's Metrics */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className={`${
            kpis.onTimeProductionChange > 0 ? 'border-green-200 bg-green-50' :
            kpis.onTimeProductionChange < 0 ? 'border-red-200 bg-red-50' :
            'border-gray-200 bg-gray-50'
          }`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className={`text-sm font-medium ${
                  kpis.onTimeProductionChange > 0 ? 'text-green-900' :
                  kpis.onTimeProductionChange < 0 ? 'text-red-900' :
                  'text-gray-900'
                }`}>
                  On-Time Production Rate
                </CardTitle>
                <div className="flex items-center gap-1">
                  <button
                    onClick={refreshOTPR}
                    disabled={otprLoading}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="Refresh OTPR"
                  >
                    {otprLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
                    ) : (
                      <RefreshCw className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                    )}
                  </button>
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="View Analytics"
                  >
                    <BarChart3 className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <span className={`text-2xl font-bold ${
                    kpis.onTimeProductionChange > 0 ? 'text-green-700' :
                    kpis.onTimeProductionChange < 0 ? 'text-red-700' :
                    'text-gray-700'
                  }`}>
                    {kpisLoading ? (
                      <span className="inline-flex items-center">
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        Updating...
                      </span>
                    ) : (
                      `${kpis.onTimeProductionRate.toFixed(1)}%`
                    )}
                  </span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-sm font-medium flex items-center ${
                      kpis.onTimeProductionChange > 0 ? 'text-green-600' :
                      kpis.onTimeProductionChange < 0 ? 'text-red-600' :
                      'text-gray-600'
                    }`}>
                      <span className="mr-1">{kpis.onTimeProductionTrend}</span>
                      {kpis.onTimeProductionChange >= 0 ? '+' : ''}{kpis.onTimeProductionChange.toFixed(1)}%
                    </span>
                    <span className="text-xs text-gray-500">vs prev 30 days</span>
                  </div>
                </div>
                {kpis.onTimeProductionChange > 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : kpis.onTimeProductionChange < 0 ? (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                ) : (
                  <ArrowRight className="w-5 h-5 text-gray-600" />
                )}
              </div>
              <Progress
                value={kpis.onTimeProductionRate}
                className={`mt-2 ${
                  kpis.onTimeProductionChange > 0 ? '[&>div]:bg-green-600' :
                  kpis.onTimeProductionChange < 0 ? '[&>div]:bg-red-600' :
                  '[&>div]:bg-gray-600'
                }`}
              />
              <p className="text-xs text-gray-600 mt-2">
                Previous 30 days: {kpis.onTimeProductionRatePrev.toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card className="border-blue-200 bg-blue-50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-blue-900">
                  Inventory Turnover
                </CardTitle>
                <div className="flex items-center gap-1">
                  <button
                    onClick={refreshInventoryTurnover}
                    disabled={turnoverLoading}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="Refresh Inventory Turnover"
                  >
                    {turnoverLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
                    ) : (
                      <RefreshCw className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                    )}
                  </button>
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="View Analytics"
                  >
                    <BarChart3 className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-blue-700">
                  {kpis.inventoryTurnoverRatio}x
                </span>
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-xs text-blue-600 mt-1">Days on hand: {kpis.daysOfStockOnHand}</p>
            </CardContent>
          </Card>

          <Card className="border-orange-200 bg-orange-50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-orange-900">
                  Expedited Costs (MTD)
                </CardTitle>
                <div className="flex items-center gap-1">
                  <button
                    onClick={refreshExpeditedCosts}
                    disabled={expeditedLoading}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="Refresh Expedited Costs"
                  >
                    {expeditedLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
                    ) : (
                      <RefreshCw className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                    )}
                  </button>
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="View Analytics"
                  >
                    <BarChart3 className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-orange-700">
                  €{kpis.expeditedShipmentsCost.toLocaleString()}
                </span>
                <Truck className="w-5 h-5 text-orange-600" />
              </div>
              <p className="text-xs text-orange-600 mt-1">+23% vs last month</p>
            </CardContent>
          </Card>

          <Card className="border-purple-200 bg-purple-50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-purple-900">
                  Days of Stock
                </CardTitle>
                <div className="flex items-center gap-1">
                  <button
                    onClick={refreshDaysOfStock}
                    disabled={daysOfStockLoading}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="Refresh Days of Stock"
                  >
                    {daysOfStockLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
                    ) : (
                      <RefreshCw className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                    )}
                  </button>
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className="p-1 hover:bg-white/50 rounded transition-colors"
                    title="View Analytics"
                  >
                    <BarChart3 className="w-4 h-4 text-gray-600 hover:text-gray-800" />
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-purple-700">
                  {kpis.daysOfStockOnHand} days
                </span>
                <Clock className="w-5 h-5 text-purple-600" />
              </div>
              <p className="text-xs text-purple-600 mt-1">Target: 15-20 days</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="transactions">Inventory Transactions</TabsTrigger>
            <TabsTrigger value="analytics">Inventory Analytics</TabsTrigger>
            <TabsTrigger value="forecast">Inventory Forecast</TabsTrigger>
          </TabsList>

          {/* Inventory Transactions Tab */}
          <TabsContent value="transactions" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Inventory Transactions</CardTitle>
                    <CardDescription className="mt-1">
                      Real-time view of all inventory movements across warehouses
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowFilters(!showFilters)}
                      className="flex items-center gap-2"
                    >
                      <Filter className="h-4 w-4" />
                      {showFilters ? 'Hide Filters' : 'Show Filters'}
                      {hasActiveFilters() && (
                        <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                          {Object.values({
                            selectedProducts: selectedProducts.length,
                            selectedWarehouses: selectedWarehouses.length,
                            selectedStatuses: selectedStatuses.length,
                            selectedTransactionTypes: selectedTransactionTypes.length,
                            dateFrom,
                            dateTo
                          }).filter(Boolean).length}
                        </span>
                      )}
                    </Button>
                    <TransactionManagement onTransactionAdded={loadDashboardData} />
                  </div>
                </div>

                {/* Collapsible Filters Panel */}
                {showFilters && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                      {/* Product Filter */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Products</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="w-full justify-between h-9 px-3">
                              <span className="text-sm">
                                {selectedProducts.length === 0 ? 'All products' :
                                 selectedProducts.length === 1 ? products.find(p => p.product_id?.toString() === selectedProducts[0])?.name :
                                 `${selectedProducts.length} selected`}
                              </span>
                              <ChevronDown className="h-4 w-4 opacity-50" />
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80 p-0" align="start">
                            <div className="max-h-64 overflow-y-auto p-2">
                              {products.map((product) => (
                                product.product_id ? (
                                  <div key={product.product_id} className="flex items-center space-x-2 py-2 px-2 hover:bg-gray-100 rounded">
                                    <Checkbox
                                      id={`product-${product.product_id}`}
                                      checked={selectedProducts.includes(product.product_id.toString())}
                                      onCheckedChange={(checked) => {
                                        const productId = product.product_id!.toString();
                                        if (checked) {
                                          setSelectedProducts([...selectedProducts, productId]);
                                        } else {
                                          setSelectedProducts(selectedProducts.filter(p => p !== productId));
                                        }
                                      }}
                                    />
                                    <label
                                      htmlFor={`product-${product.product_id}`}
                                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                                    >
                                      {product.name || `Product ${product.product_id}`}
                                    </label>
                                  </div>
                                ) : null
                              ))}
                            </div>
                          </PopoverContent>
                        </Popover>
                      </div>

                      {/* Warehouse Filter */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Warehouses</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="w-full justify-between h-9 px-3">
                              <span className="text-sm">
                                {selectedWarehouses.length === 0 ? 'All warehouses' :
                                 selectedWarehouses.length === 1 ? warehousesList.find(w => w.warehouse_id?.toString() === selectedWarehouses[0])?.name :
                                 `${selectedWarehouses.length} selected`}
                              </span>
                              <ChevronDown className="h-4 w-4 opacity-50" />
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80 p-0" align="start">
                            <div className="max-h-64 overflow-y-auto p-2">
                              {warehousesList.map((warehouse) => (
                                warehouse.warehouse_id ? (
                                  <div key={warehouse.warehouse_id} className="flex items-center space-x-2 py-2 px-2 hover:bg-gray-100 rounded">
                                    <Checkbox
                                      id={`warehouse-${warehouse.warehouse_id}`}
                                      checked={selectedWarehouses.includes(warehouse.warehouse_id.toString())}
                                      onCheckedChange={(checked) => {
                                        const warehouseId = warehouse.warehouse_id!.toString();
                                        if (checked) {
                                          setSelectedWarehouses([...selectedWarehouses, warehouseId]);
                                        } else {
                                          setSelectedWarehouses(selectedWarehouses.filter(w => w !== warehouseId));
                                        }
                                      }}
                                    />
                                    <label
                                      htmlFor={`warehouse-${warehouse.warehouse_id}`}
                                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                                    >
                                      {warehouse.name || `Warehouse ${warehouse.warehouse_id}`}
                                    </label>
                                  </div>
                                ) : null
                              ))}
                            </div>
                          </PopoverContent>
                        </Popover>
                      </div>

                      {/* Status Filter */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Status</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="w-full justify-between h-9 px-3">
                              <span className="text-sm">
                                {selectedStatuses.length === 0 ? 'All statuses' :
                                 selectedStatuses.length === 1 ? selectedStatuses[0] :
                                 `${selectedStatuses.length} selected`}
                              </span>
                              <ChevronDown className="h-4 w-4 opacity-50" />
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80 p-0" align="start">
                            <div className="max-h-64 overflow-y-auto p-2">
                              {['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'].map((status) => (
                                <div key={status} className="flex items-center space-x-2 py-2 px-2 hover:bg-gray-100 rounded">
                                  <Checkbox
                                    id={`status-${status}`}
                                    checked={selectedStatuses.includes(status)}
                                    onCheckedChange={(checked) => {
                                      if (checked) {
                                        setSelectedStatuses([...selectedStatuses, status]);
                                      } else {
                                        setSelectedStatuses(selectedStatuses.filter(s => s !== status));
                                      }
                                    }}
                                  />
                                  <label
                                    htmlFor={`status-${status}`}
                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1 capitalize"
                                  >
                                    {status}
                                  </label>
                                </div>
                              ))}
                            </div>
                          </PopoverContent>
                        </Popover>
                      </div>

                      {/* Transaction Type Filter */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Transaction Type</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="w-full justify-between h-9 px-3">
                              <span className="text-sm">
                                {selectedTransactionTypes.length === 0 ? 'All types' :
                                 selectedTransactionTypes.length === 1 ? selectedTransactionTypes[0] :
                                 `${selectedTransactionTypes.length} selected`}
                              </span>
                              <ChevronDown className="h-4 w-4 opacity-50" />
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80 p-0" align="start">
                            <div className="max-h-64 overflow-y-auto p-2">
                              {['sale', 'inbound', 'adjustment'].map((type) => (
                                <div key={type} className="flex items-center space-x-2 py-2 px-2 hover:bg-gray-100 rounded">
                                  <Checkbox
                                    id={`type-${type}`}
                                    checked={selectedTransactionTypes.includes(type)}
                                    onCheckedChange={(checked) => {
                                      if (checked) {
                                        setSelectedTransactionTypes([...selectedTransactionTypes, type]);
                                      } else {
                                        setSelectedTransactionTypes(selectedTransactionTypes.filter(t => t !== type));
                                      }
                                    }}
                                  />
                                  <label
                                    htmlFor={`type-${type}`}
                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1 capitalize"
                                  >
                                    {type}
                                  </label>
                                </div>
                              ))}
                            </div>
                          </PopoverContent>
                        </Popover>
                      </div>

                      {/* Date Range Filter - Using native date inputs */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Date Range</label>
                        <Popover open={datePickerOpen} onOpenChange={setDatePickerOpen}>
                          <PopoverTrigger asChild>
                            <Button
                              variant="outline"
                              className={cn(
                                "w-full justify-start text-left font-normal h-9 px-3",
                                !dateFrom && !dateTo && "text-muted-foreground"
                              )}
                            >
                              <CalendarIcon className="mr-2 h-4 w-4" />
                              {dateFrom && dateTo ? (
                                <span className="text-sm truncate">
                                  {format(dateFrom, "MMM d")} - {format(dateTo, "MMM d, yyyy")}
                                </span>
                              ) : dateFrom ? (
                                <span className="text-sm">From {format(dateFrom, "MMM d, yyyy")}</span>
                              ) : dateTo ? (
                                <span className="text-sm">Until {format(dateTo, "MMM d, yyyy")}</span>
                              ) : (
                                <span className="text-sm">Pick dates</span>
                              )}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80 p-3" align="start">
                            <div className="space-y-3">
                              {/* Quick Presets */}
                              <div className="space-y-2">
                                <p className="text-xs font-medium text-gray-700">Quick Select</p>
                                <div className="grid grid-cols-2 gap-1">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-xs"
                                    onClick={() => {
                                      const today = new Date();
                                      setDateFrom(today);
                                      setDateTo(today);
                                    }}
                                  >
                                    Today
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-xs"
                                    onClick={() => {
                                      const today = new Date();
                                      const yesterday = new Date(today);
                                      yesterday.setDate(today.getDate() - 1);
                                      setDateFrom(yesterday);
                                      setDateTo(yesterday);
                                    }}
                                  >
                                    Yesterday
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-xs"
                                    onClick={() => {
                                      const today = new Date();
                                      const lastWeek = new Date(today);
                                      lastWeek.setDate(today.getDate() - 7);
                                      setDateFrom(lastWeek);
                                      setDateTo(today);
                                    }}
                                  >
                                    Last 7 days
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-xs"
                                    onClick={() => {
                                      const today = new Date();
                                      const last30Days = new Date(today);
                                      last30Days.setDate(today.getDate() - 30);
                                      setDateFrom(last30Days);
                                      setDateTo(today);
                                    }}
                                  >
                                    Last 30 days
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-xs"
                                    onClick={() => {
                                      const today = new Date();
                                      const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
                                      setDateFrom(firstDay);
                                      setDateTo(today);
                                    }}
                                  >
                                    This Month
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-xs"
                                    onClick={() => {
                                      const today = new Date();
                                      const firstDay = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                                      const lastDay = new Date(today.getFullYear(), today.getMonth(), 0);
                                      setDateFrom(firstDay);
                                      setDateTo(lastDay);
                                    }}
                                  >
                                    Last Month
                                  </Button>
                                </div>
                              </div>

                              {/* Native Date Inputs */}
                              <div className="space-y-3 pt-3 border-t">
                                <div className="space-y-2">
                                  <label className="text-xs font-medium text-gray-700">Custom Range</label>
                                  <div className="grid grid-cols-2 gap-2">
                                    <div className="space-y-1">
                                      <label htmlFor="date-from" className="text-xs text-gray-600">From</label>
                                      <input
                                        id="date-from"
                                        type="date"
                                        value={dateFrom ? format(dateFrom, 'yyyy-MM-dd') : ''}
                                        max={dateTo ? format(dateTo, 'yyyy-MM-dd') : undefined}
                                        onChange={(e) => {
                                          const date = e.target.value ? new Date(e.target.value + 'T00:00:00') : null;
                                          setDateFrom(date);
                                        }}
                                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      />
                                    </div>
                                    <div className="space-y-1">
                                      <label htmlFor="date-to" className="text-xs text-gray-600">To</label>
                                      <input
                                        id="date-to"
                                        type="date"
                                        value={dateTo ? format(dateTo, 'yyyy-MM-dd') : ''}
                                        min={dateFrom ? format(dateFrom, 'yyyy-MM-dd') : undefined}
                                        onChange={(e) => {
                                          const date = e.target.value ? new Date(e.target.value + 'T00:00:00') : null;
                                          setDateTo(date);
                                        }}
                                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      />
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Actions */}
                              <div className="flex justify-between items-center pt-2 border-t">
                                <span className="text-xs text-gray-500">
                                  {dateFrom && dateTo ? (
                                    <>
                                      {Math.ceil((dateTo.getTime() - dateFrom.getTime()) / (1000 * 60 * 60 * 24)) + 1} days
                                    </>
                                  ) : dateFrom || dateTo ? (
                                    'Select both dates'
                                  ) : (
                                    'No dates selected'
                                  )}
                                </span>
                                <div className="flex gap-2">
                                  {(dateFrom || dateTo) && (
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      className="h-7 px-2 text-xs"
                                      onClick={() => {
                                        setDateFrom(null);
                                        setDateTo(null);
                                      }}
                                    >
                                      Clear
                                    </Button>
                                  )}
                                  <Button
                                    size="sm"
                                    variant="default"
                                    className="h-7 px-3 text-xs"
                                    onClick={() => {
                                      setDatePickerOpen(false);
                                    }}
                                  >
                                    Done
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </PopoverContent>
                        </Popover>
                      </div>
                    </div>

                    {/* Filter Action Buttons */}
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleClearFilters}
                        disabled={!hasActiveFilters()}
                      >
                        Clear Filters
                      </Button>
                      <Button
                        size="sm"
                        onClick={handleApplyFilters}
                      >
                        Apply Filters
                      </Button>
                    </div>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                <div className="space-y-2 mb-4">
                  <div className="flex gap-4 text-sm">
                    <div className="flex items-center">
                      <ArrowDown className="w-4 h-4 text-green-600 mr-1" />
                      <span className="text-gray-600">Inbound</span>
                    </div>
                    <div className="flex items-center">
                      <ArrowUp className="w-4 h-4 text-red-600 mr-1" />
                      <span className="text-gray-600">Sales</span>
                    </div>
                    <div className="flex items-center">
                      <Activity className="w-4 h-4 text-gray-600 mr-1" />
                      <span className="text-gray-600">Adjustment</span>
                    </div>
                  </div>
                </div>

                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">Type</TableHead>
                      <TableHead>Transaction #</TableHead>
                      <TableHead>
                        <button
                          className="flex items-center gap-1 hover:text-gray-900"
                          onClick={() => handleTransactionSort('product')}
                        >
                          Product
                          {transactionSort.key === 'product' ? (
                            transactionSort.order === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronsUpDown className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </TableHead>
                      <TableHead>
                        <button
                          className="flex items-center gap-1 hover:text-gray-900"
                          onClick={() => handleTransactionSort('warehouse')}
                        >
                          Warehouse
                          {transactionSort.key === 'warehouse' ? (
                            transactionSort.order === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronsUpDown className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>
                        <button
                          className="flex items-center gap-1 hover:text-gray-900"
                          onClick={() => handleTransactionSort('transaction_timestamp')}
                        >
                          Date & Time
                          {transactionSort.key === 'transaction_timestamp' ? (
                            transactionSort.order === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronsUpDown className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {transactionsLoading ? (
                      <TableRow>
                        <TableCell colSpan={7} className="h-24 text-center">
                          <div className="flex items-center justify-center">
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            Loading transactions...
                          </div>
                        </TableCell>
                      </TableRow>
                    ) : (
                      transactions.map((transaction) => (
                        <TableRow key={transaction.transaction_id}>
                          <TableCell>{getTransactionIcon(transaction.transaction_type)}</TableCell>
                          <TableCell className="font-mono text-sm">{transaction.transaction_number}</TableCell>
                          <TableCell className="font-medium">{transaction.product}</TableCell>
                          <TableCell>{transaction.warehouse}</TableCell>
                          <TableCell>
                            <span className={`font-medium ${
                              transaction.quantity_change > 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {transaction.quantity_change > 0 ? '+' : ''}{transaction.quantity_change}
                            </span>
                          </TableCell>
                          <TableCell>{getStatusBadge(transaction.status)}</TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {new Date(transaction.transaction_timestamp).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
                <Pagination
                  pagination={transactionsPagination}
                  onPageChange={handleTransactionsPageChange}
                  showPageSize={true}
                  pageSizeOptions={[10, 20, 50, 100]}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab with Databricks AI/BI Dashboard */}
          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Inventory Analytics Dashboard</CardTitle>
                <CardDescription>
                  Real-time analytics and insights powered by Databricks AI/BI
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                {/*
                  IMPORTANT: Replace the src URL with your actual Databricks dashboard embed URL

                  To get the embed URL:
                  1. Go to your Databricks workspace
                  2. Navigate to your AI/BI dashboard
                  3. Click on the share/embed button
                  4. Copy the embed URL
                  5. Replace the placeholder URL below

                  The URL format should be like:
                  https://<workspace>.cloud.databricks.com/embed/dashboards/<dashboard-id>

                  You may also need to add authentication token if required:
                  https://<workspace>.cloud.databricks.com/embed/dashboards/<dashboard-id>?token=<token>
                */}
                <div className="relative w-full" style={{ height: '800px' }}>
                  <iframe
                    src="https://dbc-ea2c343f-6f56.cloud.databricks.com/embed/dashboardsv3/01f09a302c7d1be385cb0a98d6b1d08a?o=3813697403783275"
                    title="Databricks Analytics Dashboard"
                    className="absolute top-0 left-0 w-full h-full border-0"
                    allowFullScreen
                    loading="lazy"
                    sandbox="allow-scripts allow-same-origin allow-popups"
                  />
                  {/* Fallback message if iframe doesn't load */}
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-50 -z-10">
                    <div className="text-center">
                      <p className="text-gray-600 mb-2">Dashboard loading...</p>
                      <p className="text-sm text-gray-500">
                        If the dashboard doesn't appear, please check your Databricks dashboard ID and permissions.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Inventory Forecast Tab */}
          <TabsContent value="forecast" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Inventory Forecast</CardTitle>
                <CardDescription>
                  30-day demand forecast and reorder recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {forecast.length === 0 ? (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>No Forecast Data Available</AlertTitle>
                    <AlertDescription>
                      Forecast data is being calculated based on historical transactions.
                      Please check back later for AI-powered predictions.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <>
                    <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead
                          className="cursor-pointer select-none"
                          onClick={() => handleForecastSort('product')}
                        >
                          <div className="flex items-center">Product {getSortIcon('product')}</div>
                        </TableHead>
                        <TableHead>SKU</TableHead>
                        <TableHead>Warehouse</TableHead>
                        <TableHead
                          className="cursor-pointer select-none"
                          onClick={() => handleForecastSort('stock')}
                        >
                          <div className="flex items-center">Current Stock {getSortIcon('stock')}</div>
                        </TableHead>
                        <TableHead
                          className="cursor-pointer select-none"
                          onClick={() => handleForecastSort('forecast')}
                        >
                          <div className="flex items-center">30-Day Forecast {getSortIcon('forecast')}</div>
                        </TableHead>
                        <TableHead
                          className="cursor-pointer select-none"
                          onClick={() => handleForecastSort('severity')}
                        >
                          <div className="flex items-center">Status {getSortIcon('severity')}</div>
                        </TableHead>
                        <TableHead>Recommended Action</TableHead>
                        <TableHead>View Forecast</TableHead>
                        <TableHead>Create Order</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {forecastLoading ? (
                        <TableRow>
                          <TableCell colSpan={9} className="h-24 text-center">
                            <div className="flex items-center justify-center">
                              <Loader2 className="h-4 w-4 animate-spin mr-2" />
                              Loading forecast...
                            </div>
                          </TableCell>
                        </TableRow>
                      ) : (
                        forecast.map((item, index) => (
                          <TableRow key={item.forecast_id || index}>
                            <TableCell className="font-medium">{item.item_name}</TableCell>
                            <TableCell className="font-mono text-sm">{item.item_id}</TableCell>
                            <TableCell>
                              <div className="flex flex-col">
                                <span className="font-medium">{item.warehouse_name}</span>
                                <span className="text-xs text-gray-500">{item.warehouse_location}</span>
                              </div>
                            </TableCell>
                            <TableCell>{item.stock.toLocaleString()}</TableCell>
                            <TableCell>{item.forecast_30_days.toLocaleString()}</TableCell>
                            <TableCell>
                              {(() => {
                                const statusStyle = getInventoryStatusStyle(item.status);
                                const StatusIcon = statusStyle.icon;
                                return (
                                  <Badge 
                                    variant={statusStyle.variant}
                                    className={`${statusStyle.className} flex items-center gap-1 w-fit`}
                                  >
                                    <StatusIcon className="h-3 w-3" />
                                    {formatStatusText(item.status)}
                                  </Badge>
                                );
                              })()}
                            </TableCell>
                            <TableCell>
                              <span className={`font-medium ${
                                item.action === 'Urgent Reorder' ? 'text-red-600' :
                                item.action === 'Reorder Now' ? 'text-orange-600' :
                                item.action === 'Monitor' ? 'text-amber-600' :
                                item.action === 'Resolved' ? 'text-blue-600' :
                                item.action === 'No Action' ? 'text-emerald-600' :
                                'text-slate-600'
                              }`}>
                                {item.action}
                              </span>
                            </TableCell>
                            <TableCell>
                              <button
                                onClick={() => handleViewForecast(item)}
                                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors duration-200 flex items-center gap-1"
                              >
                                <Activity className="w-3 h-3" />
                                View Chart
                              </button>
                            </TableCell>
                            <TableCell>
                              <button
                                onClick={() => handleCreateOrder(item)}
                                className={`px-3 py-1 text-sm rounded-md transition-colors duration-200 flex items-center gap-1 ${
                                  item.status === 'in_stock' || item.status === 'resolved'
                                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                                }`}
                                disabled={item.status === 'in_stock' || item.status === 'resolved'}
                                title={
                                  item.status === 'in_stock' ? 'Stock is sufficient' :
                                  item.status === 'resolved' ? 'Order already created for this recommendation' :
                                  'Create reorder based on this recommendation'
                                }
                              >
                                <ShoppingCart className="w-3 h-3" />
                                {item.status === 'in_stock' ? 'In Stock' : 
                                 item.status === 'resolved' ? 'Resolved' : 'Reorder'}
                              </button>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                    <Pagination
                      pagination={forecastPagination}
                      onPageChange={handleForecastPageChange}
                      showPageSize={true}
                      pageSizeOptions={[10, 20, 50, 100]}
                    />
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Forecast Modal */}
      <ForecastModal
        isOpen={forecastModalOpen}
        onClose={closeForecastModal}
        item={selectedForecastItem}
        onCreateOrder={handleCreateOrderFromForecast}
      />

      {/* Create Order Modal */}
      <CreateOrderModal
        isOpen={createOrderModalOpen}
        onClose={closeCreateOrderModal}
        onOrderCreated={handleOrderCreated}
        onOrderSuccess={handleOrderSuccess}
        selectedItem={selectedOrderItem}
      />

      {/* Order Success Modal */}
      <OrderSuccessModal
        isOpen={orderSuccessModalOpen}
        onClose={closeOrderSuccessModal}
        onRefreshData={handleOrderCreated}
        orderData={successOrderData}
        onViewForecast={async () => {
          console.log('🔍 Button clicked! Looking for forecast item with ID:', successOrderData?.forecast_id);
          
          // First, try to find the item in the current forecast data
          let forecastItem = forecast.find(item => 
            item.forecast_id === successOrderData?.forecast_id
          );
          
          console.log('📊 Found in current data:', forecastItem);
          
          if (!forecastItem) {
            console.log('🔄 Not found in current page, fetching from API...');
            
            // If not found in current data, fetch it directly from the API
            try {
              const response = await apiClient.getInventoryForecast(
                undefined, // warehouseId
                undefined, // status  
                500, // high limit to find the item
                0 // offset
              );
              
              if (response?.items) {
                forecastItem = response.items.find(item => 
                  item.forecast_id === successOrderData?.forecast_id
                );
                console.log('🔍 Found via API:', forecastItem);
              }
            } catch (error) {
              console.error('❌ Error fetching forecast data:', error);
            }
          }
          
          if (forecastItem) {
            console.log('✅ Opening forecast modal for:', forecastItem.item_name);
            setSelectedForecastItem(forecastItem);
            setForecastModalOpen(true);
          } else {
            console.log('❌ Could not find forecast item with ID:', successOrderData?.forecast_id);
            alert(`Could not find forecast item with ID ${successOrderData?.forecast_id}. It may have been removed or is on a different page.`);
          }
        }}
      />
    </div>
  );
};

export default SmartStockDashboard;