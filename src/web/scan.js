$(() => {
    M.AutoInit()

    M.Modal.init(document.querySelector('#scanning'), {
        dismissible: false
    })

    M.Modal.init(document.querySelector('#preview'), {
        dismissible: true
    })

    $('#scan').click(() => {
        $.post('/scan', (data) => {
            console.log('done')
            $('#preview img').attr('src', data.png)
            $('#png').attr('href', data.png)
            $('#pdf').attr('href', data.pdf)
            M.Modal.getInstance(document.querySelector('#scanning')).close();
            M.Modal.getInstance(document.querySelector('#preview')).open();
        })
    })
})
