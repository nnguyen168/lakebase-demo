import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, CheckCircle, Clock, Truck, Package2, ArrowUp, ArrowDown, Activity } from 'lucide-react';
import { apiClient } from '@/fastapi_client/client';
import type { TransactionResponse } from '@/fastapi_client';
import { getTransactionStatusStyle, formatStatusText } from '@/lib/status-utils';
import Pagination, { PaginationMeta } from '@/components/ui/pagination';

interface SimpleTransactionTableProps {
  onTransactionsUpdated?: () => void;
}

export function SimpleTransactionTable({ onTransactionsUpdated }: SimpleTransactionTableProps) {
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    page_size: 25,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_previous: false
  });

  const loadTransactions = async (page: number = 1) => {
    setLoading(true);
    try {
      const offset = (page - 1) * 25;
      const response = await apiClient.getTransactions(
        undefined, // status
        undefined, // warehouseId
        undefined, // productId
        undefined, // transactionType
        undefined, // dateFrom
        undefined, // dateTo
        25, // limit
        offset
      );

      if (response) {
        setTransactions(response.items);
        setPagination(response.pagination);
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  const handleRefresh = () => {
    loadTransactions(pagination.page);
    if (onTransactionsUpdated) {
      onTransactionsUpdated();
    }
  };

  const handlePageChange = (newPage: number) => {
    loadTransactions(newPage);
  };

  const getTransactionIcon = (type: string) => {
    if (type === 'inbound') return <ArrowDown className="w-4 h-4 text-green-600" />;
    if (type === 'sale') return <ArrowUp className="w-4 h-4 text-red-600" />;
    return <Activity className="w-4 h-4 text-gray-600" />;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Inventory Transactions</CardTitle>
            <CardDescription>Manage and track all inventory movements</CardDescription>
          </div>
          <Button
            onClick={handleRefresh}
            disabled={loading}
            size="sm"
            variant="outline"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Transaction #</th>
                <th className="text-left p-2">Type</th>
                <th className="text-left p-2">Product</th>
                <th className="text-left p-2">Warehouse</th>
                <th className="text-left p-2">Quantity</th>
                <th className="text-left p-2">Status</th>
                <th className="text-left p-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center p-4">Loading...</td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center p-4">No transactions found</td>
                </tr>
              ) : (
                transactions.map((transaction) => {
                  const statusStyle = getTransactionStatusStyle(transaction.status);
                  const StatusIcon = statusStyle.icon;

                  return (
                    <tr key={transaction.transaction_id} className="border-b hover:bg-gray-50">
                      <td className="p-2 font-medium">{transaction.transaction_number}</td>
                      <td className="p-2">
                        <div className="flex items-center gap-1">
                          {getTransactionIcon(transaction.transaction_type)}
                          <span className="capitalize">{transaction.transaction_type}</span>
                        </div>
                      </td>
                      <td className="p-2">{transaction.product_name}</td>
                      <td className="p-2">{transaction.warehouse_name}</td>
                      <td className="p-2">
                        <span className={transaction.quantity_change > 0 ? 'text-green-600' : 'text-red-600'}>
                          {transaction.quantity_change > 0 ? '+' : ''}{transaction.quantity_change}
                        </span>
                      </td>
                      <td className="p-2">
                        <Badge variant={statusStyle.variant} className={statusStyle.className}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {formatStatusText(transaction.status)}
                        </Badge>
                      </td>
                      <td className="p-2 text-sm text-gray-600">
                        {formatDate(transaction.transaction_timestamp)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {!loading && transactions.length > 0 && (
          <div className="mt-4">
            <Pagination
              currentPage={pagination.page}
              totalPages={pagination.total_pages}
              onPageChange={handlePageChange}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}