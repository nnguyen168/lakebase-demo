import { InventoryService } from './services/InventoryService';
import { TransactionsService } from './services/TransactionsService';
import { UserService } from './services/UserService';
import { ProductsService } from './services/ProductsService';

// Unified API client for SmartStock
export const apiClient = {
  // Inventory methods
  getInventoryForecast: InventoryService.getInventoryForecastApiInventoryForecastGet,
  getStockAlertsKpi: InventoryService.getStockAlertsKpiApiInventoryAlertsKpiGet,
  updateInventoryForecast: InventoryService.updateInventoryForecastApiInventoryForecastPut,

  // Transaction methods
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
  deleteProduct: ProductsService.deleteProductApiProductsProductIdDelete
};