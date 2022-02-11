$(() => {
    Handlebars.registerHelper('eq', (value1, value2) => value1 == value2)
    Handlebars.registerHelper('split', (string, separator) => string.split(separator))
    const template = Handlebars.compile(deviceTemplate)

    var elems = document.querySelectorAll('#chart-modal');
    var instances = M.Modal.init(elems, {
        onCloseStart: Graph.hide
    });

    Graph.initialize()

    function propertyValueChanged() {
        let element = $(this)
        const data = {
            'path': element.attr('id'),
            'value': element.is("input[type='checkbox']") ? element.is(":checked") : element.val()
        }
        console.log(data)
        $.post('/set-property', JSON.stringify(data), (response) => {
            console.log(`Async call to set-property finished with response ${response}`)
        }, "json")
    }

    function chartLinkClicked(evt) {
        evt.preventDefault()
        let path = $(evt.currentTarget).data('path')
        let name = $(evt.currentTarget).data('metric-name')
        $('#chart-metric-name').text(name)
        M.Modal.getInstance($('#chart-modal')).open()
        Graph.show(path)
    }

    $.getJSON('/devices', result => {
        console.log(result)
        result.devices.forEach(device => {
            const html = template(device)
            $('#devices').append(html)
            M.AutoInit();
            $('.property-setters :input').each((index, element) => $(element).change(propertyValueChanged.deduplicate()))
            $('.chart-trigger').click(chartLinkClicked.deduplicate())
        })
    })
})
