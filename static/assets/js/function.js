console.log("working fine");

const monthsName = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];


$("#commentForm").submit(function (e) {
    e.preventDefault();

    let dt = new Date();
    let time = dt.getDate() + " " + monthsName[dt.getUTCMonth()] + ", " + dt.getFullYear();

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function (res) {
            console.log("Comment saved to DB");

            if (res.bool == true) {
                $("#review-res").html("Review added successfully");
                $(".hide-comment-form").hide();
                $(".add-review").hide();

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                _html += '<div class="user justify-content-between d-flex" >'
                _html += '<div class="thumb text-center">'
                _html += '<img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png" alt="" />'
                _html += '<a href="#" class="font-heading text-brand">' + res.context.user + '</a>'
                _html += '</div>'

                _html += '<div class="desc">'
                _html += '<div class="d-flex justify-content-between mb-10">'
                _html += '<div class="d-flex align-items-center">'
                _html += '<span class="font-xs text-muted">' + time + '</span>'
                _html += '</div>'

                for (let i = 1; i <= res.context.rating; i++) {
                    _html += '<i class="fa fa-star text-warning"></i>'
                }

                _html += '</div>'
                _html += '<p class="mb-10">' + res.context.review + '</p>'

                _html += '</div>'
                _html += '</div >'
                _html += '</div >'

                // dynamically add new content to a list or container without refreshing the page
                $(".comment-list").prepend(_html);
            }

        },
    });
});




$(document).ready(function () {
    $(".filter-checkbox").on("click", function () {
        console.log("A checkbox have been clicked ");

        let filter_object = {}

        $(".filter-checkbox").each(function () {
            let filter_value = $(this).val()
            let filter_key = $(this).data("filter") // vendor , category

            //console.log("Filter value is:", filter_value);
            //console.log("Filter key is:", filter_key);

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')).map(function (element) {
                return element.value
            })

        })
        console.log("Filter Object is: ", filter_object);
        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType: 'json',
            beforeSend: function () {
                console.log("Trying to filter product...");
            },
            success: function (response) {
                console.log(response);
                console.log("Data filtered sucessfully...");
                $("#filtered-product").html(response.data)
            }
        })
    })
    $("#max_price").on("blur", function () {
        let min_price = $(this).attr("min");
        let max_price = $(this).attr("max");
        let current_price = $(this).val();

        // console.log("Current price is: ", current_price);
        // console.log("Max price is: ", max_price);
        // console.log("Min price is: ", min_price);

        if (current_price < parseInt(min_price) || current_price > parseInt(max_price)) {
            // console.log("Price error occured");

            //  round decimal numbers to 2 decimal places
            min_Price = Math.round(min_price * 100) / 100;
            max_Price = Math.round(max_price * 100) / 100;


            // console.log("Min price is: ", min_Price);
            // console.log("Max price is: ", max_Price);

            alert("Price must be between: $" + min_Price + " and $" + max_Price);
            $(this).val(min_price);
            $("#range").val(min_price);

            $(this).focus(); // focus on the input field

            return false;
        }
    });
});