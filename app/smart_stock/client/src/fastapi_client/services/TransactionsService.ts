/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InventoryTransaction } from '../models/InventoryTransaction';
import type { InventoryTransactionCreate } from '../models/InventoryTransactionCreate';
import type { InventoryTransactionUpdate } from '../models/InventoryTransactionUpdate';
import type { PaginatedResponse_TransactionResponse_ } from '../models/PaginatedResponse_TransactionResponse_';
import type { TransactionManagementKPI } from '../models/TransactionManagementKPI';
import type { TransactionStatus } from '../models/TransactionStatus';
import type { TransactionType } from '../models/TransactionType';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TransactionsService {
    /**
     * Get Transactions
     * Get list of inventory transactions with optional filters and pagination metadata.
     * @param status Filter by transaction status
     * @param warehouseId Filter by warehouse ID
     * @param transactionType Filter by transaction type
     * @param limit Maximum number of transactions to return
     * @param offset Number of transactions to skip
     * @returns PaginatedResponse_TransactionResponse_ Successful Response
     * @throws ApiError
     */
    public static getTransactionsApiTransactionsGet(
        status?: (TransactionStatus | null),
        warehouseId?: (number | null),
        transactionType?: (TransactionType | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<PaginatedResponse_TransactionResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/',
            query: {
                'status': status,
                'warehouse_id': warehouseId,
                'transaction_type': transactionType,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Transaction
     * Create a new inventory transaction.
     * @param requestBody
     * @returns InventoryTransaction Successful Response
     * @throws ApiError
     */
    public static createTransactionApiTransactionsPost(
        requestBody: InventoryTransactionCreate,
    ): CancelablePromise<InventoryTransaction> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/transactions/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Transaction Kpi
     * Get KPI metrics for transaction management.
     * @returns TransactionManagementKPI Successful Response
     * @throws ApiError
     */
    public static getTransactionKpiApiTransactionsKpiGet(): CancelablePromise<TransactionManagementKPI> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/kpi',
        });
    }
    /**
     * Get Transaction
     * Get a specific transaction by ID.
     * @param transactionId
     * @returns InventoryTransaction Successful Response
     * @throws ApiError
     */
    public static getTransactionApiTransactionsTransactionIdGet(
        transactionId: number,
    ): CancelablePromise<InventoryTransaction> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/{transaction_id}',
            path: {
                'transaction_id': transactionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Transaction
     * Update an existing transaction.
     * @param transactionId
     * @param requestBody
     * @returns InventoryTransaction Successful Response
     * @throws ApiError
     */
    public static updateTransactionApiTransactionsTransactionIdPut(
        transactionId: number,
        requestBody: InventoryTransactionUpdate,
    ): CancelablePromise<InventoryTransaction> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/transactions/{transaction_id}',
            path: {
                'transaction_id': transactionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Transaction
     * Cancel a transaction.
     * @param transactionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteTransactionApiTransactionsTransactionIdDelete(
        transactionId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/transactions/{transaction_id}',
            path: {
                'transaction_id': transactionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
