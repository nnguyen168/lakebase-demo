import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

interface Product {
  product_id: number;
  name: string;
  sku: string;
  price: number;
  unit: string;
}

interface Customer {
  customer_id: number;
  name: string;
  email: string;
}

interface CreateOrderFormData {
  product_id: number | null;
  customer_id: number | null;
  store_id: string;
  quantity: number;
  requested_by: string;
  notes: string;
}

interface CreateOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOrderCreated: () => void;
}

const CreateOrderModal: React.FC<CreateOrderModalProps> = ({ 
  isOpen, 
  onClose, 
  onOrderCreated 
}) => {
  const [formData, setFormData] = useState<CreateOrderFormData>({
    product_id: null,
    customer_id: null,
    store_id: '',
    quantity: 1,
    requested_by: '',
    notes: '',
  });
  
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      fetchDropdownData();
      resetForm();
    }
  }, [isOpen]);

  const resetForm = () => {
    setFormData({
      product_id: null,
      customer_id: null,
      store_id: '',
      quantity: 1,
      requested_by: '',
      notes: '',
    });
    setValidationErrors({});
    setError(null);
  };

  const fetchDropdownData = async () => {
    try {
      // For now, we'll use mock data since the API endpoints might not exist yet
      // In a real implementation, you would fetch from /api/products and /api/customers
      setProducts([
        { product_id: 1, name: 'Wireless Bluetooth Headphones', sku: 'WBH-001', price: 79.99, unit: 'unit' },
        { product_id: 2, name: 'USB-C Charging Cable', sku: 'USB-002', price: 19.99, unit: 'unit' },
        { product_id: 3, name: 'Smartphone Case', sku: 'SC-003', price: 24.99, unit: 'unit' },
      ]);
      
      setCustomers([
        { customer_id: 1, name: 'Electronics Plus', email: 'orders@electronicsplus.com' },
        { customer_id: 2, name: 'TechMart Inc', email: 'purchasing@techmart.com' },
        { customer_id: 3, name: 'Digital Solutions', email: 'orders@digitalsol.com' },
      ]);
    } catch (err) {
      setError('Failed to load form data');
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.product_id) {
      errors.product_id = 'Product is required';
    }
    
    if (!formData.customer_id) {
      errors.customer_id = 'Customer is required';
    }
    
    if (!formData.store_id.trim()) {
      errors.store_id = 'Store ID is required';
    }
    
    if (!formData.quantity || formData.quantity < 1) {
      errors.quantity = 'Quantity must be at least 1';
    }
    
    if (!formData.requested_by.trim()) {
      errors.requested_by = 'Requested by is required';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/orders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: formData.product_id,
          customer_id: formData.customer_id,
          store_id: formData.store_id,
          quantity: formData.quantity,
          requested_by: formData.requested_by,
          status: 'pending',
          notes: formData.notes || null,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create order');
      }
      
      onOrderCreated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create order');
    } finally {
      setLoading(false);
    }
  };

  const selectedProduct = products.find(p => p.product_id === formData.product_id);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Order</DialogTitle>
          <DialogDescription>
            Fill in the details to create a new order.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Product Selection */}
          <div className="space-y-2">
            <Label htmlFor="product">Product *</Label>
            <Select
              value={formData.product_id?.toString() || ''}
              onValueChange={(value) => setFormData({ ...formData, product_id: parseInt(value) })}
            >
              <SelectTrigger className={validationErrors.product_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select a product" />
              </SelectTrigger>
              <SelectContent>
                {products.map((product) => (
                  <SelectItem key={product.product_id} value={product.product_id.toString()}>
                    <div className="flex items-center justify-between w-full">
                      <span>{product.name}</span>
                      <Badge variant="outline" className="ml-2">${product.price}</Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {validationErrors.product_id && (
              <p className="text-sm text-red-500">{validationErrors.product_id}</p>
            )}
            {selectedProduct && (
              <p className="text-sm text-muted-foreground">
                SKU: {selectedProduct.sku} | ${selectedProduct.price}/{selectedProduct.unit}
              </p>
            )}
          </div>

          {/* Customer Selection */}
          <div className="space-y-2">
            <Label htmlFor="customer">Customer *</Label>
            <Select
              value={formData.customer_id?.toString() || ''}
              onValueChange={(value) => setFormData({ ...formData, customer_id: parseInt(value) })}
            >
              <SelectTrigger className={validationErrors.customer_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select a customer" />
              </SelectTrigger>
              <SelectContent>
                {customers.map((customer) => (
                  <SelectItem key={customer.customer_id} value={customer.customer_id.toString()}>
                    <div>
                      <div className="font-medium">{customer.name}</div>
                      <div className="text-sm text-muted-foreground">{customer.email}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {validationErrors.customer_id && (
              <p className="text-sm text-red-500">{validationErrors.customer_id}</p>
            )}
          </div>

          {/* Store ID */}
          <div className="space-y-2">
            <Label htmlFor="store_id">Store ID *</Label>
            <Input
              id="store_id"
              value={formData.store_id}
              onChange={(e) => setFormData({ ...formData, store_id: e.target.value })}
              placeholder="e.g. STORE-001"
              className={validationErrors.store_id ? 'border-red-500' : ''}
            />
            {validationErrors.store_id && (
              <p className="text-sm text-red-500">{validationErrors.store_id}</p>
            )}
          </div>

          {/* Quantity */}
          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity *</Label>
            <Input
              id="quantity"
              type="number"
              min="1"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
              className={validationErrors.quantity ? 'border-red-500' : ''}
            />
            {validationErrors.quantity && (
              <p className="text-sm text-red-500">{validationErrors.quantity}</p>
            )}
            {selectedProduct && formData.quantity > 0 && (
              <p className="text-sm text-muted-foreground">
                Total: ${(selectedProduct.price * formData.quantity).toFixed(2)}
              </p>
            )}
          </div>

          {/* Requested By */}
          <div className="space-y-2">
            <Label htmlFor="requested_by">Requested By *</Label>
            <Input
              id="requested_by"
              value={formData.requested_by}
              onChange={(e) => setFormData({ ...formData, requested_by: e.target.value })}
              placeholder="Enter your name"
              className={validationErrors.requested_by ? 'border-red-500' : ''}
            />
            {validationErrors.requested_by && (
              <p className="text-sm text-red-500">{validationErrors.requested_by}</p>
            )}
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Add any additional notes..."
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Order'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateOrderModal;