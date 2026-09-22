import React, { useEffect, useRef, useState } from "react";
import "../styles/Pagination.css";

export const PAGE_SIZE_OPTIONS = [10, 15, 20, 25] as const;
export const DEFAULT_PAGE_SIZE = 15;

export type PaginationProps = {
  currentPage: number;
  pageSize: number;
  totalProjects: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
};

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  pageSize,
  totalProjects,
  totalPages,
  onPageChange,
  onPageSizeChange,
}) => {
  const safeTotalPages = Math.max(1, totalPages);
  const safePage = Math.min(Math.max(1, currentPage), safeTotalPages);

  const showPrev = safePage > 1;
  const showNext = safePage < safeTotalPages;
  const rangeStart = totalProjects === 0 ? 0 : (safePage - 1) * pageSize + 1;
  const rangeEnd =
    totalProjects === 0 ? 0 : Math.min(safePage * pageSize, totalProjects);

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!dropdownOpen) return;
    const handleMouseDown = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleMouseDown);
    return () => document.removeEventListener("mousedown", handleMouseDown);
  }, [dropdownOpen]);

  const handlePrev = () => {
    if (showPrev) onPageChange(safePage - 1);
  };

  const handleNext = () => {
    if (showNext) onPageChange(safePage + 1);
  };

  const handleSelectSize = (size: number) => {
    setDropdownOpen(false);
    if (size !== pageSize) onPageSizeChange(size);
  };

  return (
    <nav className="pagination" aria-label="Pagination">
      <span className="pagination-info">Results per page</span>

      <div className="pagination-size" ref={dropdownRef}>
        <button
          type="button"
          className="awc-btn awc-btn-secondary pagination-size-btn"
          onClick={() => setDropdownOpen((open) => !open)}
          aria-haspopup="menu"
          aria-expanded={dropdownOpen}
          aria-label="Page size"
        >
          {pageSize} ▾
        </button>
        {dropdownOpen && (
          <ul className="pagination-size-menu" aria-label="Page size options">
            {PAGE_SIZE_OPTIONS.map((size) => (
              <li key={size}>
                <button
                  type="button"
                  className={`pagination-size-option ${
                    size === pageSize ? "pagination-size-option-active" : ""
                  }`}
                  onClick={() => handleSelectSize(size)}
                >
                  {size}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <span className="pagination-info">
        {rangeStart}-{rangeEnd}
      </span>

      <span className="pagination-info">of</span>

      <span className="pagination-info pagination-total">{totalProjects}</span>

      <button
        type="button"
        className="awc-btn awc-btn-secondary pagination-nav-btn"
        onClick={handlePrev}
        aria-label="Previous page"
        title="Previous"
        disabled={!showPrev}
      >
        {"<"}
      </button>

      <span className="pagination-current" aria-current="page">
        {safePage} page of {safeTotalPages}
      </span>

      <button
        type="button"
        className="awc-btn awc-btn-secondary pagination-nav-btn"
        onClick={handleNext}
        aria-label="Next page"
        title="Next"
        disabled={!showNext}
      >
        {">"}
      </button>
    </nav>
  );
};

export default Pagination;
