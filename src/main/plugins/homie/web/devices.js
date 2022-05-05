$(() => {
    getNavigationLinks('#mobile-nav, #desktop-nav')

    const deviceTemplate = Handlebars.compile($('#device-template').html())
    const propertiesTemplate = Handlebars.compile($('#properties-template').html())

    Handlebars.registerHelper('eq', (value1, value2) => value1 == value2)
    Handlebars.registerHelper('split', (string, separator) => string.split(separator))
    Handlebars.registerHelper('and', (value1, value2) => value1 && value2)
    Handlebars.registerHelper('isLongerThen', (string, len) => string != null && string.length > len)
    Handlebars.registerHelper('min', (string) => string == null || string.indexOf(':') < 0 ? -1000000 : string.substring(0, string.indexOf(':')))
    Handlebars.registerHelper('max', (string) => string == null || string.indexOf(':') < 0 ? 1000000 : string.substring(string.indexOf(':') + 1))
    Handlebars.registerHelper('tooltip', (string) => formatTooltip(string))
    Handlebars.registerPartial('properties', propertiesTemplate)


    M.Modal.init(document.querySelectorAll('#chart-modal'), {
        onCloseStart: Graph.hide
    });

    Graph.initialize()

    const commandInputValue = $('#command-input-value')
    $('#command-default').change(() => commandInputValue.val($('#command-default').val()))
    $('#command-bri').change(() => commandInputValue.val($('#command-bri').val() + "," + $('#command-bri-time').val()))
    $('#command-bri-time').change(() => commandInputValue.val($('#command-bri').val() + "," + $('#command-bri-time').val()))
    $('#command-ct').change(() => commandInputValue.val($('#command-ct').val() + "," + $('#command-ct-time').val()))
    $('#command-ct-time').change(() => commandInputValue.val($('#command-ct').val() + "," + $('#command-ct-time').val()))

    function propertyValueChanged() {
        let element = $(this)
        const data = {
            'path': element.attr('id'),
            'value': element.is("input[type='checkbox']") ? element.is(":checked") : element.val()
        }
        console.log(data)
        $.post('/homie/set-property', JSON.stringify(data), (response) => {
            console.log(`Async call to set-property finished with response ${response}`)
        }, "json")
    }

    function commandClicked() {
        let element = $(this)
        let datatype = element.data('type')
        let format = element.data('format')
        let path = element.attr('id')
        let argname = element.data('argname')
        if (datatype === 'boolean') {
            commandSend(path, true)
        } else if (datatype === 'string') {
            $('#command-default-label').text(argname)
            $('#command-input-path').val(path)
            $('#command-input-value').val('')
            $('.modal-form').hide()
            if (format === '$color-temperature-transition') {
                $('#form-color-temperature').show()
            } else if (format === '$brightness-transition') {
                $('#form-brightness').show()
            } else {
                $('#form-default').show()
            }
            M.Modal.getInstance($('#command-input-modal')).open()
        }
    }

    function commandOkClicked() {
        let path = $('#command-input-path').val()
        let value = $('#command-input-value').val()
        commandSend(path, value)
        // console.log(`${path} = ${value}`)
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

    function formatTooltip(string) {
        string = string.trim()
        if (string.indexOf('[') === 0 && string.indexOf(']') === string.length - 1) {
            let parts = string.substring(1, string.length - 1).split(',')
            return `<ul>${parts.map(it => `<li>${it}</li>`).join('')}</ul>`
        }
        return string
    }

    $.getJSON('/homie/devices', result => {
        console.log(result)
        const html = deviceTemplate(result.devices)
        $('#devices').html(html)
        M.AutoInit();
        M.Collapsible.init(document.querySelectorAll('#main-collapsible'), {
            accordion: false
        });
        initComponentsAfterUpdate()
        $('.property-setters :input').each((index, element) => $(element).change(propertyValueChanged.deduplicate()))
        $('.commands-setters a').each((index, element) => $(element).click(commandClicked.deduplicate()))
        $('#command-input-ok').click(commandOkClicked.deduplicate())

        setInterval(update, 5000)
    })

    function update() {
        $.getJSON('/homie/devices', result => {
            console.log(result)
            result.devices.forEach(device => {
                let html = propertiesTemplate(device)
                $(`#device-${device.id} .properties`).html(html)
            })
            initComponentsAfterUpdate()
        })
    }

    function initComponentsAfterUpdate() {
        M.Tooltip.init(document.querySelectorAll('.tooltipped'), {
            html: true
        })
        $('.chart-trigger').click(chartLinkClicked.deduplicate())
    }
})