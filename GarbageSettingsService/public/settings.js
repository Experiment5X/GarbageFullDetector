function getPhoneNumberList() {
    var phoneNumberList = [];
    $('.phone-number').each(function() {
        phoneNumberList.push(this.innerText);
    });

    return phoneNumberList.join(':');
}

function updateNumbersToNotifyField() {
    $('input[name="numbersToNotify"]').val(getPhoneNumberList());
}

function addNumberToList(numberText, animate) {
    var $numberListItem = $('<li class="list-group-item remove-number-list-item"><span> <span class="phone-number">' + 
            numberText +
            '</span><button class="btn btn-xs btn-danger badge float-right remove-number-button" type="button">-</button>');
    if (animate) {
        $numberListItem.css('display', 'none');
    }

    $numberListItem.find('.remove-number-button').on('click', function() {
        $(this).closest('.remove-number-list-item').slideUp(300, function() {
            this.remove();

            updateNumbersToNotifyField();
        });
    });

    $numberListItem.appendTo('#numberList');
    if (animate) {
        $numberListItem.slideDown(300);
    }
}

function loadNumberListItems(initialLoad) {
    var numbersListText = $('input[name="numbersToNotify"]').val();
    var numbersList = numbersListText.split(':');

    for (var number of numbersList) {
        // don't animate the number list item being added if this is the initial load
        addNumberToList(number, !initialLoad);
    }

    updateNumbersToNotifyField();
}

function checkAndUpdateInputNumberValid() {
    var e164Regex = /^\+?[1-9]\d{1,14}$/;
    var phoneNumberText = $('#phoneNumber').val();

    if (e164Regex.test(phoneNumberText)) {
        $('#addNumberButton').prop('disabled', false);
        $('#addNumberButton').css('background-color', 'var(--success)')
    } else {
        $('#addNumberButton').prop('disabled', true);
        $('#addNumberButton').css('background-color', 'var(--light)')
    }
}

$(document).ready(function() {
    $('#addNumberButton').on('click', function() {
        this.blur();

        addNumberToList($('#phoneNumber').val(), true);
        updateNumbersToNotifyField();

        $('#phoneNumber').val('');
    });

    checkAndUpdateInputNumberValid();
    $('#phoneNumber').on('keydown', checkAndUpdateInputNumberValid);
    $('#phoneNumber').on('paste', checkAndUpdateInputNumberValid);
    $('#phoneNumber').on('change', checkAndUpdateInputNumberValid);

    loadNumberListItems(true);

    var updateInterval = 4 * 1000; // 4 seconds
    setInterval(function() {
        $.ajax({ url: '/updateGarbageImage' }).done(function(updateTimestampText) {
            $('#garbage-image').attr('src', '/images/garbage_can.png?' + new Date().getTime());
            $('.garbage-status-time').text(updateTimestampText);
        });
    }, updateInterval);
});