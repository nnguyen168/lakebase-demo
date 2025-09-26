/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedResponse_Product_ } from '../models/PaginatedResponse_Product_';
import type { Product } from '../models/Product';
import type { ProductCreate } from '../models/ProductCreate';
import type { ProductUpdate } from '../models/ProductUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProductsService {
    /**
     * Get Products
     * Get all products with optional filters and pagination metadata.
     * @param category Filter by product category
     * @param search Search in product name or SKU
     * @param limit Maximum number of products to return
     * @param offset Number of products to skip
     * @returns PaginatedResponse_Product_ Successful Response
     * @throws ApiError
     */
    public static getProductsApiProductsGet(
        category?: (string | null),
        search?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<PaginatedResponse_Product_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/products/',
            query: {
                'category': category,
                'search': search,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Product
     * Create a new product.
     * @param requestBody
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static createProductApiProductsPost(
        requestBody: ProductCreate,
    ): CancelablePromise<Product> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/products/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Product
     * Get a specific product by ID.
     * @param productId
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static getProductApiProductsProductIdGet(
        productId: number,
    ): CancelablePromise<Product> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/products/{product_id}',
            path: {
                'product_id': productId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Product
     * Update a product.
     * @param productId
     * @param requestBody
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static updateProductApiProductsProductIdPut(
        productId: number,
        requestBody: ProductUpdate,
    ): CancelablePromise<Product> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/products/{product_id}',
            path: {
                'product_id': productId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Product
     * Delete a product.
     * @param productId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteProductApiProductsProductIdDelete(
        productId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/products/{product_id}',
            path: {
                'product_id': productId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
