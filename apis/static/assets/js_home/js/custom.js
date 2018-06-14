/**
 * Created by pulkitjain on 6/13/18.
 */

function open_login(){
    $('.error-msgs').hide();
    $('.modal-section ').hide();
    $('#id_login_form')[0].reset();
    $('#id_signup_form')[0].reset();
    $('#id_forgot_password_form')[0].reset();
    $('#id_login_section').show();
    $('#login_2').modal('show');
    return false;
}

function login_user(){
    $('.error-msgs').hide();
    $.ajax({
        url: $('#id_login_form').attr('data-url'),
        type: $('#id_login_form').attr('method'),
        data: $('#id_login_form').serialize(),
        success: function(response){
            if(response.status){
                    location.reload();
            }else{
                // $('#id_login_form').html(response.data);
                for(var i=0; i<response.errors.length; i++){
                    if (response.errors[i].key == '__all__'){
                        $('#id_all_error_login').text(response.errors[i].error);
                        $('#id_all_error_login').show();
                    }else{
                        $('#id_'+response.errors[i].key+'_error_login').text(response.errors[i].error);
                        $('#id_'+response.errors[i].key+'_error_login').show();
                        $('#id_'+response.errors[i].key+'_error_parent_div_login').addClass('has-error');
                    }
                }
            }
        }
    });
    return false;
}

function signup_user(){
    $('.error-msgs').hide();
    $.ajax({
        url: $('#id_signup_form').attr('data-url'),
        type: $('#id_signup_form').attr('method'),
        data: $('#id_signup_form').serialize(),
        success: function(response){
            if(response.status){
                alert('An email has been sent to your account activation. Please click on that link to proceed');
                location.reload();
            }else{

                // $('#id_signup_form').html(response.data);

                for(var i=0; i<response.errors.length; i++){
                    if (response.errors[i].key == '__all__'){
                        $('#id_all_error_signup').text(response.errors[i].error);
                        $('#id_all_error_signup').show();
                    }else{
                        $('#id_'+response.errors[i].key+'_error_signup').text(response.errors[i].error);
                        $('#id_'+response.errors[i].key+'_error_signup').show();
                        $('#id_'+response.errors[i].key+'_error_parent_div_signup').addClass('has-error');
                    }
                }
            }
        }
    });
    return false;
}

function forgot_password_submit(){
    $('.error-msgs').hide();
    $.ajax({
        url: $('#id_forgot_password_form').attr('data-url'),
        type: $('#id_forgot_password_form').attr('method'),
        data: $('#id_forgot_password_form').serialize(),
        success: function(response){
            if(response.status){
                $('.modal-section ').hide();
                $('#id_forgot_password_success').show();
            }else{
                for(var i=0; i<response.errors.length; i++){
                    if (response.errors[i].key == '__all__'){
                        $('#id_all_error_forgot_password').text(response.errors[i].error);
                        $('#id_all_error_forgot_password').show();
                    }else{
                        $('#id_'+response.errors[i].key+'_error_forgot_password').text(response.errors[i].error);
                        $('#id_'+response.errors[i].key+'_error_forgot_password').show();
                        $('#id_'+response.errors[i].key+'_error_parent_div_forgot_password').addClass('has-error');
                    }
                }
            }
        }
    });
    return false;
}

function toggle_forgot_password() {
    $('.error-msgs').hide();
    $('.modal-section ').hide();
    $('#id_login_form')[0].reset();
    $('#id_signup_form')[0].reset();
    $('#id_forgot_password_form')[0].reset();
    $('#id_forgot_password').show();
}

function toggle_login(){
    $('.error-msgs').hide();
    $('.modal-section ').hide();
    $('#id_login_form')[0].reset();
    $('#id_signup_form')[0].reset();
    $('#id_forgot_password_form')[0].reset();
    $('#id_login_section').show();
}

function add_to_cart(item){
    $.ajax({
        url: $('#id_add_to_cart').attr('data-url'),
        type: "GET",
        data: {
            'item': item
        },
        success: function(response){
            if(response.status){
                    location.reload();
            }else{
                // $('#id_login_form').html(response.data);
                alert("A problem occured while adding item to cart. Please Try again");
            }
        }
    });

}

function decrement_to_cart(item){
    $.ajax({
        url: $('#id_dec_cart').attr('data-url'),
        type: "GET",
        data: {
            'item': item
        },
        success: function(response){
            if(response.status){
                    location.reload();
            }else{
                // $('#id_login_form').html(response.data);
                alert("A problem occured while adding item to cart. Please Try again");
            }
        }
    });
}