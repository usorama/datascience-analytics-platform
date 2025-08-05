/**
 * DataScience Analytics Dashboard JavaScript
 * Handles interactivity, theming, filtering, and export functionality
 */

// Global variables
let dashboardCharts = {};
let dashboardTables = {};
let currentTheme = 'light';
let filterState = {};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Initialize the dashboard
 */
function initializeDashboard() {
    console.log('Initializing DataScience Analytics Dashboard...');
    
    // Set initial theme
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    setTheme(theme, false);
    
    // Initialize components
    initializeThemeToggle();
    initializeFilters();
    
    // Hide loading screen
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
    }, 1000);
    
    // Add animations to cards
    animateCards();
    
    console.log('Dashboard initialized successfully');
}

/**
 * Initialize theme toggle functionality
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeToggle && themeIcon) {
        themeToggle.addEventListener('click', () => {
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme, true);
        });
    }
}

/**
 * Set dashboard theme
 */
function setTheme(theme, animate = false) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
    
    if (animate) {
        document.body.style.transition = 'all 0.3s ease-in-out';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }
    
    // Update all charts with new theme
    Object.keys(dashboardCharts).forEach(chartId => {
        updateChartTheme(chartId, theme);
    });
    
    localStorage.setItem('dashboard-theme', theme);
}

/**
 * Initialize chart
 */
function initChart(chartId, chartData, config) {
    try {
        const chartElement = document.getElementById(chartId);
        if (!chartElement) {
            console.error(`Chart element not found: ${chartId}`);
            return;
        }
        
        // Parse chart data if it's a string
        if (typeof chartData === 'string') {
            chartData = JSON.parse(chartData);
        }
        
        // Create chart
        Plotly.newPlot(chartId, chartData.data, chartData.layout, config);
        
        // Store chart reference
        dashboardCharts[chartId] = {
            data: chartData,
            config: config,
            element: chartElement
        };
        
        // Add resize listener
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(chartId);
        });
        
        console.log(`Chart initialized: ${chartId}`);
    } catch (error) {
        console.error(`Error initializing chart ${chartId}:`, error);
        showChartError(chartId, 'Failed to load chart');
    }
}

/**
 * Update chart theme
 */
function updateChartTheme(chartId, theme) {
    if (!dashboardCharts[chartId]) return;
    
    const chart = dashboardCharts[chartId];
    const colors = getThemeColors(theme);
    
    // Update layout colors
    const layoutUpdate = {
        'plot_bgcolor': colors.background,
        'paper_bgcolor': colors.paper,
        'font.color': colors.text,
        'xaxis.gridcolor': colors.grid,
        'xaxis.tickfont.color': colors.text,
        'xaxis.title.font.color': colors.text,
        'yaxis.gridcolor': colors.grid,
        'yaxis.tickfont.color': colors.text,
        'yaxis.title.font.color': colors.text,
        'title.font.color': colors.text
    };
    
    Plotly.relayout(chartId, layoutUpdate);
}

/**
 * Get theme colors
 */
function getThemeColors(theme) {
    if (theme === 'dark') {
        return {
            background: '#1a1a1a',
            paper: '#2d2d2d',
            text: '#ffffff',
            grid: '#404040'
        };
    } else {
        return {
            background: '#ffffff',
            paper: '#f8fafc',
            text: '#1f2937',
            grid: '#e5e7eb'
        };
    }
}

/**
 * Show chart error
 */
function showChartError(chartId, message) {
    const chartElement = document.getElementById(chartId);
    if (chartElement) {
        chartElement.innerHTML = `
            <div class="d-flex justify-content-center align-items-center h-100 text-muted">
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <p>${message}</p>
                </div>
            </div>
        `;
    }
}

/**
 * Initialize DataTable
 */
