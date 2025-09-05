/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Order } from '../models/Order';
import type { OrderCreate } from '../models/OrderCreate';
import type { OrderManagementKPI } from '../models/OrderManagementKPI';
import type { OrderResponse } from '../models/OrderResponse';
import type { OrderStatus } from '../models/OrderStatus';
import type { OrderUpdate } from '../models/OrderUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OrdersService {
    /**
     * Get Orders
     * Get list of orders with optional filters.
     * @param status Filter by order status
     * @param storeId Filter by store ID
     * @param limit Maximum number of orders to return
     * @param offset Number of orders to skip
     * @returns OrderResponse Successful Response
     * @throws ApiError
     */
    public static getOrdersApiOrdersGet(
        status?: (OrderStatus | null),
        storeId?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<OrderResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/',
            query: {
                'status': status,
                'store_id': storeId,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Order
     * Create a new order.
     * @param requestBody
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static createOrderApiOrdersPost(
        requestBody: OrderCreate,
    ): CancelablePromise<Order> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/orders/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Order Kpi
     * Get KPI metrics for order management.
     * @returns OrderManagementKPI Successful Response
     * @throws ApiError
     */
    public static getOrderKpiApiOrdersKpiGet(): CancelablePromise<OrderManagementKPI> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/kpi',
        });
    }
    /**
     * Get Order
     * Get a specific order by ID.
     * @param orderId
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static getOrderApiOrdersOrderIdGet(
        orderId: number,
    ): CancelablePromise<Order> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/{order_id}',
            path: {
                'order_id': orderId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Order
     * Update an existing order.
     * @param orderId
     * @param requestBody
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static updateOrderApiOrdersOrderIdPut(
        orderId: number,
        requestBody: OrderUpdate,
    ): CancelablePromise<Order> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/orders/{order_id}',
            path: {
                'order_id': orderId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Order
     * Delete an order (soft delete by setting status to cancelled).
     * @param orderId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteOrderApiOrdersOrderIdDelete(
        orderId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/orders/{order_id}',
            path: {
                'order_id': orderId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
