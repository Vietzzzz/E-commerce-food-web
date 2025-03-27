console.log("working fine");

$("#commentForm").submit(function (e) {
    e.preventDefault();

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
                _html += '< div class="user justify-content-between d-flex" >'
                _html += '<div class="thumb text-center">'
                _html += '<img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png" alt="" />'
                _html += '<a href="#" class="font-heading text-brand">{{r.user.username|title}}</a>'
                _html += '</div>'

                _html += '<div class="desc">'
                _html += '<div class="d-flex justify-content-between mb-10">'
                _html += '<div class="d-flex align-items-center">'
                _html += '<span class="font-xs text-muted">{{r.date|date:"d M, Y"}}</span>'
                _html += '</div>'

                _html += '<div class="product-rate d-inline-block">'
                _html += '<div class="product-rating" style="width: 100%"></div>'
                _html += '</div>'
                _html += '</div>'
                _html += '<p class="mb-10">' + res.context.review + '</p>'

                _html += '</div>'
                _html += '</div >'
                _html += '</div >'
            }
        },
    });
});
