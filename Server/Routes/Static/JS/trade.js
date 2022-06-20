// Graph related containers
var graph = document.getElementById("graph-container")
var search_stocks_button = document.getElementById("company")
var search_stocks_container = document.getElementById("company-container")
var interval_unit_selection = document.getElementById("interval_unit")
var interval_value_input = document.getElementById("interval_value")
var start_date_input = document.getElementById("date_value")

// API response containers
var market_info_container = document.getElementById("market-info-container")
var sell_stocks_container = document.getElementById("sell-container")
var buy_stocks_container = document.getElementById("buy-container")
var current_stock_price_container = document.getElementById("current-stock-price")

// Variables to store API response data
var market_info
var stock_data
var chart, chartBar
var interval_graph_format = "d/M/yyyy HH:mm"

// SocketIO connection
var socket = io('http://' + document.domain + ':' + location.port + '/trade/stocks/')

// Function to reduce data input refresh time
function debounce(func, wait, immediate) {
    var timeout
    return function() {
        var context = this, args = arguments
        var later = function() {
            timeout = null
            if (!immediate) {
                func.apply(context, args)
            }
        }
        if (immediate && !timeout) {
            func.apply(context, args)
        }

        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

// Function to select stock to show chart data from the search_stocks_container
function selectStock(e) {
    let room = e.dataset.symbol.trim() + '_' + interval_value_input.value + '_' + interval_unit_selection.value
    socket.emit('join', {'room': room, 'start_date': start_date_input.value })

    if (market_info.is_open) {
        document.getElementById("current-stock-price").innerHTML = "Current share price: <b> - </b>"
        market_info_container.innerHTML = "Open market. Next closing: <b>" + market_info.close_time.toFormat('dd/LL/yyyy HH:mm', { locale: "pl" })+ "</b>"
        //check if user has bought specific stock
    }
    else {
        market_info_container.innerHTML = "Market closed. Next opening: <b>" + market_info.open_time.toFormat('dd/LL/yyyy HH:mm', { locale: "pl" }) + "</b>"
    }
        fetch('/dashboard/trade/positions/get?' + new URLSearchParams({ symbol: e.dataset.symbol.trim() }), {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {

            if (data.message == 'OK') {
                document.getElementById("account-owned-stock-container").innerHTML = "Number of shares held: <b>" + data.quantity + " </b>"
                document.getElementById("sell_quantity").setAttribute('max', data.quantity)
                document.getElementById("sell_quantity").value = (data.quantity == 0) ? 0 : 1
                document.getElementById("sell-btn").setAttribute('onclick', market_info.is_open ? 'sellStock("' + e.dataset.symbol.trim() +'", 1)' : '')
                sell_stocks_container.style.opacity = "1"
            }
            else {
                console.log(data.message)
            }
        })

        fetch('/dashboard/trade/account/budget/', {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {

            if (data.message == 'OK') {
                document.getElementById("account-budget-container").innerHTML = "Available resources: <b>" + data.cash + " $</b>, purchasing power: <b>" + data.buying_power + " $</b>"
                document.getElementById("buy-btn").setAttribute('onclick', market_info.is_open ? 'buyStock("' + e.dataset.symbol.trim() +'", 1)' : '')
                buy_stocks_container.style.opacity = "1"
            }
            else {
                console.log(data.message)
            }
        })

}

//Function to buy stocks via asynchronous connection with given stock name, quantity and user data
function buyStock(stock, quantity) {
    fetch('/dashboard/trade/stocks/buy?' + new URLSearchParams({ symbol: stock, quantity: quantity }), {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("orders-response").innerHTML = data.message
            setTimeout(() => {
                document.getElementById("orders-response").innerHTML = ""
            }, 10000)
        })
}

//Function to sell stocks via asynchronous connection with given stock name, quantity and user data
function sellStock(stock, quantity) {
    fetch('/dashboard/trade/stocks/sell?' + new URLSearchParams({ symbol: stock, quantity: quantity }), {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message == 'Successfully sold stock.') {

                fetch('/dashboard/trade/account/budget/', {
                    method: 'GET',
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(budget_data => {

                    if (budget_data.message == 'OK') {
                        document.getElementById("account-budget-container").innerHTML = "Available resources: <b>" + budget_data.cash + " $</b>, purchasing power: <b>" + budget_data.buying_power + " $</b>"
                    }
                })
                document.getElementById("orders-response").innerHTML = data.message
                document.getElementById("account-owned-stock-container").innerHTML = "Number of shares held:: <b>" + (document.getElementById("sell_quantity").getAttribute('max') - quantity) + " </b>"
                document.getElementById("sell_quantity").setAttribute('max', (document.getElementById("sell_quantity").getAttribute('max') - quantity))
                document.getElementById("sell_quantity").value = (document.getElementById("sell_quantity").getAttribute('max') == 0) ? 0 : 1
            }
            setTimeout(() => {
                document.getElementById("orders-response").innerHTML = ""
            }, 10000)
        })
}

// Event to listen for changes on interval_unit_selection
interval_unit_selection.addEventListener("change", (e) => {

    if (e.target.value == "Minute") {
        interval_value_input.min = 1
        interval_value_input.max = 59
        interval_graph_format = "d/M/yyyy HH:mm"
    }
    else if (e.target.value == "Hour") {
        interval_value_input.min = 1
        interval_value_input.max = 23
        interval_graph_format = "d/M/yyyy HH"
    }
    else if (e.target.value == "Month") {
        interval_value_input.min = 1
        interval_value_input.max = 12
        interval_graph_format = "M/yyyy"
    }
    else {
        interval_value_input.min = 1
        interval_value_input.max = 1
        interval_graph_format = "d/M/yyyy"
    }
    interval_value_input.value = 1

})

// Event to listen for changes in buy input, then change onclick function
if (typeof(document.getElementById("buy_quantity")) != 'undefined' && document.getElementById("buy_quantity") != null) {
    document.getElementById("buy_quantity").addEventListener("change", (e) => {
        let onclick_handler = document.getElementById("buy-btn").getAttribute('onclick').split(", ")[0] + ", " + e.target.value + ")"
        document.getElementById("buy-btn").setAttribute('onclick', onclick_handler)
    })
}

// Event to listen for changes in sell input, then change onclick function
if (typeof(document.getElementById("sell_quantity")) != 'undefined' && document.getElementById("buy_quantity") != null) {
    document.getElementById("sell_quantity").addEventListener("change", (e) => {
        let onclick_handler = document.getElementById("sell-btn").getAttribute('onclick').split(", ")[0] + ", " + e.target.value + ")"
        document.getElementById("sell-btn").setAttribute('onclick', onclick_handler)
    })
}

// Event to listen for key up action on search_stocks_button
search_stocks_button.addEventListener("keyup", debounce(function () {
    search_stocks_container.style.display = "none"
    if (search_stocks_button.value.trim()) {
        let form_data = new FormData()
        form_data.append("name", search_stocks_button.value.trim())

        fetch('/dashboard/trade/stocks/search/', {
            method: 'POST',
            credentials: 'same-origin',
            body : form_data
        })
        .then(response => response.json())
        .then(data => {
            let html = '<ul class="list-unstyled">'
            if (data['status'] != 'OK') {
                html+='<li class="stock-company" style="padding: 0.5rem; margin: 0.25rem;">No results</li>';
            }
            else {
                for (var i=0; i<data['body']['symbols'].length; i++) {
                    html+='<li class="stock-company" style="padding: 0.5rem; margin: 0.25rem; cursor:pointer;" onclick="selectStock(this)" data-symbol="'+data['body']['symbols'][i]+'">'+data['body']['names'][i]+'</li>';
                }
            }
            html += '</ul>'
            search_stocks_container.innerHTML = html
            search_stocks_container.style.display = "block"
        })
    }
    else {
        search_stocks_container.innerHTML = '<ul class="list-unstyled"></ul>'
    }
}, 500))

// Event to listen for incoming data from SocketIO server on market_info data
socket.on('market_info', (data) => {
    market_info = {
        "is_open": data.is_open,
        "open_time": luxon.DateTime.fromISO(data.next_open),
        "close_time": luxon.DateTime.fromISO(data.next_close)
    }

    if (market_info.is_open) {
        market_info_container.innerHTML = "Open market. Next closing: <b>" + market_info.close_time.toFormat('dd/LL/yyyy HH:mm', { locale: "pl" })+ "</b>"
    }
    else {
        market_info_container.innerHTML = "Market closed. Next opening: <b>" + market_info.open_time.toFormat('dd/LL/yyyy HH:mm', { locale: "pl" }) + "</b>"
    }
})

// Event to listen for incoming data from SocketIO server on latest_bar data
socket.on('latest_bar', (data) => {

    let last_timestamp = luxon.DateTime.fromISO(stock_data['Timestamp'][stock_data['Timestamp'].length - 1]).toMillis()
    let latest_timestamp = luxon.DateTime.fromISO(data['stock']['charts']['Timestamp']).toMillis()
    let timestamp = latest_timestamp - last_timestamp

    let interval = interval_value_input.value * 1000
    if (interval_unit_selection.value == "Minute") {
        interval *= 60
    }
    else if (interval_unit_selection.value == "Hour") {
        interval *= 3600
    }
    else if (interval_unit_selection.value == "Day") {
        interval *= 86400
    }
    else if (interval_unit_selection.value == "Week") {
        interval *= 604800
    }
    else if (interval_unit_selection.value == "Month") {
        interval *= 2592000
    }
    if (timestamp % interval == 0) {

        socket.emit('calculate_latest_interval_with_indicators', {
            'charts': {
                'Timestamp': stock_data['Timestamp'].concat(data['stock']['charts']['Timestamp']),
                'Candles': stock_data['Candles'].concat(data['stock']['charts']['Candles']),
                'Volume': stock_data['Volume'].concat(data['stock']['charts']['Volume']),
                'Vwap': stock_data['Vwap'].concat(data['stock']['charts']['Vwap'])
            }
        })
    }
    else {
        current_stock_price_container.innerHTML = 'Current share price: <b>' + data['stock']['charts']['Candles']['Close'] + ' $</b>, update date: <b>' + luxon.DateTime.fromISO(data['stock']['charts']['Timestamp']).toFormat('dd/LL/yyyy HH:mm', { locale: "pl" }) + '</b>.'
    }

})

// Event to listen for incoming data from SocketIO server on stock_bars data
socket.on('stock_bars', (data) => {
    if (data['status'] == 'OK') {
        let unit = interval_unit_selection.value.toLowerCase() + 's'
        stock_data = JSON.parse(JSON.stringify(data['stock']['charts']))

        for (var i=0; i<data['stock']['charts']['Candles'].length; i++) {
            data['stock']['charts']['Timestamp'][i] = luxon.DateTime.fromISO(data['stock']['charts']['Timestamp'][i]).toJSDate()

            data['stock']['charts']['Vwap'][i] = [data['stock']['charts']['Timestamp'][i], data['stock']['charts']['Vwap'][i]]
            data['stock']['charts']['RSI'][i] = [data['stock']['charts']['Timestamp'][i], data['stock']['charts']['RSI'][i]]
            data['stock']['charts']['EMA'][i] = [data['stock']['charts']['Timestamp'][i], data['stock']['charts']['EMA'][i]]
            data['stock']['charts']['MACD'][i] = [data['stock']['charts']['Timestamp'][i], data['stock']['charts']['MACD'][i]]
            data['stock']['charts']['MFI'][i] = [data['stock']['charts']['Timestamp'][i], data['stock']['charts']['MFI'][i]]
            data['stock']['charts']['Volume'][i] = [data['stock']['charts']['Timestamp'][i], data['stock']['charts']['Volume'][i]]

            data['stock']['charts']['Candles'][i] = [
                data['stock']['charts']['Timestamp'][i],
                data['stock']['charts']['Candles'][i]['Open'],
                data['stock']['charts']['Candles'][i]['High'],
                data['stock']['charts']['Candles'][i]['Low'],
                data['stock']['charts']['Candles'][i]['Close'],
            ]
        }
        if (typeof chart != "undefined") {
            chart.updateOptions({
                title: {
                    text: data['stock']['symbol'],
                    align: 'center'
                },
                series: [
                    {
                        name: 'Candles',
                        data: data['stock']['charts']['Candles']
                    },
                    {
                        name: 'Vwap',
                        data: data['stock']['charts']['Vwap']
                    },
                    {
                        name: 'RSI',
                        data: data['stock']['charts']['RSI']
                    },
                    {
                        name: 'EMA',
                        data: data['stock']['charts']['EMA']
                    },
                    {
                        name: 'MACD',
                        data: data['stock']['charts']['MACD']
                    },
                    {
                        name: 'MFI',
                        data: data['stock']['charts']['MFI']
                    }
                ]
            })
            chartBar.updateOptions({
                selection: {
                    xaxis: {
                        min: luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][0][0]).minus({ [unit]: (2*interval_value_input.value) }).toJSDate().getTime(),
                        max: luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][data['stock']['charts']['Volume'].length - 1][0]).plus({ [unit]: (2*interval_value_input.value) }).toJSDate().getTime()
                    },
                },
                series: [
                    {
                        name: 'Volume',
                        data: [[luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][0][0]).minus({ [unit]: (2*interval_value_input.value) }).toJSDate(), 0]].concat(
                            data['stock']['charts']['Volume'].concat(
                                [[luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][data['stock']['charts']['Volume'].length - 1][0]).plus({ [unit]: (2*interval_value_input.value) }).toJSDate(), 0]]
                            )
                        )
                    }
                ]
            })

        }
        else {
            var options = {
                series: [
                    {
                        type: 'candlestick',
                        name: 'Candles',
                        data: data['stock']['charts']['Candles']
                    },
                    {
                        type: 'line',
                        name: 'Vwap',
                        data: data['stock']['charts']['Vwap']
                    },
                    {
                        type: 'line',
                        name: 'RSI',
                        data: data['stock']['charts']['RSI']
                    },
                    {
                        type: 'line',
                        name: 'EMA',
                        data: data['stock']['charts']['EMA']
                    },
                    {
                        type: 'line',
                        name: 'MACD',
                        data: data['stock']['charts']['MACD']
                    },
                    {
                        type: 'line',
                        name: 'MFI',
                        data: data['stock']['charts']['MFI']
                    }
                ],
                chart: {
                    redrawOnWindowResize: true,
                    height: 320,
                    width: '100%',
                    type: 'line',
                    id: 'main_graph',
                    toolbar: {
                        autoSelected: 'pan',
                        show: false
                    },
                    zoom: {
                        enabled: false,
                    },
                    animations: {
                        enabled: false
                    }
                },
                stroke: {
                    width: [1, 1]
                },
                xaxis: {
                    type: 'datetime',
                    labels: {
                        show: false,
                        datetimeUTC: true,
                        format: interval_graph_format
                    },
                    tickPlacement: 'on',
                    tooltip: {
                        enabled: false
                    }
                },
                yaxis: {
                    forceNiceScale: true,
                    decimalsInFloat: 2
                },
                plotOptions: {
                    bar: {
                        columnWidth: '50%'
                    }
                },
                tooltip: {
                    onDatasetHover: {
                        highlightDataSeries: true
                    },
                    custom: function({series, seriesIndex, dataPointIndex, w}) {
                        let date = new Date(w.globals.seriesX[0][dataPointIndex])
                        date =  luxon.DateTime.fromJSDate(date)
                        date = date.toFormat('dd/LL/yyyy HH:mm')
                        box = '<div class="apexcharts-tooltip-title" style="font-size: 12px;">' + date + '</div>'

                        for (var i = 0; i < series.length; i++) {
                            if (series[i].length != 0) {
                                let series_legend = document.querySelector("div.apexcharts-legend-series[rel='" + (i + 1) + "']")
                                box += '<div class="apexcharts-tooltip-series-group apexcharts-active" style="order: ' + (i + 1) + '; display: flex;">'
                                box += '<span class="apexcharts-tooltip-marker" style="background-color:' + series_legend.firstElementChild.style.background + ';"></span>'
                                box += '<div class="apexcharts-tooltip-text" style="font-size: 12px;">'
                                box += '<div class="apexcharts-tooltip-y-group">'
                                if (i == 0) {
                                    box += '<span class="apexcharts-tooltip-text-o-label">Open: </span>'
                                    box += '<span class="apexcharts-tooltip-text-o-value">' + w.globals.seriesCandleO[0][dataPointIndex].toFixed(2) + ' $</span></br>'
                                    box += '<span class="apexcharts-tooltip-text-o-label">High: </span>'
                                    box += '<span class="apexcharts-tooltip-text-o-value">' + w.globals.seriesCandleH[0][dataPointIndex].toFixed(2) + ' $</span></br>'
                                    box += '<span class="apexcharts-tooltip-text-o-label">Low: </span>'
                                    box += '<span class="apexcharts-tooltip-text-o-value">' + w.globals.seriesCandleL[0][dataPointIndex].toFixed(2) + ' $</span></br>'
                                    box += '<span class="apexcharts-tooltip-text-o-label">Close: </span>'
                                    box += '<span class="apexcharts-tooltip-text-o-value">' + w.globals.seriesCandleC[0][dataPointIndex].toFixed(2) + ' $</span></br>'
                                }
                                else {
                                    box += '<span class="apexcharts-tooltip-text-y-label">' + series_legend.getAttribute("seriesname") + ': </span>'
                                    box += '<span class="apexcharts-tooltip-text-y-value">'
                                    if (series[i][dataPointIndex] == null) {
                                        box += '-'
                                    }
                                    else {
                                        box += series[i][dataPointIndex].toFixed(2)
                                    }
                                    box += '</span>'
                                }
                                box += '</div>'
                                box += '</div>'
                                box += '</div>'
                            }
                        }
                        return box
                    }
                },
                legend: {
                    onItemClick: {
                        toggleDataSeries: false
                    },
                    markers: {
                        onClick: function(chart, seriesIndex, opts) {
                            if (opts.globals.seriesNames[seriesIndex] != "Candles") {
                                chart.toggleSeries(opts.globals.seriesNames[seriesIndex])
                            }
                        }
                    }
                },
                title: {
                    text: data['stock']['symbol'],
                    align: 'center'
                }
            }
            var optionsBar = {
                series: [
                    {
                        name: 'Volume',
                        data: [[luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][0][0]).minus({ [unit]: (2*interval_value_input.value) }).toJSDate(), 0]].concat(
                            data['stock']['charts']['Volume'].concat(
                                [[luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][data['stock']['charts']['Volume'].length - 1][0]).plus({ [unit]: (2*interval_value_input.value) }).toJSDate(), 0]]
                            )
                        )
                    }
                ],
                chart: {
                    redrawOnWindowResize: true,
                    height: 160,
                    width: '100%',
                    type: 'bar',
                    brush: {
                        enabled: true,
                        target: 'main_graph'
                    },
                    selection: {
                        enabled: true,
                        xaxis: {
                            min: luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][0][0]).minus({ [unit]: (2*interval_value_input.value) }).toJSDate().getTime(),
                            max: luxon.DateTime.fromJSDate(data['stock']['charts']['Volume'][data['stock']['charts']['Volume'].length - 1][0]).plus({ [unit]: (2*interval_value_input.value) }).toJSDate().getTime()
                        },
                        fill: {
                            color: '#ccc',
                            opacity: 0.4
                        },
                        stroke: {
                            color: '#0D47A1',
                        }
                    },
                },
                dataLabels: {
                    enabled: false
                },
                plotOptions: {
                    bar: {
                        columnWidth: '80%',
                        colors: {
                            ranges: [
                                {
                                    from: 0,
                                    to: 5000,
                                    color: '#D7263D'
                                },
                                {
                                    from: 5001,
                                    to: 10000,
                                    color: '#FEB019'
                                },
                                {
                                    from: 10001,
                                    to: 20000,
                                    color: '#4CAF50'
                                },
                            ],
                        },
                    }
                },
                stroke: {
                    width: 0
                },
                xaxis: {
                    type: 'datetime',
                    labels: {
                        datetimeUTC: true,
                        format: interval_graph_format
                    },
                    tickPlacement: 'on',
                },
                yaxis: {
                    labels: {
                        show: true
                    }
                },
                title: {
                    text: 'Volume',
                    align: 'center'
                },
            }
            if (document.body.classList.contains('dark-mode')) {
                options.theme = {
                    mode: 'dark'
                }
                optionsBar.theme = {
                    mode: 'dark'
                }
            }

            chart = new ApexCharts(graph.querySelector("#candles"), options)
            chartBar = new ApexCharts(graph.querySelector("#datetime-slider"), optionsBar)

            chart.render()
            chartBar.render()
            chart.hideSeries("Vwap")
            chart.hideSeries("RSI")
            chart.hideSeries("EMA")
            chart.hideSeries("MACD")
            chart.hideSeries("MFI")
        }
        if (data['predictions'] != null) {
            document.getElementById("predictions-response").innerHTML = 'Trend direction: <b>' + data['predictions']['trend_direction'] + '</b>, suggested action: <b>' + data['predictions']['action'] + '</b>.'
        }
        current_stock_price_container.innerHTML = 'Current share price: <b>' + data['latest_bar']['Candles']['Close'] + ' $</b>, update date: <b>' + luxon.DateTime.fromISO(data['latest_bar']['Timestamp']).toFormat('dd/LL/yyyy HH:mm', { locale: "pl" }) + '</b>.'
    }
    else {
        if (typeof chart != "undefined") {
            chartBar.destroy()
            chart.destroy()
        }
        graph.querySelector("#candles").innerHTML = '<p class="text-center text-danger">' + data['status'] + '</p>'
    }

    search_stocks_button.value = ""
    search_stocks_container.innerHTML = ""
    search_stocks_container.style.display = "none"

})

