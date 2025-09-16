/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TransactionStatus } from './TransactionStatus';
import type { TransactionType } from './TransactionType';
/**
 * Inventory transaction model with ID.
 */
export type InventoryTransaction = {
    product_id: number;
    warehouse_id: number;
    quantity_change: number;
    transaction_type: TransactionType;
    status?: TransactionStatus;
    notes?: (string | null);
    transaction_id: number;
    transaction_number: string;
    transaction_timestamp: string;
    updated_at: string;
    product_name?: (string | null);
    warehouse_name?: (string | null);
};

