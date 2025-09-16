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
  CheckCircle, ArrowUp, ArrowDown, Factory, Battery,
  Settings, Zap, Activity, BarChart3, Package2
} from 'lucide-react';
import { apiClient } from '@/fastapi_client';
import { TransactionResponse, TransactionManagementKPI } from '@/fastapi_client';

const TransactionsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('transactions');
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [kpi, setKpi] = useState<TransactionManagementKPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [productSummary, setProductSummary] = useState<Map<string, { inbound: number, sales: number, net: number }>>(new Map());
  const [warehouseSummary, setWarehouseSummary] = useState<Map<string, { inbound: number, sales: number, transactions: number }>>(new Map());

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load transactions
      const transactionsResponse = await apiClient.getTransactions();
      if (transactionsResponse.data) {
        setTransactions(transactionsResponse.data);

        // Calculate summaries
        const prodSummary = new Map<string, { inbound: number, sales: number, net: number }>();
        const whSummary = new Map<string, { inbound: number, sales: number, transactions: number }>();

        transactionsResponse.data.forEach((t: TransactionResponse) => {
          // Product summary
          if (!prodSummary.has(t.product)) {
            prodSummary.set(t.product, { inbound: 0, sales: 0, net: 0 });
          }
          const prod = prodSummary.get(t.product)!;
          if (t.transaction_type === 'inbound') {
            prod.inbound += Math.abs(t.quantity_change);
          } else if (t.transaction_type === 'sale') {
            prod.sales += Math.abs(t.quantity_change);
          }
          prod.net += t.quantity_change;

          // Warehouse summary
          if (!whSummary.has(t.warehouse)) {
            whSummary.set(t.warehouse, { inbound: 0, sales: 0, transactions: 0 });
          }
          const wh = whSummary.get(t.warehouse)!;
          if (t.transaction_type === 'inbound') {
            wh.inbound += Math.abs(t.quantity_change);
          } else if (t.transaction_type === 'sale') {
            wh.sales += Math.abs(t.quantity_change);
          }
          wh.transactions += 1;
        });

        setProductSummary(prodSummary);
        setWarehouseSummary(whSummary);
      }

      // Load KPIs
      const kpiResponse = await apiClient.getTransactionKpi();
      if (kpiResponse.data) {
        setKpi(kpiResponse.data);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      'pending': 'secondary',
      'confirmed': 'default',
      'processing': 'secondary',
      'shipped': 'default',
      'delivered': 'default',
      'cancelled': 'destructive'
    };

    const icons: Record<string, any> = {
      'pending': <Clock className="w-3 h-3 mr-1" />,
      'confirmed': <CheckCircle className="w-3 h-3 mr-1" />,
      'processing': <Settings className="w-3 h-3 mr-1" />,
      'shipped': <Truck className="w-3 h-3 mr-1" />,
      'delivered': <Package className="w-3 h-3 mr-1" />
    };

    return (
      <Badge variant={variants[status] || 'default'} className="flex items-center">
        {icons[status]}
        {status}
      </Badge>
    );
  };

  const getTransactionIcon = (type: string) => {
    if (type === 'inbound') return <ArrowDown className="w-4 h-4 text-green-600" />;
    if (type === 'sale') return <ArrowUp className="w-4 h-4 text-red-600" />;
    return <Activity className="w-4 h-4 text-gray-600" />;
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
                <p className="text-sm text-gray-600">VulcanTech Manufacturing · Real-Time Inventory</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="px-3 py-1">
                <Activity className="w-3 h-3 mr-1" />
                {transactions.length} Transactions
              </Badge>
              <div className="text-right">
                <p className="text-sm font-medium">Elena Rodriguez</p>
                <p className="text-xs text-gray-600">Senior Inventory Planner</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      {kpi && (
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-blue-900">
                  Total Transactions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-blue-700">
                    {kpi.total_transactions}
                  </span>
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-green-50">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-green-900">
                  Confirmed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-green-700">
                    {kpi.confirmed_transactions}
                  </span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <Progress value={(kpi.confirmed_transactions / kpi.total_transactions) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card className="border-orange-200 bg-orange-50">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-orange-900">
                  Pending
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-orange-700">
                    {kpi.pending_transactions}
                  </span>
                  <Clock className="w-5 h-5 text-orange-600" />
                </div>
                <p className="text-xs text-orange-600 mt-1">Awaiting confirmation</p>
              </CardContent>
            </Card>

            <Card className="border-purple-200 bg-purple-50">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-purple-900">
                  Total Units Moved
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-purple-700">
                    {kpi.total_quantity_change?.toLocaleString() || 0}
                  </span>
                  <Package2 className="w-5 h-5 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Main Content Tabs */}
      <div className="container mx-auto px-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="transactions">Recent Transactions</TabsTrigger>
            <TabsTrigger value="products">Product Movement</TabsTrigger>
            <TabsTrigger value="warehouses">Warehouse Activity</TabsTrigger>
          </TabsList>

          <TabsContent value="transactions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Inventory Transactions</CardTitle>
                <CardDescription>
                  Real-time view of all inventory movements across warehouses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Type</TableHead>
                      <TableHead>Transaction #</TableHead>
                      <TableHead>Product</TableHead>
                      <TableHead>Warehouse</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Timestamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {transactions.slice(0, 20).map((transaction) => (
                      <TableRow key={transaction.transaction_id}>
                        <TableCell>{getTransactionIcon(transaction.transaction_type)}</TableCell>
                        <TableCell className="font-mono text-sm">{transaction.transaction_number}</TableCell>
                        <TableCell className="font-medium">{transaction.product}</TableCell>
                        <TableCell>{transaction.warehouse}</TableCell>
                        <TableCell>
                          <span className={transaction.quantity_change > 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                            {transaction.quantity_change > 0 ? '+' : ''}{transaction.quantity_change}
                          </span>
                        </TableCell>
                        <TableCell>{getStatusBadge(transaction.status)}</TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {new Date(transaction.transaction_timestamp).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="products" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Product Movement Summary</CardTitle>
                <CardDescription>
                  Inbound vs outbound quantities by product
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product</TableHead>
                      <TableHead>Total Inbound</TableHead>
                      <TableHead>Total Sales</TableHead>
                      <TableHead>Net Movement</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Array.from(productSummary.entries())
                      .sort((a, b) => Math.abs(b[1].net) - Math.abs(a[1].net))
                      .slice(0, 15)
                      .map(([product, summary]) => (
                        <TableRow key={product}>
                          <TableCell className="font-medium">{product}</TableCell>
                          <TableCell>
                            <span className="text-green-600 font-medium">+{summary.inbound}</span>
                          </TableCell>
                          <TableCell>
                            <span className="text-red-600 font-medium">-{summary.sales}</span>
                          </TableCell>
                          <TableCell>
                            <span className={summary.net >= 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                              {summary.net > 0 ? '+' : ''}{summary.net}
                            </span>
                          </TableCell>
                          <TableCell>
                            <Badge variant={summary.net < 0 ? 'destructive' : 'default'}>
                              {summary.net < 0 ? 'Negative' : 'Positive'}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="warehouses" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Array.from(warehouseSummary.entries()).map(([warehouse, summary]) => (
                <Card key={warehouse}>
                  <CardHeader>
                    <CardTitle className="text-lg">{warehouse}</CardTitle>
                    <CardDescription>{summary.transactions} total transactions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Inbound Units</span>
                        <span className="font-medium text-green-600">+{summary.inbound.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Sales Units</span>
                        <span className="font-medium text-red-600">-{summary.sales.toLocaleString()}</span>
                      </div>
                      <div className="pt-2 border-t">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Net Movement</span>
                          <span className={`font-bold ${(summary.inbound - summary.sales) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {(summary.inbound - summary.sales) > 0 ? '+' : ''}{summary.inbound - summary.sales}
                          </span>
                        </div>
                      </div>
                      <Progress
                        value={summary.inbound / (summary.inbound + summary.sales) * 100}
                        className="mt-2"
                      />
                      <p className="text-xs text-gray-500">
                        {Math.round(summary.inbound / (summary.inbound + summary.sales) * 100)}% inbound
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default TransactionsDashboard;