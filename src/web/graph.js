function encodeQueryData(data) {
    const ret = [];
    for (let d in data)
        ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
    return ret.join('&');
}

const Graph = {
    is_visible: false,
    history_amount: null,
    history_units: null,
    path: "",

    initialize: function () {
        $(window).resize(Graph.onResize.deduplicate(200))
        $('#chart-history-amount').change(Graph.onHistoryChange.deduplicate(200))
        $('#chart-history-units').change(Graph.onHistoryChange.deduplicate(200))
        Graph.history_amount = $('#chart-history-amount').val()
        Graph.history_units = $('#chart-history-units').val()
    },

    onResize: function () {
        Graph.rerender()
    },

    onHistoryChange: function () {
        let minutes = $('#chart-history-amount').val()
        let units = $('#chart-history-units').val()
        if (minutes && minutes > 0) {
            Graph.history_amount = minutes
            Graph.history_units = units
            Graph.rerender()
        }
    },

    rerender: function () {
        if (Graph.is_visible) {
            Graph.show(Graph.path)
        }
    },

    show: function (path) {
        Graph.path = path
        Graph.is_visible = true
        let params = {
            width: Math.floor($('.modal-content').width()),
            height: Math.floor($(window).height() * 0.5),
            target: `keepLastValue(${path})`,
            from: `-${Graph.history_amount}${Graph.history_units}`,
            bgcolor: 'FAFAFA',
            fgcolor: 'black'
        }
        let url = `http://192.168.86.100:9080/render/?${encodeQueryData(params)}`
        $('#chart-img').attr('src', url)
    },

    hide: function () {
        Graph.is_visible = false
    }
}
