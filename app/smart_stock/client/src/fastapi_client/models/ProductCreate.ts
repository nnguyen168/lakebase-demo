/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Model for creating a new product.
 */
export type ProductCreate = {
    name: string;
    description?: (string | null);
    sku: string;
    price: (number | string);
    unit?: string;
    category?: (string | null);
    reorder_level?: number;
};

