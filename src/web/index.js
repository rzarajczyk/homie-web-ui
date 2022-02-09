$(() => {
    Handlebars.registerHelper('eq', (value1, value2) => value1 == value2)
    Handlebars.registerHelper('split', (string, separator) => string.split(separator))

    const template = Handlebars.compile(deviceTemplate)

    function changed() {
        let element = $(this)
        const data = {
            'path': element.attr('id'),
            'value': element.val()
        }
        $.post('/set-property', JSON.stringify(data), (response) => {
            console.log(`Async call to set-property finished with response ${response}`)
        }, "json")
    }

    $.getJSON('/devices', result => {
        console.log(result)
        result.devices.forEach(device => {
            const html = template(device)
            $('#devices').append(html)
            M.AutoInit();
            $('.property-setters :input').each((index, element) => $(element).change(changed.deduplicate()))
        })
    })
})
