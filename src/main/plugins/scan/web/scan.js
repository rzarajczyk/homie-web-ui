$(() => {
    getNavigationLinks('#mobile-nav, #desktop-nav')

    M.AutoInit()

    M.Modal.init(document.querySelector('#scanning'), {
        dismissible: false
    })

    M.Modal.init(document.querySelector('#preview'), {
        dismissible: true
    })

    $.get('/scan/ready', (data) => {
        console.log('Scanner ready: ' + data.ready)
        if (data.ready) {
            $('#scan').removeAttr('disabled').html('Scan')
        } else {
            $('#scan').html('Scanner not ready')
        }
    })

    $('#scan').click(() => {
        $.post('/scan/scan', (data) => {
            console.log('done')
            $('#preview img').attr('src', data.png)
            $('#png').attr('href', data.png)
            $('#pdf').attr('href', data.pdf)
            M.Modal.getInstance(document.querySelector('#scanning')).close();
            M.Modal.getInstance(document.querySelector('#preview')).open();
        }).fail(() => {
            console.log('error')
            M.Modal.getInstance(document.querySelector('#scanning')).close();
            alert('Scanner error')
        })
    })
})
