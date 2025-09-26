/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OrderStatus } from './OrderStatus';
/**
 * Model for updating an order.
 */
export type OrderUpdate = {
    status?: (OrderStatus | null);
    quantity?: (number | null);
    notes?: (string | null);
};

