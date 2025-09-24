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
import { apiClient } from '@/fastapi_client/client';

interface Product {
  product_id: number;
  name: string;
  sku: string;
  price: string; // Changed to string to match FastAPI client
  unit?: string; // Changed to optional to match FastAPI client
  category?: string | null; // Allow null to match FastAPI client
  reorder_level?: number;
}

interface CreateOrderFormData {
  product_id: number | null;
  quantity: number;
  requested_by: string;
  notes: string;
}

interface OrderData {
  order_id: number;
  order_number: string;
  product_id: number;
  quantity: number;
  requested_by: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  product_name?: string;
  product_sku?: string;
  unit_price?: string;
}

interface CreateOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOrderCreated: () => void;
  onOrderSuccess: (orderData: OrderData) => void; // New callback for successful order
  selectedItem?: any; // InventoryForecastResponse from dashboard
}

const CreateOrderModal: React.FC<CreateOrderModalProps> = ({ 
  isOpen, 
  onClose, 
  onOrderCreated,
  onOrderSuccess,
  selectedItem
}) => {
  const [formData, setFormData] = useState<CreateOrderFormData>({
    product_id: null,
    quantity: 1,
    requested_by: '',
    notes: '',
  });
  
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [userName, setUserName] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      fetchDropdownData();
      fetchUserInfo();
      resetForm();
    }
  }, [isOpen]);

  // Effect to update requested_by when userName changes
  useEffect(() => {
    console.log('userName effect triggered:', { userName, isOpen });
    if (userName && isOpen) {
      console.log('Updating form data with userName:', userName);
      setFormData(prev => ({
        ...prev,
        requested_by: userName
      }));
    }
  }, [userName, isOpen]);

  // Effect to prefill form when selectedItem is provided
  useEffect(() => {
    if (selectedItem && products.length > 0) {
      // Try to find matching product by item_id or item_name
      const matchingProduct = products.find(p => 
        p.sku === selectedItem.item_id || 
        p.name.toLowerCase().includes(selectedItem.item_name.toLowerCase())
      );
      
      if (matchingProduct) {
        setFormData(prev => ({
          ...prev,
          product_id: matchingProduct.product_id,
          quantity: Math.max(1, selectedItem.forecast_30_days || 1),
          notes: `Reorder recommendation based on forecast: ${selectedItem.action}. Current stock: ${selectedItem.stock}, 30-day forecast: ${selectedItem.forecast_30_days}`
        }));
      }
    }
  }, [selectedItem, products]);

  const resetForm = () => {
    setFormData({
      product_id: null,
      quantity: 1,
      requested_by: userName, // Pre-fill with user name
      notes: '',
    });
    setValidationErrors({});
    setError(null);
  };

  const fetchUserInfo = async () => {
    try {
      console.log('Fetching user info...');
      const userInfo = await apiClient.getUserInfo();
      console.log('User info received:', userInfo);
      if (userInfo && userInfo.displayName) {
        // Combine displayName and role if both are available
        const fullName = userInfo.displayName;
        console.log('Setting userName to:', fullName);
        setUserName(fullName);
      } else if (userInfo && userInfo.userName) {
        console.log('Setting userName to userName:', userInfo.userName);
        // If no displayName, use userName as fallback
        setUserName(userInfo.userName);
      }
    } catch (err) {
      console.warn('Could not fetch user info:', err);
      // Fallback to a default name or leave empty
      setUserName('');
    }
  };

  const fetchDropdownData = async () => {
    try {
      // Fetch products using apiClient
      try {
        const productsData = await apiClient.getProducts();
        setProducts(productsData.items);
      } catch (apiError) {
        console.warn('API client failed, trying fallback:', apiError);
        // Fallback to debug endpoint
        const debugResponse = await fetch('/debug/products');
        if (debugResponse.ok) {
          const debugData = await debugResponse.json();
          if (debugData.status === 'success') {
            setProducts(debugData.products);
          } else {
            throw new Error('Failed to load products from database');
          }
        } else {
          throw new Error('Failed to fetch products');
        }
      }
    } catch (err) {
      setError('Failed to load products from database');
      console.error('Error fetching products:', err);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.product_id) {
      errors.product_id = 'Product is required';
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
          quantity: formData.quantity,
          requested_by: formData.requested_by,
          status: 'pending',
          notes: formData.notes || null,
          forecast_id: selectedItem?.forecast_id || null, // Include forecast_id if order is based on recommendation
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create order');
      }
      
      const orderData = await response.json();
      
      // Close this modal and show success modal
      onClose();
      onOrderSuccess(orderData);
      
      // Reset form for next use
      setTimeout(() => {
        resetForm();
      }, 100);
      
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
          <DialogTitle>
            {selectedItem ? 'Create Reorder Based on Recommendation' : 'Create New Product Order'}
          </DialogTitle>
          <DialogDescription>
            {selectedItem 
              ? `Reorder recommendation for ${selectedItem.item_name} - ${selectedItem.action}`
              : 'Place an order for products based on inventory recommendations.'
            }
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
              disabled={loading}
            >
              <SelectTrigger className={`h-16 ${validationErrors.product_id ? 'border-red-500' : ''}`}>
                <SelectValue placeholder="Select a product" />
              </SelectTrigger>
              <SelectContent className="max-w-lg">
                {products.map((product) => (
                  <SelectItem key={product.product_id} value={product.product_id.toString()} className="h-20 p-4">
                    <div className="flex flex-col space-y-2 w-full">
                      <div className="flex items-center justify-between w-full">
                        <span className="font-medium text-base">{product.name}</span>
                        <Badge variant="outline" className="ml-2">${product.price}/{product.unit || 'unit'}</Badge>
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                        <span className="font-mono">SKU: {product.sku}</span>
                        {product.category && (
                          <Badge variant="secondary" className="text-xs">{product.category}</Badge>
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
                <p>SKU: {selectedProduct.sku} | ${selectedProduct.price}/{selectedProduct.unit || 'unit'}</p>
                {selectedProduct.category && (
                  <p>Category: {selectedProduct.category}</p>
                )}
                {selectedProduct.reorder_level && (
                  <p>Reorder Level: {selectedProduct.reorder_level} {selectedProduct.unit || 'unit'}</p>
                )}
              </div>
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
              disabled={loading}
            />
            {validationErrors.quantity && (
              <p className="text-sm text-red-500">{validationErrors.quantity}</p>
            )}
            {selectedProduct && formData.quantity > 0 && (
              <p className="text-sm text-muted-foreground">
                Total: ${(parseFloat(selectedProduct.price) * formData.quantity).toFixed(2)}
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
              disabled={loading}
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
              disabled={loading}
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