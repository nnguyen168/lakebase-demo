/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedResponse_Warehouse_ } from '../models/PaginatedResponse_Warehouse_';
import type { Warehouse } from '../models/Warehouse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WarehousesService {
    /**
     * Get Warehouses
     * Get all warehouses with pagination metadata.
     * @param limit Maximum number of warehouses to return
     * @param offset Number of warehouses to skip
     * @returns PaginatedResponse_Warehouse_ Successful Response
     * @throws ApiError
     */
    public static getWarehousesApiWarehousesGet(
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<PaginatedResponse_Warehouse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/warehouses/',
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Warehouse
     * Get a specific warehouse by ID.
     * @param warehouseId
     * @returns Warehouse Successful Response
     * @throws ApiError
     */
    public static getWarehouseApiWarehousesWarehouseIdGet(
        warehouseId: number,
    ): CancelablePromise<Warehouse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/warehouses/{warehouse_id}',
            path: {
                'warehouse_id': warehouseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
