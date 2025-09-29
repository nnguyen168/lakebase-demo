import { InventoryService } from './services/InventoryService';
import { TransactionsService } from './services/TransactionsService';
import { UserService } from './services/UserService';
import { ProductsService } from './services/ProductsService';
import { WarehousesService } from './services/WarehousesService';

// Unified API client for SmartStock
export const apiClient = {
  // Inventory methods
  getInventoryForecast: InventoryService.getInventoryForecastApiInventoryForecastGet,
  getStockAlertsKpi: InventoryService.getStockAlertsKpiApiInventoryAlertsKpiGet,
  updateInventoryForecast: InventoryService.updateInventoryForecastApiInventoryForecastPut,

  // Transaction methods
  transactions: {
    getTransactions: TransactionsService.getTransactionsApiTransactionsGet,
    getTransactionKpi: TransactionsService.getTransactionKpiApiTransactionsKpiGet,
    getTransaction: TransactionsService.getTransactionApiTransactionsTransactionIdGet,
    createTransaction: TransactionsService.createTransactionApiTransactionsPost,
    updateTransaction: TransactionsService.updateTransactionApiTransactionsTransactionIdPut,
    deleteTransaction: TransactionsService.deleteTransactionApiTransactionsTransactionIdDelete,
    bulkUpdateStatus: TransactionsService.bulkUpdateStatusApiTransactionsBulkStatusPut,
  },
  // Keep backward compatibility
  getTransactions: TransactionsService.getTransactionsApiTransactionsGet,
  getTransactionKpi: TransactionsService.getTransactionKpiApiTransactionsKpiGet,
  getTransaction: TransactionsService.getTransactionApiTransactionsTransactionIdGet,
  createTransaction: TransactionsService.createTransactionApiTransactionsPost,
  updateTransaction: TransactionsService.updateTransactionApiTransactionsTransactionIdPut,
  deleteTransaction: TransactionsService.deleteTransactionApiTransactionsTransactionIdDelete,

  // User methods
  getUserInfo: UserService.getCurrentUserApiUserMeGet,
  getUserWorkspaceInfo: UserService.getUserWorkspaceInfoApiUserMeWorkspaceGet,

  // Product methods
  getProducts: ProductsService.getProductsApiProductsGet,
  getProduct: ProductsService.getProductApiProductsProductIdGet,
  createProduct: ProductsService.createProductApiProductsPost,
  updateProduct: ProductsService.updateProductApiProductsProductIdPut,
  deleteProduct: ProductsService.deleteProductApiProductsProductIdDelete,

  // Warehouse methods
  getWarehouses: WarehousesService.getWarehousesApiWarehousesGet
};