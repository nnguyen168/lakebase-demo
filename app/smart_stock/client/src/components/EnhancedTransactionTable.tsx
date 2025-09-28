import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
// import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
// import { Calendar } from '@/components/ui/calendar';
// import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  RefreshCw, Filter, CheckCircle, Clock, Truck, Package2,
  ArrowUp, ArrowDown, Activity, X, AlertCircle,
  CheckSquare, Square, Settings
} from 'lucide-react';
// import { format } from 'date-fns';
import { apiClient } from '@/fastapi_client/client';
import type { TransactionResponse, Product, Warehouse, TransactionStatus } from '@/fastapi_client';
import { getTransactionStatusStyle, formatStatusText } from '@/lib/status-utils';
import Pagination, { PaginationMeta } from '@/components/ui/pagination';

interface EnhancedTransactionTableProps {
  onTransactionsUpdated?: () => void;
}

interface Filters {
  transactionType: string;
  productId: string;
  warehouseId: string;
  status: string;
  dateFrom: Date | undefined;
  dateTo: Date | undefined;
}

export function EnhancedTransactionTable({ onTransactionsUpdated }: EnhancedTransactionTableProps) {
  // State
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [selectedTransactions, setSelectedTransactions] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [bulkUpdateModalOpen, setBulkUpdateModalOpen] = useState(false);
  const [bulkUpdateStatus, setBulkUpdateStatus] = useState<TransactionStatus>('pending');
  const [bulkUpdateLoading, setBulkUpdateLoading] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState<string | null>(null);
  const [updateError, setUpdateError] = useState<string | null>(null);

  // Filters
  const [filters, setFilters] = useState<Filters>({
    transactionType: '',
    productId: '',
    warehouseId: '',
    status: '',
    dateFrom: undefined,
    dateTo: undefined
  });

  // Pagination
  const [pagination, setPagination] = useState<PaginationMeta>({
    total: 0,
    limit: 25,
    offset: 0,
    has_next: false,
    has_prev: false
  });

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Load transactions when filters change
  useEffect(() => {
    if (products.length > 0 && warehouses.length > 0) {
      loadTransactions();
    }
  }, [loadTransactions, products.length, warehouses.length]);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [productsResponse, warehousesResponse] = await Promise.all([
        apiClient.getProducts({ limit: 500 }),
        apiClient.getWarehouses({ limit: 100 })
      ]);
      setProducts(productsResponse.items || []);
      setWarehouses(warehousesResponse.items || []);
      // Don't load transactions here, let the useEffect handle it
    } finally {
      setLoading(false);
    }
  };

  const loadTransactions = useCallback(async (offset: number = 0, limit: number = 25) => {
    setRefreshing(true);
    try {
      console.log('Loading transactions with:', { offset, limit, filters });
      // Apply filters
      const response = await apiClient.getTransactions(
        filters.status || undefined,
        filters.warehouseId ? parseInt(filters.warehouseId) : undefined,
        undefined, // productId - not in filters yet
        filters.transactionType as any || undefined,
        undefined, // dateFrom - handled client-side for now
        undefined, // dateTo - handled client-side for now
        limit,
        offset
      );
      console.log('Transactions response:', response);

      if (response) {
        // Filter by date if needed (client-side for now)
        let filteredTransactions = response.items;

        if (filters.dateFrom || filters.dateTo) {
          filteredTransactions = filteredTransactions.filter(t => {
            const transDate = new Date(t.transaction_timestamp);
            if (filters.dateFrom && transDate < filters.dateFrom) return false;
            if (filters.dateTo && transDate > filters.dateTo) return false;
            return true;
          });
        }

        if (filters.productId) {
          filteredTransactions = filteredTransactions.filter(t => {
            const product = products.find(p => p.name === t.product);
            return product?.product_id.toString() === filters.productId;
          });
        }

        setTransactions(filteredTransactions);
        setPagination(response.pagination);
        // Clear selections when refreshing
        setSelectedTransactions(new Set());
        console.log('Set transactions:', filteredTransactions.length, 'items');
      } else {
        console.warn('No response from getTransactions API');
        setTransactions([]);
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
      setTransactions([]);
    } finally {
      setRefreshing(false);
    }
  }, [filters, products]);

  const handleRefresh = () => {
    loadTransactions(pagination.offset, pagination.limit);
  };

  const handlePageChange = (offset: number, limit: number) => {
    loadTransactions(offset, limit);
  };

  const handleSelectAll = () => {
    if (selectedTransactions.size === transactions.length) {
      setSelectedTransactions(new Set());
    } else {
      setSelectedTransactions(new Set(transactions.map(t => t.transaction_id)));
    }
  };

  const handleSelectTransaction = (transactionId: number) => {
    const newSelected = new Set(selectedTransactions);
    if (newSelected.has(transactionId)) {
      newSelected.delete(transactionId);
    } else {
      newSelected.add(transactionId);
    }
    setSelectedTransactions(newSelected);
  };

  const handleBulkStatusUpdate = async () => {
    if (selectedTransactions.size === 0) {
      setUpdateError('Please select at least one transaction');
      return;
    }

    setBulkUpdateLoading(true);
    setUpdateError(null);
    setUpdateSuccess(null);

    try {
      // Use bulk update endpoint
      const transactionIds = Array.from(selectedTransactions);
      await apiClient.bulkUpdateTransactionStatus({
        requestBody: {
          transaction_ids: transactionIds,
          status_update: { status: bulkUpdateStatus }
        }
      });

      setUpdateSuccess(`Successfully updated ${selectedTransactions.size} transaction(s) to ${bulkUpdateStatus}`);

      // Refresh the table
      await loadTransactions(pagination.offset, pagination.limit);

      // Clear selections
      setSelectedTransactions(new Set());

      // Close modal after a delay
      setTimeout(() => {
        setBulkUpdateModalOpen(false);
        setUpdateSuccess(null);
      }, 2000);

      // Notify parent
      onTransactionsUpdated?.();
    } catch (error: any) {
      setUpdateError(error.message || 'Failed to update transactions');
    } finally {
      setBulkUpdateLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({
      transactionType: '',
      productId: '',
      warehouseId: '',
      status: '',
      dateFrom: undefined,
      dateTo: undefined
    });
  };

  const getStatusBadge = (status: string) => {
    const statusStyle = getTransactionStatusStyle(status);
    const StatusIcon = statusStyle.icon;

    return (
      <Badge
        variant={statusStyle.variant}
        className={`${statusStyle.className} flex items-center gap-1`}
      >
        <StatusIcon className="w-3 h-3" />
        {formatStatusText(status)}
      </Badge>
    );
  };

  const getTransactionIcon = (type: string) => {
    if (type === 'inbound') return <ArrowDown className="w-4 h-4 text-green-600" />;
    if (type === 'sale') return <ArrowUp className="w-4 h-4 text-red-600" />;
    return <Activity className="w-4 h-4 text-gray-600" />;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Inventory Transactions</CardTitle>
            <CardDescription>
              Manage and update inventory transactions
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {selectedTransactions.size > 0 && (
              <Badge variant="secondary" className="px-3 py-1">
                {selectedTransactions.size} selected
              </Badge>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="gap-2"
            >
              <Filter className="h-4 w-4" />
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
              className="gap-2"
            >
              <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
              Refresh
            </Button>
            {selectedTransactions.size > 0 && (
              <Button
                size="sm"
                onClick={() => setBulkUpdateModalOpen(true)}
                className="gap-2"
              >
                <Settings className="h-4 w-4" />
                Update Status ({selectedTransactions.size})
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      {showFilters && (
        <CardContent className="border-b pb-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {/* Transaction Type Filter */}
            <div>
              <Label htmlFor="filter-type" className="text-xs">Type</Label>
              <Select
                value={filters.transactionType}
                onValueChange={(value) => setFilters({ ...filters, transactionType: value })}
              >
                <SelectTrigger id="filter-type" className="h-9">
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All types</SelectItem>
                  <SelectItem value="inbound">Inbound</SelectItem>
                  <SelectItem value="sale">Sale</SelectItem>
                  <SelectItem value="adjustment">Adjustment</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Product Filter */}
            <div>
              <Label htmlFor="filter-product" className="text-xs">Product</Label>
              <Select
                value={filters.productId}
                onValueChange={(value) => setFilters({ ...filters, productId: value })}
              >
                <SelectTrigger id="filter-product" className="h-9">
                  <SelectValue placeholder="All products" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All products</SelectItem>
                  {products.map((product) => (
                    <SelectItem key={product.product_id} value={product.product_id.toString()}>
                      {product.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Warehouse Filter */}
            <div>
              <Label htmlFor="filter-warehouse" className="text-xs">Warehouse</Label>
              <Select
                value={filters.warehouseId}
                onValueChange={(value) => setFilters({ ...filters, warehouseId: value })}
              >
                <SelectTrigger id="filter-warehouse" className="h-9">
                  <SelectValue placeholder="All warehouses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All warehouses</SelectItem>
                  {warehouses.map((warehouse) => (
                    <SelectItem key={warehouse.warehouse_id} value={warehouse.warehouse_id.toString()}>
                      {warehouse.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Status Filter */}
            <div>
              <Label htmlFor="filter-status" className="text-xs">Status</Label>
              <Select
                value={filters.status}
                onValueChange={(value) => setFilters({ ...filters, status: value })}
              >
                <SelectTrigger id="filter-status" className="h-9">
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="shipped">Shipped</SelectItem>
                  <SelectItem value="delivered">Delivered</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Date From Filter */}
            <div>
              <Label htmlFor="filter-date-from" className="text-xs">From Date</Label>
              <Input
                id="filter-date-from"
                type="date"
                className="h-9"
                value={filters.dateFrom ? filters.dateFrom.toISOString().split('T')[0] : ''}
                onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value ? new Date(e.target.value) : undefined })}
              />
            </div>

            {/* Date To Filter */}
            <div>
              <Label htmlFor="filter-date-to" className="text-xs">To Date</Label>
              <Input
                id="filter-date-to"
                type="date"
                className="h-9"
                value={filters.dateTo ? filters.dateTo.toISOString().split('T')[0] : ''}
                onChange={(e) => setFilters({ ...filters, dateTo: e.target.value ? new Date(e.target.value) : undefined })}
              />
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button
              size="sm"
              onClick={() => loadTransactions(0, pagination.limit)}
              className="gap-2"
            >
              <Filter className="h-4 w-4" />
              Apply Filters
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={clearFilters}
              className="gap-2"
            >
              <X className="h-4 w-4" />
              Clear Filters
            </Button>
          </div>
        </CardContent>
      )}

      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[50px]">
                <input
                  type="checkbox"
                  checked={transactions.length > 0 && selectedTransactions.size === transactions.length}
                  onChange={handleSelectAll}
                  aria-label="Select all"
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </TableHead>
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
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} className="h-24 text-center">
                  Loading transactions...
                </TableCell>
              </TableRow>
            ) : transactions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="h-24 text-center">
                  No transactions found
                </TableCell>
              </TableRow>
            ) : (
              transactions.map((transaction) => (
                <TableRow key={transaction.transaction_id}>
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={selectedTransactions.has(transaction.transaction_id)}
                      onChange={() => handleSelectTransaction(transaction.transaction_id)}
                      aria-label={`Select transaction ${transaction.transaction_number}`}
                      className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                  </TableCell>
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
              ))
            )}
          </TableBody>
        </Table>

        <div className="p-4 border-t">
          <Pagination
            pagination={pagination}
            onPageChange={handlePageChange}
            showPageSize={true}
            pageSizeOptions={[10, 25, 50, 100]}
          />
        </div>
      </CardContent>

      {/* Bulk Update Modal */}
      <Dialog open={bulkUpdateModalOpen} onOpenChange={setBulkUpdateModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Update Transaction Status</DialogTitle>
            <DialogDescription>
              Update the status for {selectedTransactions.size} selected transaction(s)
            </DialogDescription>
          </DialogHeader>

          {updateError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{updateError}</AlertDescription>
            </Alert>
          )}

          {updateSuccess && (
            <Alert className="border-green-500 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{updateSuccess}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="bulk-status">New Status</Label>
              <Select
                value={bulkUpdateStatus}
                onValueChange={(value: TransactionStatus) => setBulkUpdateStatus(value)}
              >
                <SelectTrigger id="bulk-status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">🕐 Pending</SelectItem>
                  <SelectItem value="confirmed">✅ Confirmed</SelectItem>
                  <SelectItem value="processing">⚙️ Processing</SelectItem>
                  <SelectItem value="shipped">📦 Shipped</SelectItem>
                  <SelectItem value="delivered">✔️ Delivered</SelectItem>
                  <SelectItem value="cancelled">❌ Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="text-sm text-gray-600">
              <p>Selected transactions will be updated to: <strong>{bulkUpdateStatus}</strong></p>
              <p className="mt-2">This action cannot be undone.</p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setBulkUpdateModalOpen(false)}
              disabled={bulkUpdateLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleBulkStatusUpdate}
              disabled={bulkUpdateLoading}
            >
              {bulkUpdateLoading ? 'Updating...' : 'Update Status'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}