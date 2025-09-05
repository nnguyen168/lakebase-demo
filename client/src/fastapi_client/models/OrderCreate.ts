/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OrderStatus } from './OrderStatus';
/**
 * Model for creating a new order.
 */
export type OrderCreate = {
    product_id: number;
    customer_id: number;
    store_id: string;
    quantity: number;
    requested_by: string;
    status?: OrderStatus;
    notes?: (string | null);
};

