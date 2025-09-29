import React, { useState, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Upload, FileSpreadsheet, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/fastapi_client/client';
import type { TransactionType } from '@/fastapi_client';

interface TransactionManagementProps {
  onTransactionAdded?: () => void;
}

export function TransactionManagement({ onTransactionAdded }: TransactionManagementProps) {
  const [singleModalOpen, setSingleModalOpen] = useState(false);
  const [bulkModalOpen, setBulkModalOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Single transaction form state
  const [singleForm, setSingleForm] = useState({
    product_id: '',
    warehouse_id: '',
    quantity_change: '',
    transaction_type: 'inbound' as TransactionType,
    notes: ''
  });

  // Bulk transactions state
  const [bulkData, setBulkData] = useState('');

  const handleSingleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      // Call API to create transaction (backend auto-generates transaction number)
      await apiClient.createTransaction({
        product_id: parseInt(singleForm.product_id),
        warehouse_id: parseInt(singleForm.warehouse_id),
        quantity_change: parseInt(singleForm.quantity_change),
        transaction_type: singleForm.transaction_type,
        notes: singleForm.notes || undefined
      });
      setSingleModalOpen(false);
      onTransactionAdded?.();
      // Reset form
      setSingleForm({
        product_id: '',
        warehouse_id: '',
        quantity_change: '',
        transaction_type: 'inbound' as TransactionType,
        notes: ''
      });
    } catch (err: any) {
      setError(err.message || 'Failed to create transaction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      // Parse bulk data (expecting JSON format)
      const transactions = JSON.parse(bulkData);
      // TODO: Call API to create bulk transactions
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulated delay
      setBulkModalOpen(false);
      setBulkData('');
      onTransactionAdded?.();
    } catch (err) {
      setError('Invalid JSON format or failed to create transactions.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    // Demo only - just show success after a delay
    setTimeout(() => {
      alert(`File "${file.name}" selected successfully!\n\nThis is a demo - actual file processing is not implemented yet.`);
      setUploadModalOpen(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="flex gap-2">
      {/* Single Transaction Button - Modal handled by parent */}
      <Button
        size="sm"
        className="gap-2"
        onClick={() => {
          // Trigger the parent's enhanced modal
          const event = new CustomEvent('openCreateTransaction');
          window.dispatchEvent(event);
        }}
      >
        <Plus className="h-4 w-4" />
        Create Transaction
      </Button>

      {/* Original Dialog kept but hidden - will be removed in cleanup */}
      <Dialog open={false} onOpenChange={setSingleModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Transaction</DialogTitle>
            <DialogDescription>
              Add a single inventory transaction to the system.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="grid gap-2">
              <Label htmlFor="transaction_type">Transaction Type</Label>
              <Select
                value={singleForm.transaction_type}
                onValueChange={(value: TransactionType) => setSingleForm({ ...singleForm, transaction_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="inbound">Inbound</SelectItem>
                  <SelectItem value="sale">Sale</SelectItem>
                  <SelectItem value="adjustment">Adjustment</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="product_id">Product ID</Label>
                <Input
                  id="product_id"
                  type="number"
                  value={singleForm.product_id}
                  onChange={(e) => setSingleForm({ ...singleForm, product_id: e.target.value })}
                  placeholder="Enter product ID"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="warehouse_id">Warehouse ID</Label>
                <Input
                  id="warehouse_id"
                  type="number"
                  value={singleForm.warehouse_id}
                  onChange={(e) => setSingleForm({ ...singleForm, warehouse_id: e.target.value })}
                  placeholder="Enter warehouse ID"
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="quantity_change">Quantity Change</Label>
              <Input
                id="quantity_change"
                type="number"
                value={singleForm.quantity_change}
                onChange={(e) => setSingleForm({ ...singleForm, quantity_change: e.target.value })}
                placeholder="Positive for inbound, negative for sale"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={singleForm.notes}
                onChange={(e) => setSingleForm({ ...singleForm, notes: e.target.value })}
                placeholder="Additional notes..."
                rows={3}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setSingleModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSingleSubmit} disabled={loading}>
              {loading ? 'Creating...' : 'Create Transaction'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Bulk Transactions Modal */}
      <Dialog open={bulkModalOpen} onOpenChange={setBulkModalOpen}>
        <DialogTrigger asChild>
          <Button size="sm" variant="outline" className="gap-2">
            <FileSpreadsheet className="h-4 w-4" />
            Bulk Create
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Create Bulk Transactions</DialogTitle>
            <DialogDescription>
              Paste JSON data to create multiple transactions at once.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="grid gap-2">
              <Label htmlFor="bulk_data">Transaction Data (JSON Format)</Label>
              <Textarea
                id="bulk_data"
                value={bulkData}
                onChange={(e) => setBulkData(e.target.value)}
                placeholder={`[
  {
    "transaction_number": "INB-2025-100",
    "product_id": 1,
    "warehouse_id": 1,
    "quantity_change": 50,
    "transaction_type": "inbound"
  },
  ...
]`}
                rows={10}
                className="font-mono text-sm"
              />
            </div>
            <div className="text-sm text-gray-500">
              Tip: Each transaction should include transaction_number, product_id, warehouse_id, quantity_change, and transaction_type.
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setBulkModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleBulkSubmit} disabled={loading || !bulkData}>
              {loading ? 'Creating...' : 'Create Transactions'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Upload File Modal */}
      <Dialog open={uploadModalOpen} onOpenChange={setUploadModalOpen}>
        <DialogTrigger asChild>
          <Button size="sm" variant="outline" className="gap-2">
            <Upload className="h-4 w-4" />
            Upload CSV/Excel
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Upload Transactions File</DialogTitle>
            <DialogDescription>
              Upload a CSV or Excel file containing transaction data.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="grid gap-4">
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <div className="text-sm text-gray-600 mb-2">
                  Choose a CSV or Excel file to upload
                </div>
                <Input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <Label
                  htmlFor="file-upload"
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
                >
                  Choose File
                </Label>
              </div>
              <div className="text-sm text-gray-500">
                <p className="font-semibold mb-1">File Requirements:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>CSV or Excel format (.csv, .xlsx, .xls)</li>
                  <li>Headers: transaction_number, product_id, warehouse_id, quantity_change, transaction_type</li>
                  <li>Transaction types: inbound, sale, or adjustment</li>
                  <li>Maximum 1000 transactions per file</li>
                </ul>
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setUploadModalOpen(false)}>
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}