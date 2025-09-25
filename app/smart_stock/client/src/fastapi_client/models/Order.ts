/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OrderStatus } from './OrderStatus';
/**
 * Order model with ID.
 */
export type Order = {
    product_id: number;
    quantity: number;
    warehouse_id: number;
    requested_by: string;
    status?: OrderStatus;
    notes?: (string | null);
    forecast_id?: (number | null);
    order_id: number;
    order_number: string;
    created_at: string;
    updated_at: string;
    product_name?: (string | null);
    product_sku?: (string | null);
    unit_price?: (string | null);
};