// Event to listen for incoming update_data from SocketIO server on stocks_bar_update data
socket.on('stocks_bar_update', (data) => {
    if (data['status'] == 'OK') {
        let unit = interval_unit_selection.value.toLowerCase() + 's'

        stock_data['Timestamp'].push(data['stocks_bar']['Timestamp'])
        stock_data['Vwap'].push(data['stocks_bar']['Vwap'])
        stock_data['Volume'].push(data['stocks_bar']['Volume'])
        stock_data['Candles'].push(data['stocks_bar']['Candles'])
        stock_data['RSI'].push(data['stocks_bar']['RSI'])
        stock_data['EMA'].push(data['stocks_bar']['EMA'])
        stock_data['MACD'].push(data['stocks_bar']['MACD'])
        stock_data['MFI'].push(data['stocks_bar']['MFI'])

        let data_volume = []
        for (var i=0; i<stock_data['Volume'].length; i++) {
            data_volume[i] = [luxon.DateTime.fromISO(stock_data['Timestamp'][i]).toJSDate(), stock_data['Volume'][i]]
        }
        if (typeof chart != "undefined") {
            chart.appendData([
                {
                    data: [
                        luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toJSDate(),
                        data['stocks_bar']['Candles']['Open'],
                        data['stocks_bar']['Candles']['High'],
                        data['stocks_bar']['Candles']['Low'],
                        data['stocks_bar']['Candles']['Close'],
                    ]
                },
                {
                    data: [ luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toJSDate(), data['stocks_bar']['Vwap'] ]
                },
                {
                    data: [ luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toJSDate(), data['stocks_bar']['RSI'] ]
                },
                {
                    data: [ luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toJSDate(), data['stocks_bar']['EMA'] ]
                },
                {
                    data: [ luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toJSDate(), data['stocks_bar']['MACD'] ]
                },
                {
                    data: [ luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toJSDate(), data['stocks_bar']['MFI'] ]
                }
            ])
            chartBar.updateOptions({
                selection: {
                    xaxis: {
                        min: luxon.DateTime.fromJSDate(data_volume[0][0]).minus({ [unit]: (2*interval_value_input.value) }).toJSDate().getTime(),
                        max: luxon.DateTime.fromJSDate(data_volume[data_volume.length - 1][0]).plus({ [unit]: (2*interval_value_input.value) }).toJSDate().getTime()
                    },
                },
                series: [
                    {
                        name: 'Volume',
                        data: [[luxon.DateTime.fromJSDate(data_volume[0][0]).minus({ [unit]: (2*interval_value_input.value) }).toJSDate(), 0]].concat(
                            data_volume.concat(
                                [[luxon.DateTime.fromJSDate(data_volume[data_volume.length - 1][0]).plus({ [unit]: (2*interval_value_input.value) }).toJSDate(), 0]]
                            )
                        )
                    }
                ]
            })

        }
        if (data['predictions'] != null) {
            document.getElementById("predictions-response").innerHTML = 'Trend direction: <b>' + data['predictions']['trend_direction'] + '</b>, suggested action: <b>' + data['predictions']['action'] + '</b>.'
        }
        current_stock_price_container.innerHTML = 'Current share price: <b>' + data['stocks_bar']['Candles']['Close'] + ' $</b>, update date: <b>' + luxon.DateTime.fromISO(data['stocks_bar']['Timestamp']).toFormat('dd/LL/yyyy HH:mm', { locale: "pl" }) + '</b>.'
    }

})

// Connect to SocketIO server
socket.connect()

// Event to listen for unload page and disconnecting user from SocketIO server
window.addEventListener('beforeunload', () => {
    socket.disconnect()
})