function initDataTable(tableId) {
    try {
        const tableElement = document.getElementById(tableId);
        if (!tableElement) {
            console.error(`Table element not found: ${tableId}`);
            return;
        }
        
        const searchable = tableElement.dataset.searchable === 'true';
        const sortable = tableElement.dataset.sortable === 'true';
        const paginated = tableElement.dataset.paginated === 'true';
        const pageSize = parseInt(tableElement.dataset.pageSize) || 10;
        
        const options = {
            responsive: true,
            searching: searchable,
            ordering: sortable,
            paging: paginated,
            pageLength: pageSize,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries per page",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        };
        
        const dataTable = $(tableElement).DataTable(options);
        
        // Store table reference
        dashboardTables[tableId] = {
            instance: dataTable,
            element: tableElement
        };
        
        console.log(`DataTable initialized: ${tableId}`);
    } catch (error) {
        console.error(`Error initializing DataTable ${tableId}:`, error);
    }
}

/**
 * Initialize filters
 */
function initializeFilters() {
    const filters = document.querySelectorAll('.dashboard-filter');
    
    filters.forEach(filter => {
        // Store initial values
        const filterId = filter.id || filter.dataset.filterId;
        if (filterId) {
            if (filter.type === 'range') {
                filterState[filterId] = filter.value;
                // Update slider value display
                const valueDisplay = document.getElementById(`${filterId}_value`);
                if (valueDisplay) {
                    filter.addEventListener('input', (e) => {
                        valueDisplay.textContent = e.target.value;
                        filterState[filterId] = e.target.value;
                    });
                }
            } else if (filter.dataset.filterType === 'daterange') {
                const part = filter.dataset.filterPart;
                if (!filterState[filterId]) {
                    filterState[filterId] = {};
                }
                filterState[filterId][part] = filter.value;
            } else {
                filterState[filterId] = filter.value;
            }
        }
        
        // Add change listeners
        filter.addEventListener('change', handleFilterChange);
        if (filter.type === 'text') {
            filter.addEventListener('input', debounce(handleFilterChange, 300));
        }
    });
}

/**
 * Handle filter changes
 */
function handleFilterChange(event) {
    const filter = event.target;
    const filterId = filter.id || filter.dataset.filterId;
    const filterType = filter.dataset.filterType;
    
    if (filterType === 'daterange') {
        const part = filter.dataset.filterPart;
        if (!filterState[filterId]) {
            filterState[filterId] = {};
        }
        filterState[filterId][part] = filter.value;
    } else {
        filterState[filterId] = filter.value;
    }
    
    console.log('Filter changed:', filterId, filterState[filterId]);
}

/**
 * Apply filters to dashboard components
 */
function applyFilters() {
    console.log('Applying filters:', filterState);
    
    // Show loading indicator
    showGlobalLoading(true);
    
    // Simulate filter processing (replace with actual filtering logic)
    setTimeout(() => {
        // Update charts based on filters
        Object.keys(dashboardCharts).forEach(chartId => {
            updateChartWithFilters(chartId);
        });
        
        // Update tables based on filters
        Object.keys(dashboardTables).forEach(tableId => {
            updateTableWithFilters(tableId);
        });
        
        showGlobalLoading(false);
        showNotification('Filters applied successfully', 'success');
    }, 1000);
}

/**
 * Clear all filters
 */
function clearFilters() {
    const filters = document.querySelectorAll('.dashboard-filter');
    
    filters.forEach(filter => {
        if (filter.type === 'checkbox') {
            filter.checked = false;
        } else if (filter.tagName === 'SELECT') {
            filter.selectedIndex = 0;
        } else {
            filter.value = '';
        }
    });
    
    filterState = {};
    showNotification('Filters cleared', 'info');
}

/**
 * Reset filters to default values
 */
function resetFilters() {
    const filters = document.querySelectorAll('.dashboard-filter');
    
    filters.forEach(filter => {
        const defaultValue = filter.getAttribute('data-default-value');
        if (defaultValue) {
            filter.value = defaultValue;
        } else if (filter.tagName === 'SELECT') {
            filter.selectedIndex = 0;
        } else {
            filter.value = '';
        }
    });
    
    // Reinitialize filter state
    initializeFilters();
    showNotification('Filters reset to default', 'info');
}

/**
 * Update chart with filters (placeholder implementation)
 */
function updateChartWithFilters(chartId) {
    // This is a placeholder - implement actual filtering logic based on your data
    console.log(`Updating chart ${chartId} with filters:`, filterState);
    
    // For demonstration, just refresh the chart
    refreshChart(chartId);
}

/**
 * Update table with filters (placeholder implementation)
 */
function updateTableWithFilters(tableId) {
    // This is a placeholder - implement actual filtering logic based on your data
    console.log(`Updating table ${tableId} with filters:`, filterState);
    
    if (dashboardTables[tableId]) {
        dashboardTables[tableId].instance.draw();
    }
}

/**
 * Refresh chart
 */
function refreshChart(chartId) {
    const loadingElement = document.getElementById(`loading-${chartId}`);
    const chartElement = document.getElementById(chartId);
    
    if (loadingElement && chartElement) {
        loadingElement.classList.remove('d-none');
        chartElement.style.opacity = '0.5';
        
        setTimeout(() => {
            loadingElement.classList.add('d-none');
            chartElement.style.opacity = '1';
            
            // Redraw chart
            if (dashboardCharts[chartId]) {
                Plotly.redraw(chartId);
            }
        }, 500);
    }
}

/**
 * Refresh table
 */
function refreshTable(tableId) {
    if (dashboardTables[tableId]) {
        dashboardTables[tableId].instance.ajax.reload();
    }
}

/**
 * Fullscreen chart
 */
function fullscreenChart(chartId) {
    const chart = dashboardCharts[chartId];
    if (!chart) return;
    
    // Create fullscreen modal
    const modal = document.createElement('div');
    modal.className = 'chart-fullscreen';
    modal.innerHTML = `
        <div class="chart-fullscreen-header">
            <h5 class="mb-0">Chart - Fullscreen View</h5>
            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="closeFullscreenChart()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="chart-fullscreen-body">
            <div id="${chartId}-fullscreen" class="chart-container" style="width: 100%; height: 100%;"></div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Copy chart to fullscreen
    setTimeout(() => {
        Plotly.newPlot(`${chartId}-fullscreen`, chart.data.data, {
            ...chart.data.layout,
            height: undefined,
            width: undefined
        }, chart.config);
    }, 100);
    
    // Store reference for cleanup
    modal.dataset.chartId = chartId;
}

/**
 * Close fullscreen chart
 */
function closeFullscreenChart() {
    const modal = document.querySelector('.chart-fullscreen');
    if (modal) {
        modal.remove();
    }
}

/**
 * Export chart
 */
function exportChart(chartId) {
    if (!dashboardCharts[chartId]) return;
    
    const options = {
        format: 'png',
        width: 1200,
        height: 800,
        filename: `chart-${chartId}-${new Date().toISOString().split('T')[0]}`
    };
    
    Plotly.downloadImage(chartId, options);
    showNotification('Chart exported successfully', 'success');
}

/**
 * Export table
 */
function exportTable(tableId) {
    if (!dashboardTables[tableId]) return;
    
    // Simple CSV export
    const table = dashboardTables[tableId].instance;
    const data = table.data().toArray();
    const headers = table.columns().header().toArray().map(h => h.textContent);
    
    let csv = headers.join(',') + '\n';
    data.forEach(row => {
        csv += row.join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `table-${tableId}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('Table exported successfully', 'success');
}

/**
 * Export dashboard to PDF
 */
function exportToPDF() {
    showGlobalLoading(true, 'Generating PDF...');
    
    // Use html2canvas and jsPDF for PDF export
    const element = document.body;
    
    html2canvas(element, {
        scale: 1,
        useCORS: true,
        allowTaint: true,
        height: element.scrollHeight,
        width: element.scrollWidth
    }).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgWidth = 210;
        const pageHeight = 295;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;
        let position = 0;
        
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
        
        while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
        }
        
        pdf.save(`dashboard-${new Date().toISOString().split('T')[0]}.pdf`);
        showGlobalLoading(false);
        showNotification('Dashboard exported as PDF', 'success');
    }).catch(error => {
        console.error('PDF export failed:', error);
        showGlobalLoading(false);
        showNotification('PDF export failed', 'error');
    });
}

