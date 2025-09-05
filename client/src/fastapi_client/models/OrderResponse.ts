/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OrderStatus } from './OrderStatus';
/**
 * Response model for order with product details.
 */
export type OrderResponse = {
    order_id: number;
    order_number: string;
    product: string;
    quantity: number;
    store: string;
    requested_by: string;
    order_date: string;
    status: OrderStatus;
};

