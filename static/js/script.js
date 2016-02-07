$(document).ready(function() {

    var temp_image, first_save;

    var range_slider = $("#threshold").slider({});

    $('#image-preview').click(function (argument) {

        var formData = new FormData($('#image-upload')[0]);
        $.ajax({

            url : '/upload',
            dataType: 'json',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log(response);
                if (response['error'] == 0) {
                    temp_image = response['url'];
                    $('#temporary').attr('src', temp_image);
                    formData.append('url', temp_image);
                };
            }

        });

    });


    $('#image-submit').click(function (argument) {

        console.log(temp_image)
        $.ajax({

            url : '/generate',
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                'url': temp_image
            }),
            contentType: "application/json; charset=utf-8",
            processData: false,
            success: function(response) {
                console.log(response);
            }

        });

    });

});