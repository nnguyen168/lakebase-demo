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
  AlertTriangle, Package, TrendingUp, Clock, Truck,
  CheckCircle, XCircle, ShoppingCart, AlertCircle,
  Factory, Battery, Settings, Zap
} from 'lucide-react';
import { apiClient } from '@/fastapi_client/client';
import { useUserInfo } from '@/hooks/useUserInfo';

// Elena's KPIs
interface ElenaKPIs {
  onTimeProductionRate: number;
  inventoryTurnoverRatio: number;
  expeditedShipmentsCost: number;
  daysOfStockOnHand: number;
  criticalComponents: number;
  pendingReorders: number;
}

interface ComponentStatus {
  sku: string;
  name: string;
  category: 'motor' | 'battery' | 'frame' | 'wheel' | 'brake' | 'electronics';
  currentStock: number;
  requiredForProduction: number;
  daysOfStock: number;
  leadTime: number;
  supplier: string;
  status: 'healthy' | 'warning' | 'critical';
  nextDelivery?: string;
  reorderPoint: number;
}

const InventoryDashboard: React.FC = () => {
  const { displayName, role } = useUserInfo();
  const [activeTab, setActiveTab] = useState('overview');
  const [kpis, setKpis] = useState<ElenaKPIs>({
    onTimeProductionRate: 94.5,
    inventoryTurnoverRatio: 8.2,
    expeditedShipmentsCost: 12500,
    daysOfStockOnHand: 18,
    criticalComponents: 3,
    pendingReorders: 7
  });
  const [components, setComponents] = useState<ComponentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [forecast, setForecast] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load forecast data
      const forecastResponse = await apiClient.getInventoryForecast();
      if (forecastResponse.data) {
        setForecast(forecastResponse.data);

        // Transform forecast data to component status
        const componentData: ComponentStatus[] = forecastResponse.data.map((item: any) => ({
          sku: item.item_id,
          name: item.item_name,
          category: categorizeComponent(item.item_name),
          currentStock: item.stock,
          requiredForProduction: Math.floor(item.forecast_30_days / 30 * 7), // Weekly requirement
          daysOfStock: Math.floor(item.stock / (item.forecast_30_days / 30)),
          leadTime: 14, // Default lead time
          supplier: getSupplierName(item.item_name),
          status: getComponentStatus(item.status),
          reorderPoint: Math.floor(item.forecast_30_days * 0.3),
          nextDelivery: getNextDelivery(item.status)
        }));
        setComponents(componentData);
      }

      // Load alerts
      const alertsResponse = await apiClient.getStockAlertsKpi();
      if (alertsResponse.data) {
        setAlerts(alertsResponse.data);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const categorizeComponent = (name: string): ComponentStatus['category'] => {
    const nameLower = name.toLowerCase();
    if (nameLower.includes('motor')) return 'motor';
    if (nameLower.includes('battery')) return 'battery';
    if (nameLower.includes('frame')) return 'frame';
    if (nameLower.includes('wheel')) return 'wheel';
    if (nameLower.includes('brake')) return 'brake';
    return 'electronics';
  };

  const getSupplierName = (componentName: string): string => {
    const suppliers: Record<string, string> = {
      'motor': 'Bosch eBike Systems',
      'battery': 'Samsung SDI',
      'frame': 'Carbon Tech EU',
      'wheel': 'DT Swiss',
      'brake': 'Shimano Europe',
      'default': 'General Supplies Ltd'
    };

    const category = categorizeComponent(componentName);
    return suppliers[category] || suppliers.default;
  };

  const getComponentStatus = (status: string): 'healthy' | 'warning' | 'critical' => {
    switch (status) {
      case 'out_of_stock':
        return 'critical';
      case 'reorder_needed':
      case 'low_stock':
        return 'warning';
      default:
        return 'healthy';
    }
  };

  const getNextDelivery = (status: string): string | undefined => {
    if (status === 'reorder_needed' || status === 'out_of_stock') {
      const days = Math.floor(Math.random() * 7) + 3;
      const date = new Date();
      date.setDate(date.getDate() + days);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
    return undefined;
  };

  const getCategoryIcon = (category: ComponentStatus['category']) => {
    const icons = {
      motor: <Zap className="w-4 h-4" />,
      battery: <Battery className="w-4 h-4" />,
      frame: <Package className="w-4 h-4" />,
      wheel: <Settings className="w-4 h-4" />,
      brake: <AlertCircle className="w-4 h-4" />,
      electronics: <Settings className="w-4 h-4" />
    };
    return icons[category];
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
      {alerts && alerts.total_alerts > 0 && (
        <div className="container mx-auto px-4 py-4">
          <Alert className="bg-red-50 border-red-200">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertTitle className="text-red-900">Action Required</AlertTitle>
            <AlertDescription className="text-red-700">
              {alerts.out_of_stock_items > 0 && (
                <span className="block">
                  • {alerts.out_of_stock_items} components are out of stock - production at risk!
                </span>
              )}
              {alerts.reorder_needed_items > 0 && (
                <span className="block">
                  • {alerts.reorder_needed_items} components need immediate reordering
                </span>
              )}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* KPI Cards */}
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
                  {kpis.onTimeProductionRate}%
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
            <TabsTrigger value="overview">Critical Components</TabsTrigger>
            <TabsTrigger value="warehouse">Warehouse Status</TabsTrigger>
            <TabsTrigger value="forecast">30-Day Forecast</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Component Inventory Status</CardTitle>
                <CardDescription>
                  Real-time view of critical e-bike components across all warehouses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">Type</TableHead>
                      <TableHead>Component</TableHead>
                      <TableHead>SKU</TableHead>
                      <TableHead>Current Stock</TableHead>
                      <TableHead>Required/Week</TableHead>
                      <TableHead>Days of Stock</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Supplier</TableHead>
                      <TableHead>Next Delivery</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {components.map((component, index) => (
                      <TableRow key={index} className={component.status === 'critical' ? 'bg-red-50' : ''}>
                        <TableCell>{getCategoryIcon(component.category)}</TableCell>
                        <TableCell className="font-medium">{component.name}</TableCell>
                        <TableCell className="text-sm text-gray-600">{component.sku}</TableCell>
                        <TableCell>{component.currentStock.toLocaleString()}</TableCell>
                        <TableCell>{component.requiredForProduction.toLocaleString()}</TableCell>
                        <TableCell>
                          <Badge variant={component.daysOfStock < 7 ? 'destructive' : 'default'}>
                            {component.daysOfStock} days
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              component.status === 'critical' ? 'destructive' :
                              component.status === 'warning' ? 'secondary' :
                              'default'
                            }
                          >
                            {component.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">{component.supplier}</TableCell>
                        <TableCell>
                          {component.nextDelivery && (
                            <span className="text-sm font-medium">{component.nextDelivery}</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {(component.status === 'warning' || component.status === 'critical') && (
                            <Button size="sm" variant={component.status === 'critical' ? 'destructive' : 'default'}>
                              {component.status === 'critical' ? 'Expedite' : 'Reorder'}
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="warehouse" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Lyon Main Warehouse</CardTitle>
                  <CardDescription>Primary distribution center</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Capacity Used</span>
                      <span className="font-medium">78%</span>
                    </div>
                    <Progress value={78} />
                    <div className="pt-2">
                      <p className="text-sm text-gray-600">Active SKUs: 42</p>
                      <p className="text-sm text-gray-600">Last Audit: 2 days ago</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Munich Assembly Hub</CardTitle>
                  <CardDescription>Production support</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Capacity Used</span>
                      <span className="font-medium">65%</span>
                    </div>
                    <Progress value={65} />
                    <div className="pt-2">
                      <p className="text-sm text-gray-600">Active SKUs: 38</p>
                      <p className="text-sm text-gray-600">Last Audit: 5 days ago</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Milan Overflow</CardTitle>
                  <CardDescription>Secondary storage</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Capacity Used</span>
                      <span className="font-medium">45%</span>
                    </div>
                    <Progress value={45} />
                    <div className="pt-2">
                      <p className="text-sm text-gray-600">Active SKUs: 28</p>
                      <p className="text-sm text-gray-600">Last Audit: 1 week ago</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="forecast" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>30-Day Demand Forecast</CardTitle>
                <CardDescription>
                  AI-powered predictions based on historical data and market trends
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Alert>
                    <TrendingUp className="h-4 w-4" />
                    <AlertTitle>Increased Demand Expected</AlertTitle>
                    <AlertDescription>
                      Spring season approaching - expect 35% increase in e-bike demand over next 30 days
                    </AlertDescription>
                  </Alert>

                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Component Category</TableHead>
                        <TableHead>Current Stock</TableHead>
                        <TableHead>30-Day Forecast</TableHead>
                        <TableHead>Recommended Action</TableHead>
                        <TableHead>Confidence</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {forecast.slice(0, 8).map((item, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{item.item_name}</TableCell>
                          <TableCell>{item.stock.toLocaleString()}</TableCell>
                          <TableCell>{item.forecast_30_days.toLocaleString()}</TableCell>
                          <TableCell>
                            <Badge variant={item.action === 'Urgent Reorder' ? 'destructive' : 'secondary'}>
                              {item.action}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Progress value={85 + Math.random() * 10} className="w-20" />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default InventoryDashboard;