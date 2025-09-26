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
import { AlertCircle, Info } from 'lucide-react';

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

interface EditOrderFormData {
  quantity: number;
  status: string;
  notes: string;
}

interface EditOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOrderUpdated: () => void;
  order: OrderData | null;
}

const orderStatuses = [
  { value: 'pending', label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'approved', label: 'Approved', color: 'bg-blue-100 text-blue-800' },
  { value: 'shipped', label: 'Shipped', color: 'bg-purple-100 text-purple-800' },
  { value: 'delivered', label: 'Delivered', color: 'bg-green-100 text-green-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
];

const EditOrderModal: React.FC<EditOrderModalProps> = ({
  isOpen,
  onClose,
  onOrderUpdated,
  order,
}) => {
  const [formData, setFormData] = useState<EditOrderFormData>({
    quantity: 0,
    status: '',
    notes: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen && order) {
      setFormData({
        quantity: order.quantity,
        status: order.status,
        notes: '', // We don't have notes in the current order data structure
      });
      setValidationErrors({});
      setError(null);
    }
  }, [isOpen, order]);

  const getStatusTransitions = (currentStatus: string): string[] => {
    const statusFlow = {
      'pending': ['pending', 'approved', 'cancelled'],
      'approved': ['approved', 'shipped', 'cancelled'],
      'shipped': ['shipped', 'delivered'],
      'delivered': ['delivered'],
      'cancelled': ['cancelled'],
    };
    
    return statusFlow[currentStatus as keyof typeof statusFlow] || [currentStatus];
  };

  const canEditQuantity = (status: string): boolean => {
    return ['pending', 'approved'].includes(status);
  };

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'approved':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'shipped':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'delivered':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.quantity || formData.quantity < 1) {
      errors.quantity = 'Quantity must be at least 1';
    }
    
    if (!formData.status) {
      errors.status = 'Status is required';
    }
    
    // Business rule validation
    if (order) {
      const allowedStatuses = getStatusTransitions(order.status);
      if (!allowedStatuses.includes(formData.status)) {
        errors.status = `Cannot change status from ${order.status} to ${formData.status}`;
      }
      
      // Prevent quantity changes for shipped/delivered orders
      if (!canEditQuantity(order.status) && formData.quantity !== order.quantity) {
        errors.quantity = `Cannot change quantity for ${order.status} orders`;
      }
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!order || !validateForm()) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const updateData: any = {};
      
      // Only send changed fields
      if (formData.status !== order.status) {
        updateData.status = formData.status;
      }
      
      if (canEditQuantity(order.status) && formData.quantity !== order.quantity) {
        updateData.quantity = formData.quantity;
      }
      
      if (formData.notes.trim()) {
        updateData.notes = formData.notes;
      }
      
      // If no changes, just close the modal
      if (Object.keys(updateData).length === 0) {
        onClose();
        return;
      }
      
      const response = await fetch(`/api/orders/${order.order_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to update order');
      }
      
      onOrderUpdated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update order');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!order) return;
    
    if (confirm('Are you sure you want to cancel this order? This action cannot be undone.')) {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`/api/orders/${order.order_id}`, {
          method: 'DELETE',
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to cancel order');
        }
        
        onOrderUpdated();
        onClose();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to cancel order');
      } finally {
        setLoading(false);
      }
    }
  };

  if (!order) return null;

  const allowedStatuses = getStatusTransitions(order.status);
  const quantityEditable = canEditQuantity(order.status);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Edit Order {order.order_number}</DialogTitle>
          <DialogDescription>
            Update order details. Some fields may be restricted based on current status.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Order Information (Read-only) */}
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Product:</span> {order.product}
              </div>
              <div>
                <span className="font-medium">Store:</span> {order.store}
              </div>
              <div>
                <span className="font-medium">Requested by:</span> {order.requested_by}
              </div>
              <div>
                <span className="font-medium">Order Date:</span>{' '}
                {new Date(order.order_date).toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Status */}
          <div className="space-y-2">
            <Label htmlFor="status">Status *</Label>
            <Select
              value={formData.status}
              onValueChange={(value) => setFormData({ ...formData, status: value })}
            >
              <SelectTrigger className={validationErrors.status ? 'border-red-500' : ''}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {allowedStatuses.map((statusValue) => {
                  const statusConfig = orderStatuses.find(s => s.value === statusValue);
                  return (
                    <SelectItem key={statusValue} value={statusValue}>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(statusValue)} variant="secondary">
                          {statusConfig?.label || statusValue}
                        </Badge>
                        {statusValue === order.status && (
                          <span className="text-xs text-muted-foreground">(current)</span>
                        )}
                      </div>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
            {validationErrors.status && (
              <p className="text-sm text-red-500">{validationErrors.status}</p>
            )}
            {order.status !== formData.status && (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Changing status from <Badge variant="outline">{order.status}</Badge> to{' '}
                  <Badge variant="outline">{formData.status}</Badge>
                </AlertDescription>
              </Alert>
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
              disabled={!quantityEditable}
            />
            {validationErrors.quantity && (
              <p className="text-sm text-red-500">{validationErrors.quantity}</p>
            )}
            {!quantityEditable && (
              <p className="text-xs text-muted-foreground">
                Quantity cannot be changed for {order.status} orders
              </p>
            )}
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Update Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Add notes about this update..."
              rows={3}
            />
          </div>

          <DialogFooter className="flex flex-col sm:flex-row gap-2">
            {order.status !== 'cancelled' && order.status !== 'delivered' && (
              <Button 
                type="button" 
                variant="destructive" 
                onClick={handleCancel} 
                disabled={loading}
                className="w-full sm:w-auto"
              >
                Cancel Order
              </Button>
            )}
            <div className="flex gap-2 flex-1 sm:flex-initial">
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                Close
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Updating...' : 'Update Order'}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EditOrderModal;