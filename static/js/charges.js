$(function () {

  /**
   * Clean up state when the modal closes
   * Hide the spinner and message if they are visible
   */
  $('#realexFormModal').on('hidden.bs.modal', function () {
    hideSpinner();
    hideMessage();
  });

  /**
   * Take control of the form submission. Prevent the default submission
   * behaviour
   */
  $('#realex-form').submit( function (e) {
    e.preventDefault();

    // Disable the button to stop the user making multiple requests before
    // completing the current one
    $('#submit-btn').prop("disabled", true);

    // Show the loading spinner
    showSpinner();

    // Charge the user with their inputted details
    createCharge();
  });

  /**
   * This function creates a realex charge request using the realex object.
   * This request will call the realexResponseHandler on completion
   * @method createCharge
   */
  function createCharge() {
    // Send a post request to the charges route
      if ($('#3d_secure').val() == '1'){
          $.post('/threedsecure', {
          card_holder_name: $('#card-holder-name').val(),
          amount: $('#amount').val(),
          card_number: $('#card-number').val(),
          cvv: $('#cvv').val(),
          card_type: $('#card-type').val(),
          currency: $('#currency').val(),
          expiry_month: $('#expiry-month').val(),
          expiry_year: $('#expiry-year').val()
        })
        .done(res => renderResponse(res))
        .fail(err => handleErrors(err.responseText))
        .always(function() {
          $('#submit-btn').prop("disabled", false);
    });
      }
    else{
        $.post('/auth', {
          card_holder_name: $('#card-holder-name').val(),
          amount: $('#amount').val(),
          card_number: $('#card-number').val(),
          cvv: $('#cvv').val(),
          card_type: $('#card-type').val(),
          currency: $('#currency').val(),
          expiry_month: $('#expiry-month').val(),
          expiry_year: $('#expiry-year').val()
        })
        .done(res => showSuccess(res))
        .fail(err => handleErrors(err.responseText))
        .always(function() {
          $('#submit-btn').prop("disabled", false);
        });
      }
  }

    function renderResponse(res) {
        if(res.message) {
            showSuccess(res);
        }
        else {
            $('#message-container').html(res);
            $('#realex-form').hide();
            $('#spinner-container').hide();
            $('#message-container').show();
        }
    };

  /**
   * Shows the user the success message from the realex_handler module
   * @method showSuccess
   * @param  {}     res     response object returned from the realex purchase
   */
  function showSuccess (res) {
    // Hide the spinner
    hideSpinner();
    // Show the user the success message
    showMessage(res.message);
  };

  /**
   * Sorts through the error retrieved from the realex charge and executes
   * the nessecary methods
   * @method handleErrors
   * @param  {}     err     error object returned from the realex charge
   */
  function handleErrors(err) {
    showMessage(err.message);
  };

  /**
   * Highlight fields with invalid params.
   * @method highlightFields
   * @return []     fields      A list of all the fields to highlight
   */
  function highlightFields(fields) {
    // Highlight specific/all fields
    fields.forEach((element) => {
      $(`#${element}`).css('border', '1px solid red');
    });

    // Hide the spinner if active
    hideSpinner();
  };

  /**
   * Retry the transaction from scratch with the users inputted details.
   * This method should inform the user that the transaction is taking longer
   * than normal/being re-tried.
   * @method retry
   */
  function retry () {
    // Set the amount to a 00 value for a success response
    $('#amount').val(1.00);

    // Wait two seconds to try and avoid any network issues
    setTimeout(() => {
      // Change the message that the user sees
      $('.payment-text').text('Just a little longer .... ');
      createCharge();
    }, 2000);

    // Put the default text back in the payment text section
    $('#payment-text').text('One moment we are processing your request ...');
  };

  /**
   * Show the spinner and hide the form
   * @method showSpinner
   */
  function showSpinner () {
    $('#spinner-container').show();
    $('#realex-form').hide();
  };

  /**
   * Hide the spinner and show the form
   * @method hideSpinner
   */
  function hideSpinner () {
    $('#spinner-container').hide();
    $('#realex-form').show();
  };

  /**
   * Show the user a message based on the error we recieve
   * @method showMessage
   * @param  string     message     The message to show the user
   */
  function showMessage(message) {
    $('#message-text').text(message);

    $('#realex-form').hide();
    $('#spinner-container').hide();
    $('#message-container').show();
  };

  /**
   * Hide the message from the user and show the form again
   * @method hideMessage
   */
  function hideMessage() {
    $('#message-container').hide();
    $('#realex-form').show();
  };
});


$(function () {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    /*
     The functions below will create a header with csrftoken
     */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});