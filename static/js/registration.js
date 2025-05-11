$(document).ready(function () {
    $('#phone_number').mask('+7(999)-999-99-99');

    function isValidField(field) {
        return field.val().trim() !== '';
    }

    $('input[type="text"], input[type="email"], input[type="password"]').on('input', function () {
        let $this = $(this);
        if (isValidField($this)) {
            $this.addClass('is-valid');
            $this.removeClass('is-invalid');
        } else {
            $this.addClass('is-invalid');
            $this.removeClass('is-valid');
        }
    });

    $('form').on('submit', function (event) {
        let formIsValid = true;
        $('input[type="text"], input[type="email"], input[type="password"]').each(function () {
            let $this = $(this);
            if (!isValidField($this)) {
                $this.addClass('is-invalid');
                $this.removeClass('is-valid');
                formIsValid = false;
            }
        });
        if (!formIsValid) {
            event.preventDefault();
        }
    });

    $(function () {
    $(".task-container").sortable({
        connectWith: ".task-container",
        update: function (event, ui) {
            var taskId = ui.item.data('task-id');
            var newStatus = $(this).closest('.column').data('status');
            $.ajax({
                url: '/task/update_status/' + taskId + '/',
                method: 'POST',
                data: {
                    'status': newStatus,
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                success: function (data) {
                    if (data.success) {
                        console.log('Статус задачи успешно обновлен.');
                    } else {
                        console.error(data.error);
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Ошибка при обновлении статуса задачи:', error);
                }
            });
        }
    }).disableSelection();

});


});

