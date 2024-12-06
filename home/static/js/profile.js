document.addEventListener('DOMContentLoaded', function () {
    // Handle search bar
    const searchBar = document.querySelector('.search-bar input');
    const searchButton = document.querySelector('.search-bar button');

    searchButton.addEventListener('click', () => {
        const query = searchBar.value.trim();
        if (query) {
            alert(`Searching for: ${query}`);
            // Redirect or process the search
        }
    });

    // Handle gender selection
    const genderInputs = document.querySelectorAll('input[name="gender"]');
    genderInputs.forEach(input => {
        input.addEventListener('change', (event) => {
            console.log(`Gender selected: ${event.target.value}`);
        });
    });

    // Handle form submission
    const form = document.querySelector('form');
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const name = document.getElementById('name').value;
        const storeName = document.getElementById('store-name').value;

        // Validate form fields
        if (!name.trim() || !storeName.trim()) {
            alert('Nama dan Nama Toko wajib diisi.');
            return;
        }

        alert(`Data berhasil disimpan untuk: ${username}`);
        // Add AJAX or Fetch API call here to submit data to the server
    });
});
