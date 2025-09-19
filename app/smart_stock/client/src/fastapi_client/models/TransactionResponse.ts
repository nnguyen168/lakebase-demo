/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TransactionStatus } from './TransactionStatus';
/**
 * Response model for transaction with details.
 */
export type TransactionResponse = {
    transaction_id: number;
    transaction_number: string;
    product: string;
    quantity_change: number;
    warehouse: string;
    transaction_type: string;
    transaction_timestamp: string;
    status: TransactionStatus;
};

