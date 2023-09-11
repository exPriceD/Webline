$(document).on('click', '#sendFormBtn', function(e) {
    e.preventDefault();
    let promocode = $("#promocode");
    let error_text = $("#error_text");
    if (!promocode.val()) {
        error_text.html("Введите промокод");
        error_text.css('display', 'block');
        promocode.css('border', '2px solid red');
        promocode.focus(function() {
            error_text.css('display', 'none');
            promocode.css('border', '1px solid black');
        });
    }
    var form_data = new FormData();
    form_data.append('promocode', promocode.val());

    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '/write/promo',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            console.log(data);
            promocode.val('');
            e.stopPropagation();
            $("#balance").html(`Баланс: ${data["Balance"]} ₽`);
            if (data["Status"] === "Success") {
                $("#close_promo").click()
                $("#text_promo").html(`Промокод был успешно применен. Ваш баланс пополнился на сумму ${data["Amount"]} ₽`);
                const toastLiveExample = document.getElementById('liveToast-promo');
                const toast = new bootstrap.Toast(toastLiveExample);
                toast.show();
            } else if (data["Status"] === "Promo not found") {
                error_text.html("Промокод не найден");
                error_text.css('display', 'block');
                promocode.css('border', '2px solid red');
                promocode.focus(function() {
                    error_text.css('display', 'none');
                    promocode.css('border', '1px solid black');
                });
            } else if (data["Status"] === "Expired") {
                error_text.html("Срок действия промокода истек");
                error_text.css('display', 'block');
                promocode.css('border', '2px solid red');
                promocode.focus(function() {
                    error_text.css('display', 'none');
                    promocode.css('border', '1px solid black');
                });
            } else if (data["Status"] === "Already used") {
                error_text.html("Вы уже использовали данный промокод");
                error_text.css('display', 'block');
                promocode.css('border', '2px solid red');
                promocode.focus(function() {
                    error_text.css('display', 'none');
                    promocode.css('border', '1px solid black');
                });
            } else if (data["Status"] === "Used") {
                error_text.html("Промокод использован максимальное кол-во раз");
                error_text.css('display', 'block');
                promocode.css('border', '2px solid red');
                promocode.focus(function() {
                    error_text.css('display', 'none');
                    promocode.css('border', '1px solid black');
                });
            }
        }
    })
})