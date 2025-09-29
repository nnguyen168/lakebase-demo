/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TransactionStatus } from './TransactionStatus';
/**
 * Request model for bulk status update.
 */
export type BulkStatusUpdateRequest = {
    transaction_ids: Array<number>;
    status: TransactionStatus;
};

