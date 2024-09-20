window.handleBankDetailsDropdown = function(event) {
    const targetId = event.detail.target.id;
    
    if (targetId === 'bank-details-dropdown') {
        // Get the JSON response
        const response = JSON.parse(event.detail.xhr.responseText);

        // Clear the dropdown content first
        const dropdown = document.getElementById('bank-details-dropdown');
        dropdown.innerHTML = '';

        // Check if the response is successful and contains bank details
        if (response.status === 'success' && response.bank_details.length > 0) {
            response.bank_details.forEach(function (bank_detail) {
                // Create a new list item for each bank detail
                const li = document.createElement('li');
                li.classList.add('p-2', 'hover:bg-gray-200', 'flex', 'flex-row', 'justify-between', 'items-center', 'cursor-pointer');

                // Set the bank detail as data attributes for the dropdown item
                const detailDiv = document.createElement('div');
                detailDiv.classList.add('flex', 'flex-col', 'items-start');
                detailDiv.setAttribute('data-account-holder-name', bank_detail.account_holder_name);
                detailDiv.setAttribute('data-account-number', bank_detail.account_number);
                detailDiv.setAttribute('data-sort-code', bank_detail.sort_code);

                // Set the inner HTML with bank details
                detailDiv.innerHTML = `
                    <span class="font-semibold">${bank_detail.account_holder_name}</span>
                    <span class="text-sm text-gray-500">Account Number: ${bank_detail.account_number}</span>
                    <span class="text-sm text-gray-500">Sort Code: ${bank_detail.sort_code}</span>
                `;

                // Add an event listener to populate form fields when clicked
                li.addEventListener('click', function () {
                    document.querySelector('input[name="account_holder_name"]').value = bank_detail.account_holder_name;
                    document.querySelector('input[name="account_number"]').value = bank_detail.account_number;
                    document.querySelector('input[name="sort_code"]').value = bank_detail.sort_code;

                    // Recheck the fields to enable/disable the save button
                    checkFieldsFilled();

                    dropdown.classList.add('opacity-0');
                    setTimeout(() => {
                        dropdown.style.display = 'none';
                    }, 0); 
                });

                // Create the delete icon and handle delete request with fetch
                const deleteIcon = document.createElement('div');
                deleteIcon.innerHTML = '<i class="fa fa-trash text-red-500"></i>';
                deleteIcon.classList.add('ml-4', 'cursor-pointer');

                deleteIcon.addEventListener('click', function (e) {
                    e.stopPropagation();
                    // Send a fetch request to delete the bank detail
                    fetch(`/api/invoices/delete_bank_detail/${bank_detail.id}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Remove the deleted item from the dropdown
                            li.remove();
                            console.log('Bank detail deleted successfully');
                        } else {
                            console.error('Error deleting bank detail:', data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting bank detail:', error);
                    });
                });

                // Append both the details div and delete icon to the list item
                li.appendChild(detailDiv);
                li.appendChild(deleteIcon);

                // Append the new list item to the dropdown
                dropdown.appendChild(li);
            });

            dropdown.style.display = 'block';
            dropdown.classList.remove('opacity-0');
        } else {
            // Show a message if no bank details are available
            dropdown.innerHTML = '<li class="p-2">No saved bank details found</li>';
        }
    }
};