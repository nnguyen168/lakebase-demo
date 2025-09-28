import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw } from 'lucide-react';
import { apiClient } from '@/fastapi_client/client';

export function BasicTransactionList() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getTransactions(
        undefined, // status
        undefined, // warehouseId
        undefined, // productId
        undefined, // transactionType
        undefined, // dateFrom
        undefined, // dateTo
        50, // limit
        0 // offset
      );

      if (response && response.items) {
        setTransactions(response.items);
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>Latest 50 inventory movements</CardDescription>
          </div>
          <Button
            onClick={loadTransactions}
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
        {loading ? (
          <div className="text-center p-8">Loading transactions...</div>
        ) : transactions.length === 0 ? (
          <div className="text-center p-8 text-gray-500">No transactions found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Transaction #</th>
                  <th className="text-left p-2">Type</th>
                  <th className="text-left p-2">Product</th>
                  <th className="text-left p-2">Warehouse</th>
                  <th className="text-left p-2">Quantity</th>
                  <th className="text-left p-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.transaction_id} className="border-b">
                    <td className="p-2">{t.transaction_number || 'N/A'}</td>
                    <td className="p-2 capitalize">{t.transaction_type || 'N/A'}</td>
                    <td className="p-2">{t.product_name || 'N/A'}</td>
                    <td className="p-2">{t.warehouse_name || 'N/A'}</td>
                    <td className="p-2">
                      <span className={t.quantity_change > 0 ? 'text-green-600' : 'text-red-600'}>
                        {t.quantity_change > 0 ? '+' : ''}{t.quantity_change}
                      </span>
                    </td>
                    <td className="p-2">
                      <Badge variant="outline">
                        {t.status || 'pending'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}