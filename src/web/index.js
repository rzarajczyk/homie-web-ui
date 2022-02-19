$(() => {
    Handlebars.registerHelper('eq', (value1, value2) => value1 == value2)
    Handlebars.registerHelper('split', (string, separator) => string.split(separator))
    const deviceTemplate = $('#device-template').html()
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

    function commandClicked() {
        let element = $(this)
        let datatype = element.data('type')
        let path = element.attr('id')
        let argname = element.data('argname')
        console.log(datatype)
        if (datatype === 'boolean') {
            commandSend(path, true)
        } else if (datatype === 'string') {
            $('#command-input-modal label').text(argname)
            $('#command-input-path').val(path)
            $('#command-input-value').val('')
            M.Modal.getInstance($('#command-input-modal')).open()
        }
    }

    function commandOkClicked() {
        let path = $('#command-input-path').val()
        let value = $('#command-input-value').val()
        commandSend(path, value)
    }

    function commandSend(path, value) {
        const data = {
            'path': path,
            'value': value
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
            $('.commands-setters a').each((index, element) => $(element).click(commandClicked.deduplicate()))
            $('.chart-trigger').click(chartLinkClicked.deduplicate())
            $('#command-input-ok').click(commandOkClicked.deduplicate())
        })
    })
})
