/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TransactionType } from './TransactionType';
/**
 * Model for creating a new transaction.
 */
export type InventoryTransactionCreate = {
    product_id: number;
    warehouse_id: number;
    quantity_change: number;
    transaction_type: TransactionType;
    notes?: (string | null);
};

