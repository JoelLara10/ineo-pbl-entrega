// src/components/Pagination.jsx
import React from 'react';
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import './Pagination.css';

const Pagination = ({
  currentPage,
  totalPages,
  onPageChange,
  itemsPerPage,
  totalItems,
}) => {
  // Renderiza los números de página (máximo 5 visibles)
  const renderPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage + 1 < maxVisible) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          className={`pagination-page-btn ${currentPage === i ? 'active' : ''}`}
          onClick={() => onPageChange(i)}
        >
          {i}
        </button>
      );
    }
    return pages;
  };

  // Si solo hay una página, no mostramos nada
  if (totalPages <= 1) return null;

  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className="pagination-container">
      <div className="pagination-info">
        <span>
          Mostrando {startItem} - {endItem} de {totalItems}
        </span>
      </div>

      <div className="pagination-controls">
        {/* Flecha izquierda */}
        <button
          className={`pagination-arrow ${currentPage === 1 ? 'disabled' : ''}`}
          onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          <FiChevronLeft size={20} />
        </button>

        {/* Números de página */}
        {renderPageNumbers()}

        {/* Flecha derecha */}
        <button
          className={`pagination-arrow ${currentPage === totalPages ? 'disabled' : ''}`}
          onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          <FiChevronRight size={20} />
        </button>
      </div>
    </div>
  );
};

export default Pagination;