/**
 * Export dashboard to PNG
 */
function exportToPNG() {
    showGlobalLoading(true, 'Generating PNG...');
    
    html2canvas(document.body, {
        scale: 1,
        useCORS: true,
        allowTaint: true
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = `dashboard-${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL();
        link.click();
        
        showGlobalLoading(false);
        showNotification('Dashboard exported as PNG', 'success');
    }).catch(error => {
        console.error('PNG export failed:', error);
        showGlobalLoading(false);
        showNotification('PNG export failed', 'error');
    });
}

/**
 * Show global loading indicator
 */
function showGlobalLoading(show, message = 'Loading...') {
    let loader = document.getElementById('global-loader');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.className = 'loading-screen';
            loader.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">${message}</p>
                </div>
            `;
            document.body.appendChild(loader);
        } else {
            loader.querySelector('p').textContent = message;
            loader.style.display = 'flex';
        }
    } else {
        if (loader) {
            loader.style.display = 'none';
        }
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1055; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Animate cards on load
 */
function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Decompress data if needed
 */
function decompressData(data) {
    if (window.isCompressed && typeof pako !== 'undefined') {
        try {
            const compressed = atob(data);
            const decompressed = pako.inflate(compressed, { to: 'string' });
            return JSON.parse(decompressed);
        } catch (error) {
            console.error('Failed to decompress data:', error);
            return null;
        }
    } else {
        return typeof data === 'string' ? JSON.parse(data) : data;
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + D: Toggle theme
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme, true);
    }
    
    // Ctrl/Cmd + E: Export to PDF
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportToPDF();
    }
    
    // Escape: Close fullscreen
    if (e.key === 'Escape') {
        closeFullscreenChart();
    }
});

// Handle window resize
window.addEventListener('resize', debounce(() => {
    // Resize all charts
    Object.keys(dashboardCharts).forEach(chartId => {
        Plotly.Plots.resize(chartId);
    });
    
    // Redraw DataTables
    Object.keys(dashboardTables).forEach(tableId => {
        dashboardTables[tableId].instance.columns.adjust().draw();
    });
}, 250));

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('dashboard-theme');
    if (savedTheme && savedTheme !== currentTheme) {
        setTheme(savedTheme, false);
    }
});

console.log('DataScience Analytics Dashboard JavaScript loaded successfully');