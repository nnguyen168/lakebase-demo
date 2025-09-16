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
  category?: string;
  expiration_days?: number;
  storage_temp?: string;
  allergens?: string;
  organic?: boolean;
}

interface Customer {
  customer_id: number;
  name: string;
  email: string;
  customer_type?: string;
}

interface Store {
  store_id: number;
  name: string;
  location?: string;
  type: string;
}

interface CreateOrderFormData {
  product_id: number | null;
  customer_id: number | null;
  store_id: number | null;
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
  const [stores, setStores] = useState<Store[]>([]);
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
      store_id: null,
      quantity: 1,
      requested_by: '',
      notes: '',
    });
    setValidationErrors({});
    setError(null);
  };

  const fetchDropdownData = async () => {
    try {
      // Fetch products from PostgreSQL database
      const productsResponse = await fetch('/debug/products');
      if (productsResponse.ok) {
        const productsData = await productsResponse.json();
        if (productsData.status === 'success') {
          setProducts(productsData.products);
        } else {
          throw new Error('Failed to load products from database');
        }
      } else {
        throw new Error('Failed to fetch products');
      }

      // Fetch customers from PostgreSQL database
      const customersResponse = await fetch('/debug/customers');
      if (customersResponse.ok) {
        const customersData = await customersResponse.json();
        if (customersData.status === 'success') {
          setCustomers(customersData.customers);
        } else {
          // Fallback to enhanced mock customers
          setCustomers([
            { customer_id: 1, name: 'Pacific Northwest Hotels', email: 'orders@pnwhotels.com', customer_type: 'hotel' },
            { customer_id: 2, name: 'Elite Catering Services', email: 'purchasing@elitecatering.com', customer_type: 'catering' },
            { customer_id: 3, name: 'Sunshine Restaurant Group', email: 'supply@sunshinerestaurants.com', customer_type: 'restaurant' },
          ]);
        }
      } else {
        // Fallback to enhanced mock customers
        setCustomers([
          { customer_id: 1, name: 'Pacific Northwest Hotels', email: 'orders@pnwhotels.com', customer_type: 'hotel' },
          { customer_id: 2, name: 'Elite Catering Services', email: 'purchasing@elitecatering.com', customer_type: 'catering' },
          { customer_id: 3, name: 'Sunshine Restaurant Group', email: 'supply@sunshinerestaurants.com', customer_type: 'restaurant' },
        ]);
      }

      // Fetch stores - fallback to mock data
      setStores([
        { store_id: 1, name: 'Downtown Bistro', location: 'Portland, OR', type: 'restaurant' },
        { store_id: 2, name: 'Central Food Warehouse', location: 'Portland, OR', type: 'warehouse' },
        { store_id: 3, name: 'Morning Glory Cafe', location: 'Seattle, WA', type: 'cafe' },
        { store_id: 4, name: 'Gourmet Express Food Truck', location: 'Mobile', type: 'food_truck' },
        { store_id: 5, name: 'The Garden Restaurant', location: 'San Francisco, CA', type: 'restaurant' },
      ]);
    } catch (err) {
      setError('Failed to load form data from database');
      console.error('Error fetching dropdown data:', err);
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
    
    if (!formData.store_id) {
      errors.store_id = 'Store is required';
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
          <DialogTitle>Create New Food & Beverage Order</DialogTitle>
          <DialogDescription>
            Place an order for fresh ingredients, beverages, and specialty food items.
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
                    <div className="flex flex-col space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{product.name}</span>
                        <Badge variant="outline">${product.price}/{product.unit}</Badge>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <span>SKU: {product.sku}</span>
                        {product.category && (
                          <Badge variant="secondary" className="text-xs">{product.category}</Badge>
                        )}
                        {product.organic && (
                          <Badge variant="outline" className="text-xs bg-green-50">Organic</Badge>
                        )}
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {validationErrors.product_id && (
              <p className="text-sm text-red-500">{validationErrors.product_id}</p>
            )}
            {selectedProduct && (
              <div className="text-sm text-muted-foreground space-y-1">
                <p>SKU: {selectedProduct.sku} | ${selectedProduct.price}/{selectedProduct.unit}</p>
                {selectedProduct.category && (
                  <p>Category: {selectedProduct.category}</p>
                )}
                {selectedProduct.storage_temp && (
                  <p>Storage: {selectedProduct.storage_temp}</p>
                )}
                {selectedProduct.expiration_days && (
                  <p className="text-orange-600">Shelf life: {selectedProduct.expiration_days} days</p>
                )}
                {selectedProduct.allergens && (
                  <p className="text-red-600">⚠️ Contains: {selectedProduct.allergens}</p>
                )}
              </div>
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
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{customer.name}</span>
                        {customer.customer_type && (
                          <Badge variant="outline" className="text-xs">
                            {customer.customer_type}
                          </Badge>
                        )}
                      </div>
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

          {/* Store Selection */}
          <div className="space-y-2">
            <Label htmlFor="store">Store *</Label>
            <Select
              value={formData.store_id?.toString() || ''}
              onValueChange={(value) => setFormData({ ...formData, store_id: parseInt(value) })}
            >
              <SelectTrigger className={validationErrors.store_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select a store" />
              </SelectTrigger>
              <SelectContent>
                {stores.map((store) => (
                  <SelectItem key={store.store_id} value={store.store_id.toString()}>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{store.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {store.type}
                        </Badge>
                      </div>
                      {store.location && (
                        <div className="text-sm text-muted-foreground">{store.location}</div>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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