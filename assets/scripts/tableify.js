window.Tableify = class Tableify {
  constructor(selector) {
    this.table = $(selector);
    this.filters = {};
    this.currentSort = null;
    this.sortDirection = 0; // 0 for no sort, 1 for ascending, -1 for descending

    this.initialize();
  }

  initialize() {
    this.table.find("thead th").each((index, th) => {
      const colName = $(th).attr("mft-col-name");
      const colFilters = $(th).attr("mft-filters");
      const filterType = $(th).attr("mft-filter-type");

      // Add filter icon if filters are defined
      if (colFilters || filterType === "searchable" || filterType === "searchable-amount" || filterType === "normal") {
        const filterIcon = $('<i class="fa fa-filter ml-2 cursor-pointer"></i>');
        const countBadge = $('<span class="filter-count hidden ml-1 badge badge-primary"></span>');
        $(th).append(filterIcon).append(countBadge);

        $(th).addClass('cursor-pointer').on("click", () => {
          this.toggleFilter(th, colName);
        });
      }
    });

    // Initialize sorting buttons
    $('[mft-sort-by]').each((index, button) => {
      $(button).on("click", (e) => {
        e.preventDefault();
        const colName = $(button).attr("mft-sort-by");
        this.handleSortButtonClick(colName);
      });
    });
  }

  handleSortButtonClick(colName, parentId) {
    // Determine the new sort direction
    let newSortDirection;

    if (this.currentSort === colName) {
      // If the same column is clicked again, toggle the direction
      newSortDirection = this.sortDirection === 1 ? -1 : (this.sortDirection === -1 ? 0 : 1);
    } else {
      // New column is clicked, set to ascending
      newSortDirection = 1;
    }

    // Update the current sort column and direction
    this.currentSort = newSortDirection === 0 ? null : colName;
    this.sortDirection = newSortDirection;

    this.redraw(); // Redraw the table with updated sorting
  }

  redraw() {
    const rows = this.table.find("tbody tr");
    rows.show(); // Show all rows initially

    if (Object.keys(this.filters).length > 0) {
      rows.each((index, row) => {
        const isVisible = Object.keys(this.filters).every((colName) => {
          const filterType = this.table.find(`th[mft-col-name="${colName}"]`).attr("mft-filter-type") || "normal";

          // Get the index of the column
          const colIndex = this.table.find(`th[mft-col-name="${colName}"]`).index();
          const cell = $(row).find(`td:eq(${colIndex})`);

          // Get the value to check against the filter
          const cellText = cell.text();
          const cellValue = cell.attr("td-value") || cellText; // Use td-value if available
          const parsedValue = parseFloat(cellValue);

          // Perform filtering logic based on filter type
          if (filterType === "amount") {
            const maxFilter = Math.max(...this.filters[colName].map(f => parseFloat(f)));
            return parsedValue >= maxFilter;
          } else if (filterType === "searchable") {
            return cellText.toLowerCase().includes(this.filters[colName][0].toLowerCase());
          } else if (filterType === "searchable-amount") {
            const inputValue = this.filters[colName][0];

            // Handle both exact match and greater than
            if (inputValue.endsWith('+')) {
              const numericValue = parseFloat(inputValue.slice(0, -1)); // Remove '+' and parse
              return parsedValue >= numericValue; // Include equal and greater
            } else {
              const numericValue = parseFloat(inputValue); // Exact number
              return parsedValue === numericValue; // Exact match
            }
          } else {
            return this.filters[colName].some(filterValue => cellValue.includes(filterValue));
          }
        });

        if (!isVisible) {
          $(row).hide();
        }
      });
    }

    // Handle sorting if a column is selected for sorting
    if (this.currentSort) {
      const sortedRows = rows.toArray().sort((a, b) => {
        const valA = $(a).find(`td:eq(${this.table.find(`th[mft-col-name="${this.currentSort}"]`).index()})`).text();
        const valB = $(b).find(`td:eq(${this.table.find(`th[mft-col-name="${this.currentSort}"]`).index()})`).text();

        const isAmount = this.table.find(`th[mft-col-name="${this.currentSort}"]`).attr("mft-filter-type") === "amount";

        if (isAmount) {
          return (parseFloat(valA) - parseFloat(valB)) * this.sortDirection;
        } else {
          return (valA < valB ? -1 : (valA > valB ? 1 : 0)) * this.sortDirection;
        }
      });

      this.table.find("tbody").html(sortedRows);
    }

    this.updateFilterCounts();
  }

  toggleFilter(element, colName) {
    const colFilters = $(element).attr("mft-filters");
    const filterType = $(element).attr("mft-filter-type");

    // Do nothing if there are no filters or search options defined
    if (!colFilters && (filterType !== "searchable" && filterType !== "searchable-amount" && filterType !== "normal")) {
      return;
    }

    let dropdown = $(element).find('.filter-dropdown');
    if (dropdown.length === 0) {
      dropdown = $('<div class="filter-dropdown absolute bg-base-300 shadow-md rounded-md p-2 mt-1 hidden z-50"></div>');

      // Handle different filter types
      if (filterType === "normal" && colFilters) {
        const filters = colFilters.split(",");
        filters.forEach((filter) => {
          const checkbox = $(`<label class="flex items-center">
                              <input type="checkbox" value="${filter}" class="mr-2" />
                              ${filter}
                            </label>`);
          checkbox.on("change", (e) => {
            e.stopPropagation(); // Prevent closing on checkbox interaction
            this.updateFilter(colName, filter, checkbox.find('input').is(":checked"));
          });
          dropdown.append(checkbox);
        });
      } else if (filterType === "searchable") {
        // Create search input for searchable columns
        const searchInput = $(`<input type="text" class="input input-bordered w-full input-sm" placeholder="Search..." />`);
        searchInput.on("input", (e) => {
          e.stopPropagation(); // Prevent closing on typing
          const searchValue = searchInput.val();
          if (searchValue) {
            this.filters[colName] = [searchValue];
          } else {
            delete this.filters[colName];
          }
          this.redraw();
        });
        dropdown.append(searchInput);
      } else if (filterType === "searchable-amount") {
        // Create numeric input for searchable-amount columns
        const amountInput = $(`<input type="text" class="input input-bordered w-full input-sm" placeholder="Enter amount or amount+ for greater..." />`);
        amountInput.on("input", (e) => {
          e.stopPropagation(); // Prevent closing on typing
          const amountValue = amountInput.val();

          if (amountValue) {
            this.filters[colName] = [amountValue]; // Store as is
          } else {
            delete this.filters[colName]; // Remove if empty
          }

          this.redraw();
        });
        dropdown.append(amountInput);
      }

      $(element).append(dropdown); // Append the new dropdown to the column header

      // Prevent dropdown from closing when clicking inside
      dropdown.on("click", (e) => {
        e.stopPropagation(); // Prevent propagation of clicks within the dropdown
      });
    }

    // Toggle dropdown visibility
    dropdown.toggleClass('hidden');

    // Close dropdown when clicking outside
    const handleClickOutside = (e) => {
      if (!$(e.target).closest(dropdown).length && !$(e.target).closest(element).length) {
        dropdown.addClass('hidden');
        $(document).off('click', handleClickOutside); // Remove event listener when dropdown is closed
      }
    };

    $(document).on('click', handleClickOutside); // Attach event listener to close dropdown when clicking outside
  }

  updateFilter(colName, value, checked) {
    if (!this.filters[colName]) this.filters[colName] = [];

    if (checked) {
      if (!this.filters[colName].includes(value)) {
        this.filters[colName].push(value);
      }
    } else {
      this.filters[colName] = this.filters[colName].filter((val) => val !== value);
      if (this.filters[colName].length === 0) delete this.filters[colName];
    }

    this.redraw();
  }

  updateFilterCounts() {
    this.table.find("thead th").each((index, th) => {
      const colName = $(th).attr("mft-col-name");
      const count = this.filters[colName] ? this.filters[colName].length : 0;
      $(th).find('.filter-count').text(count).toggleClass('hidden', count === 0);
    });
  }
}
