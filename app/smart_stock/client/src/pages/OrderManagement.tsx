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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  AlertCircle, Package, ShoppingCart, Plus, Edit, Trash2,
  Clock, CheckCircle, Truck, Package2, XCircle, TrendingUp,
  TrendingDown, AlertTriangle
} from 'lucide-react';
import CreateOrderModal from '@/components/CreateOrderModal';
import EditOrderModal from '@/components/EditOrderModal';
import ForecastModal from '@/components/ForecastModal';

interface OrderData {
  order_id: number;
  order_number: string;
  product: string;
  quantity: number;
  store: string;
  requested_by: string;
  order_date: string;
  status: string;
}

interface InventoryForecastData {
  item_id: string;
  item_name: string;
  stock: number;
  forecast_30_days: number;
  status: string;
  action: string;
}

interface OrderKPI {
  total_orders: number;
  pending_orders: number;
  approved_orders: number;
  shipped_orders: number;
  average_order_value: number;
}

interface StockKPI {
  low_stock_items: number;
  out_of_stock_items: number;
  reorder_needed_items: number;
  total_alerts: number;
}

const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<OrderData[]>([]);
  const [inventory, setInventory] = useState<InventoryForecastData[]>([]);
  const [orderKPI, setOrderKPI] = useState<OrderKPI | null>(null);
  const [stockKPI, setStockKPI] = useState<StockKPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<OrderData | null>(null);
  const [isForecastModalOpen, setIsForecastModalOpen] = useState(false);
  const [selectedInventoryItem, setSelectedInventoryItem] = useState<InventoryForecastData | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [ordersRes, inventoryRes, orderKPIRes, stockKPIRes] = await Promise.all([
        fetch('/api/orders/'),
        fetch('/api/inventory/forecast'),
        fetch('/api/orders/kpi'),
        fetch('/api/inventory/alerts/kpi'),
      ]);

      if (!ordersRes.ok || !inventoryRes.ok || !orderKPIRes.ok || !stockKPIRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [ordersData, inventoryData, orderKPIData, stockKPIData] = await Promise.all([
        ordersRes.json(),
        inventoryRes.json(),
        orderKPIRes.json(),
        stockKPIRes.json(),
      ]);

      setOrders(ordersData);
      setInventory(inventoryData);
      setOrderKPI(orderKPIData);
      setStockKPI(stockKPIData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeStyles = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return {
          variant: 'secondary' as const,
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200 hover:bg-yellow-200',
          icon: Clock
        };
      case 'approved':
        return {
          variant: 'secondary' as const,
          className: 'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-200',
          icon: CheckCircle
        };
      case 'shipped':
        return {
          variant: 'secondary' as const,
          className: 'bg-purple-100 text-purple-800 border-purple-200 hover:bg-purple-200',
          icon: Truck
        };
      case 'delivered':
        return {
          variant: 'secondary' as const,
          className: 'bg-green-100 text-green-800 border-green-200 hover:bg-green-200',
          icon: Package2
        };
      case 'cancelled':
        return {
          variant: 'destructive' as const,
          className: 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200',
          icon: XCircle
        };
      default:
        return {
          variant: 'secondary' as const,
          className: 'bg-gray-100 text-gray-800 border-gray-200 hover:bg-gray-200',
          icon: Package
        };
    }
  };

  const getInventoryStatusBadgeStyles = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_stock':
        return {
          variant: 'secondary' as const,
          className: 'bg-green-100 text-green-800 border-green-200 hover:bg-green-200',
          icon: Package
        };
      case 'low_stock':
        return {
          variant: 'secondary' as const,
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200 hover:bg-yellow-200',
          icon: AlertTriangle
        };
      case 'out_of_stock':
        return {
          variant: 'destructive' as const,
          className: 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200',
          icon: AlertTriangle
        };
      case 'reorder_needed':
        return {
          variant: 'secondary' as const,
          className: 'bg-orange-100 text-orange-800 border-orange-200 hover:bg-orange-200',
          icon: TrendingDown
        };
      default:
        return {
          variant: 'secondary' as const,
          className: 'bg-gray-100 text-gray-800 border-gray-200 hover:bg-gray-200',
          icon: Package
        };
    }
  };


  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleEditOrder = (order: OrderData) => {
    setSelectedOrder(order);
    setIsEditModalOpen(true);
  };

  const handleOrderUpdated = () => {
    fetchData(); // Refresh all data
  };

  const handleOrderCreated = () => {
    fetchData(); // Refresh all data
  };

  const handleSeeForecast = (item: InventoryForecastData) => {
    setSelectedInventoryItem(item);
    setIsForecastModalOpen(true);
  };

  const getStatusTooltip = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'Order is awaiting approval from management';
      case 'approved':
        return 'Order has been approved and is ready for fulfillment';
      case 'shipped':
        return 'Order has been shipped and is in transit to the customer';
      case 'delivered':
        return 'Order has been successfully delivered to the customer';
      case 'cancelled':
        return 'Order has been cancelled and inventory has been restored';
      default:
        return 'Order status';
    }
  };

  const renderStatusBadge = (status: string, showIcon: boolean = true, showTooltip: boolean = false) => {
    const statusStyle = getStatusBadgeStyles(status);
    const StatusIcon = statusStyle.icon;
    
    const badge = (
      <Badge 
        variant={statusStyle.variant}
        className={`${statusStyle.className} ${showIcon ? 'flex items-center gap-1' : ''} w-fit cursor-default`}
      >
        {showIcon && <StatusIcon className="h-3 w-3" />}
        {status}
      </Badge>
    );

    if (showTooltip) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              {badge}
            </TooltipTrigger>
            <TooltipContent>
              <p>{getStatusTooltip(status)}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    return badge;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert className="border-red-500">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Error loading data: {error}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Inventory Management Dashboard</h1>

      <Tabs defaultValue="order-management" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="order-management">Order Management</TabsTrigger>
          <TabsTrigger value="inventory">Inventory</TabsTrigger>
        </TabsList>

        <TabsContent value="order-management" className="space-y-6">
          {/* Order Status Legend */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Order Status Guide</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {[
                  { status: 'pending', description: 'Awaiting approval' },
                  { status: 'approved', description: 'Ready for fulfillment' },
                  { status: 'shipped', description: 'In transit' },
                  { status: 'delivered', description: 'Completed successfully' },
                  { status: 'cancelled', description: 'Order cancelled' }
                ].map(({ status, description }) => (
                  <div key={status} className="flex items-center gap-2">
                    {renderStatusBadge(status)}
                    <span className="text-sm text-muted-foreground">{description}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* KPI Cards */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Order Management</CardTitle>
                <ShoppingCart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{orderKPI?.total_orders || 0}</div>
                <p className="text-xs text-muted-foreground">Total Orders</p>
                <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="font-medium">{orderKPI?.pending_orders || 0}</span>
                    <span className="text-muted-foreground"> Pending</span>
                  </div>
                  <div>
                    <span className="font-medium">{orderKPI?.approved_orders || 0}</span>
                    <span className="text-muted-foreground"> Approved</span>
                  </div>
                  <div>
                    <span className="font-medium">{orderKPI?.shipped_orders || 0}</span>
                    <span className="text-muted-foreground"> Shipped</span>
                  </div>
                </div>
                {orderKPI?.average_order_value && (
                  <div className="mt-2 text-xs">
                    <span className="text-muted-foreground">Avg. Order Value: </span>
                    <span className="font-medium">${orderKPI.average_order_value.toFixed(2)}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Stock Management Alert</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stockKPI?.total_alerts || 0}</div>
                <p className="text-xs text-muted-foreground">Total Alerts</p>
                <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="font-medium text-yellow-600">{stockKPI?.low_stock_items || 0}</span>
                    <span className="text-muted-foreground"> Low Stock</span>
                  </div>
                  <div>
                    <span className="font-medium text-red-600">{stockKPI?.out_of_stock_items || 0}</span>
                    <span className="text-muted-foreground"> Out of Stock</span>
                  </div>
                  <div>
                    <span className="font-medium text-orange-600">{stockKPI?.reorder_needed_items || 0}</span>
                    <span className="text-muted-foreground"> Reorder</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Orders Table */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Orders</CardTitle>
                  <CardDescription>
                    Manage and track your orders
                  </CardDescription>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Order
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Order Number</TableHead>
                    <TableHead>Product</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Store</TableHead>
                    <TableHead>Requested By</TableHead>
                    <TableHead>Order Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {orders.map((order) => (
                    <TableRow key={order.order_id}>
                      <TableCell className="font-medium">{order.order_number}</TableCell>
                      <TableCell>{order.product}</TableCell>
                      <TableCell>{order.quantity}</TableCell>
                      <TableCell>{order.store}</TableCell>
                      <TableCell>{order.requested_by}</TableCell>
                      <TableCell>{formatDate(order.order_date)}</TableCell>
                      <TableCell>
                        {renderStatusBadge(order.status, true, true)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleEditOrder(order)}
                            disabled={order.status === 'cancelled'}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="inventory" className="space-y-6">
          {/* Inventory Forecast Table */}
          <Card>
            <CardHeader>
              <CardTitle>Inventory Forecast</CardTitle>
              <CardDescription>
                30-day forecast and stock management
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item ID</TableHead>
                    <TableHead>Item Name</TableHead>
                    <TableHead>Stock</TableHead>
                    <TableHead>30 Day Forecast</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {inventory.map((item) => (
                    <TableRow key={item.item_id}>
                      <TableCell className="font-medium">{item.item_id}</TableCell>
                      <TableCell>{item.item_name}</TableCell>
                      <TableCell>{item.stock}</TableCell>
                      <TableCell>{item.forecast_30_days}</TableCell>
                      <TableCell>
                        {(() => {
                          const statusStyle = getInventoryStatusBadgeStyles(item.status);
                          const StatusIcon = statusStyle.icon;
                          return (
                            <Badge 
                              variant={statusStyle.variant}
                              className={`${statusStyle.className} flex items-center gap-1 w-fit`}
                            >
                              <StatusIcon className="h-3 w-3" />
                              {item.status.replace('_', ' ')}
                            </Badge>
                          );
                        })()}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleSeeForecast(item)}
                          className="flex items-center gap-2"
                        >
                          <TrendingUp className="h-3 w-3" />
                          See Forecast
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Modals */}
      <CreateOrderModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onOrderCreated={handleOrderCreated}
      />
      
      <EditOrderModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onOrderUpdated={handleOrderUpdated}
        order={selectedOrder}
      />
      
      <ForecastModal
        isOpen={isForecastModalOpen}
        onClose={() => setIsForecastModalOpen(false)}
        item={selectedInventoryItem}
      />
    </div>
  );
};

export default OrderManagement;