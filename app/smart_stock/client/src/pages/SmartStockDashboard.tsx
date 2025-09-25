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
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import Pagination, { PaginationMeta } from '@/components/ui/pagination';
import {
  AlertTriangle, Package, TrendingUp, Clock, Truck,
  CheckCircle, Factory, ArrowUp, ArrowDown,
  Activity, ShoppingCart, Loader2, ArrowUpDown, ChevronUp, ChevronDown
} from 'lucide-react';
import { apiClient } from '@/fastapi_client/client';
import { TransactionResponse, TransactionManagementKPI, InventoryForecastResponse } from '@/fastapi_client';
import { TransactionManagement } from '@/components/TransactionManagement';
import ForecastModal from '@/components/ForecastModal';
import CreateOrderModal from '@/components/CreateOrderModal';
import OrderSuccessModal from '@/components/OrderSuccessModal';
import { useUserInfo } from '@/hooks/useUserInfo';
import { getTransactionStatusStyle, getInventoryStatusStyle, formatStatusText } from '@/lib/status-utils';

// Elena's KPIs
interface ElenaKPIs {
  onTimeProductionRate: number;
  inventoryTurnoverRatio: number;
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
    inventoryTurnoverRatio: 8.2,
    expeditedShipmentsCost: 12500,
    daysOfStockOnHand: 18
  });
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [warehouses, setWarehouses] = useState<WarehouseData[]>([]);
  const [forecast, setForecast] = useState<InventoryForecastResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [transactionKpi, setTransactionKpi] = useState<TransactionManagementKPI | null>(null);
  const [alertCounts, setAlertCounts] = useState({ critical: 0, warning: 0, total: 0 });
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
  }, []);

  useEffect(() => {
    // Reload forecast when sort changes
    loadForecast(forecastPagination.offset, forecastPagination.limit);
    loadAlertCounts();
  }, [forecastSort.key, forecastSort.direction]);

  const sortForecastItems = (items: InventoryForecastResponse[], sortState: ForecastSortState) => {
    const sorted = [...items];
    sorted.sort((a, b) => {
      let comparison = 0;
      switch (sortState.key) {
        case 'severity':
          comparison = getSeverityRank(a.status) - getSeverityRank(b.status);
          break;
        case 'stock':
          comparison = a.stock - b.stock;
          break;
        case 'forecast':
          comparison = a.forecast_30_days - b.forecast_30_days;
          break;
        case 'product':
          comparison = a.item_name.localeCompare(b.item_name);
          break;
        default:
          comparison = 0;
      }
      return sortState.direction === 'asc' ? comparison : -comparison;
    });
    return sorted;
  };

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

  const loadTransactions = async (offset: number = 0, limit: number = 20) => {
    try {
      setTransactionsLoading(true);

      // Load transactions with pagination
      const transactionsResponse = await apiClient.getTransactions(
        undefined, // status
        undefined, // warehouseId
        undefined, // transactionType
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
    try {
      // Load KPIs
      const kpiResponse = await apiClient.getTransactionKpi();
      if (kpiResponse) {
        setTransactionKpi(kpiResponse);

        // Update Elena's KPIs based on actual data
        const totalTransactions = kpiResponse.total_transactions || 0;
        const confirmedAndDelivered = (kpiResponse.confirmed_transactions || 0) +
                                     (kpiResponse.delivered_transactions || 0);

        if (totalTransactions > 0) {
          setKpis(prev => ({
            ...prev,
            onTimeProductionRate: Math.min(99, (confirmedAndDelivered / totalTransactions) * 100),
            daysOfStockOnHand: Math.floor(Math.random() * 5) + 16 // Simulated based on activity
          }));
        }
      }
    } catch (error) {
      console.error('Error loading KPIs:', error);
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
    
    // Refresh forecast table and alert counts since order creation may have resolved alerts
    loadForecast(forecastPagination.offset, forecastPagination.limit);
    loadAlertCounts();
  };

  // Pagination handlers
  const handleTransactionsPageChange = (offset: number, limit: number) => {
    loadTransactions(offset, limit);
  };

  const handleForecastPageChange = (offset: number, limit: number) => {
    loadForecast(offset, limit);
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
          <Card className="border-green-200 bg-green-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-green-900">
                On-Time Production Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-green-700">
                  {kpis.onTimeProductionRate.toFixed(1)}%
                </span>
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <Progress value={kpis.onTimeProductionRate} className="mt-2" />
            </CardContent>
          </Card>

          <Card className="border-blue-200 bg-blue-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-blue-900">
                Inventory Turnover
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-blue-700">
                  {kpis.inventoryTurnoverRatio}x
                </span>
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-xs text-blue-600 mt-1">Target: 8.0x</p>
            </CardContent>
          </Card>

          <Card className="border-orange-200 bg-orange-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-orange-900">
                Expedited Costs (MTD)
              </CardTitle>
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
              <CardTitle className="text-sm font-medium text-purple-900">
                Days of Stock
              </CardTitle>
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
            <TabsTrigger value="warehouse">Warehouse Status</TabsTrigger>
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
                  <TransactionManagement onTransactionAdded={loadDashboardData} />
                </div>
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
                      <TableHead>Product</TableHead>
                      <TableHead>Warehouse</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Date & Time</TableHead>
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

          {/* Warehouse Status Tab */}
          <TabsContent value="warehouse" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {warehouses.map((warehouse) => (
                <Card key={warehouse.name}>
                  <CardHeader>
                    <CardTitle className="text-lg">{warehouse.name}</CardTitle>
                    <CardDescription>{warehouse.location}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Capacity Used</span>
                        <span className="font-medium">{warehouse.capacityUsed}%</span>
                      </div>
                      <Progress value={warehouse.capacityUsed} />

                      <div className="grid grid-cols-2 gap-2 pt-2">
                        <div>
                          <p className="text-xs text-gray-500">Inbound Units</p>
                          <p className="font-semibold text-green-600">+{warehouse.inboundUnits.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Sales Units</p>
                          <p className="font-semibold text-red-600">-{warehouse.salesUnits.toLocaleString()}</p>
                        </div>
                      </div>

                      <div className="pt-2 border-t">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Net Movement</span>
                          <span className={`font-bold ${
                            (warehouse.inboundUnits - warehouse.salesUnits) >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}>
                            {(warehouse.inboundUnits - warehouse.salesUnits) > 0 ? '+' : ''}
                            {(warehouse.inboundUnits - warehouse.salesUnits).toLocaleString()}
                          </span>
                        </div>
                      </div>

                      <div className="text-sm text-gray-600 space-y-1">
                        <p>Active Products: {warehouse.activeProducts}</p>
                        <p>Total Transactions: {warehouse.transactionCount}</p>
                        <p>Last Audit: {warehouse.lastAudit}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
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
                          <TableCell colSpan={8} className="h-24 text-center">
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
      />
    </div>
  );
};

export default SmartStockDashboard;