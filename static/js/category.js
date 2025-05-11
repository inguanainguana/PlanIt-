document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('category');
    const otherCategoryCheckbox = document.getElementById('other_category_checkbox');
    const otherCategoryContainer = document.getElementById('other_category_container');
    const otherCategoryInput = document.getElementById('other_category');

    otherCategoryCheckbox.addEventListener('change', function() {
        if (this.checked) {
            categorySelect.disabled = true;
            categorySelect.classList.add('disabled');
            otherCategoryContainer.style.display = 'block';
            categorySelect.required = false;
            otherCategoryInput.required = true;
        } else {
            categorySelect.disabled = false;
            categorySelect.classList.remove('disabled');
            otherCategoryContainer.style.display = 'none';
            categorySelect.required = true;
            otherCategoryInput.required = false;
        }
    });
});