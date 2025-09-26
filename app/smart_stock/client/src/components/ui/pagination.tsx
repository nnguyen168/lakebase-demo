import React from 'react';
import { Button } from '@/components/ui/button';
import { 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight 
} from 'lucide-react';

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

interface PaginationProps {
  pagination: PaginationMeta;
  onPageChange: (offset: number, limit: number) => void;
  showPageSize?: boolean;
  pageSizeOptions?: number[];
}

export const Pagination: React.FC<PaginationProps> = ({
  pagination,
  onPageChange,
  showPageSize = true,
  pageSizeOptions = [10, 25, 50, 100]
}) => {
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const startItem = pagination.offset + 1;
  const endItem = Math.min(pagination.offset + pagination.limit, pagination.total);

  const goToFirstPage = () => {
    onPageChange(0, pagination.limit);
  };

  const goToPreviousPage = () => {
    const newOffset = Math.max(0, pagination.offset - pagination.limit);
    onPageChange(newOffset, pagination.limit);
  };

  const goToNextPage = () => {
    const newOffset = pagination.offset + pagination.limit;
    onPageChange(newOffset, pagination.limit);
  };

  const goToLastPage = () => {
    const lastPageOffset = Math.floor((pagination.total - 1) / pagination.limit) * pagination.limit;
    onPageChange(lastPageOffset, pagination.limit);
  };

  const handlePageSizeChange = (newLimit: number) => {
    // Maintain the same relative position when changing page size
    const currentItemIndex = pagination.offset;
    const newOffset = Math.floor(currentItemIndex / newLimit) * newLimit;
    onPageChange(newOffset, newLimit);
  };

  const generatePageNumbers = () => {
    const pages: number[] = [];
    const maxVisiblePages = 7;
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show smart pagination with ellipsis
      if (currentPage <= 4) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push(-1); // Ellipsis
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1);
        pages.push(-1); // Ellipsis
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push(-1); // Ellipsis
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push(-1); // Ellipsis
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  if (pagination.total === 0) {
    return (
      <div className="flex items-center justify-between px-2 py-3 text-sm text-gray-500">
        No items found
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between px-2 py-3 border-t">
      <div className="flex items-center space-x-4">
        <div className="text-sm text-gray-500">
          Showing {startItem.toLocaleString()} to {endItem.toLocaleString()} of {pagination.total.toLocaleString()} items
        </div>
        
        {showPageSize && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Items per page:</span>
            <select
              value={pagination.limit}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {pageSizeOptions.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-1">
        <Button
          variant="outline"
          size="sm"
          onClick={goToFirstPage}
          disabled={!pagination.has_prev}
          className="p-2"
          title="First page"
        >
          <ChevronsLeft className="h-4 w-4" />
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          onClick={goToPreviousPage}
          disabled={!pagination.has_prev}
          className="p-2"
          title="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <div className="flex items-center space-x-1 mx-2">
          {generatePageNumbers().map((page, index) => (
            page === -1 ? (
              <span key={`ellipsis-${index}`} className="px-2 py-1 text-gray-400">
                ...
              </span>
            ) : (
              <Button
                key={page}
                variant={page === currentPage ? "default" : "outline"}
                size="sm"
                onClick={() => {
                  const newOffset = (page - 1) * pagination.limit;
                  onPageChange(newOffset, pagination.limit);
                }}
                className="px-3 py-1 min-w-[2.5rem]"
              >
                {page}
              </Button>
            )
          ))}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={goToNextPage}
          disabled={!pagination.has_next}
          className="p-2"
          title="Next page"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          onClick={goToLastPage}
          disabled={!pagination.has_next}
          className="p-2"
          title="Last page"
        >
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default Pagination;
