/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TransactionStatus } from './TransactionStatus';
/**
 * Model for updating a transaction.
 */
export type InventoryTransactionUpdate = {
    status?: (TransactionStatus | null);
    quantity_change?: (number | null);
    notes?: (string | null);
};

