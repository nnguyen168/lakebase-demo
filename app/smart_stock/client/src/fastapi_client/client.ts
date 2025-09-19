import { InventoryService } from './services/InventoryService';
import { TransactionsService } from './services/TransactionsService';
import { UserService } from './services/UserService';

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
  getUserInfo: UserService.getUserInfoApiUserMeGet,
  getUserWorkspaceInfo: UserService.getUserWorkspaceInfoApiUserWorkspaceGet
};