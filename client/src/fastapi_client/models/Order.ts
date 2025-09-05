/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OrderStatus } from './OrderStatus';
/**
 * Order model with ID and timestamps.
 */
export type Order = {
    product_id: number;
    customer_id: number;
    store_id: string;
    quantity: number;
    requested_by: string;
    status?: OrderStatus;
    notes?: (string | null);
    order_id: number;
    order_number: string;
    order_date: string;
    updated_at: string;
    product_name?: (string | null);
    customer_name?: (string | null);
};

