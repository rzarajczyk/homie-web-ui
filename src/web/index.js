$(() => {
    const template = Handlebars.compile(deviceTemplate)
    $.getJSON('/devices', result => {
        console.log(result)
        result.devices.forEach(device => {
            const html = template(device)
            $('#devices').append(html)
        })
    })
})
