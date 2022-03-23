function formatDateFromTimestamp(timestamp) {
    let date = new Date(parseInt(timestamp))
    return formatDate(date)
}

const ParkingMap = {
    lat: null,
    lon: null,
    timestamp: null,
    map: null,

    setLatLon: (lat, lon, timestamp) => {
        ParkingMap.lat = parseFloat(lat)
        ParkingMap.lon = parseFloat(lon)
        ParkingMap.timestamp = formatDateFromTimestamp(timestamp)
        ParkingMap.tryRun()
    },

    setMap: (map) => {
        ParkingMap.map = map
        ParkingMap.tryRun()
    },

    tryRun: () => {
        if (ParkingMap.map != null && ParkingMap.lon != null && ParkingMap.lat != null) {
            console.log(`Setting map center to ${ParkingMap.lat}, ${ParkingMap.lon}`)
            let location = {lat: ParkingMap.lat, lng: ParkingMap.lon}
            ParkingMap.map.setCenter(location)
            new google.maps.Marker({
                position: location,
                map: ParkingMap.map,
                title: `Parked at: ${ParkingMap.timestamp}`
            })
        }
    }
}
const TripMap = {
    map: null,
    polyline: null,

    setMap: (map) => {
        TripMap.map = map
    },

    setTrip: (path) => {
        if (TripMap.polyline != null) {
            TripMap.polyline.setMap(null)
        }
        TripMap.polyline = new google.maps.Polyline({
            path: path,
            geodesic: true,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 2,
          });
        TripMap.polyline.setMap(TripMap.map);

        let bounds = new google.maps.LatLngBounds()
        path.forEach(it => bounds.extend(it))
        TripMap.map.fitBounds(bounds)
    }
}

function formatAddress(address) {
    return address
        .split(',')
        .map(it => it.trim())
        .filter(it => it != 'Poland')
        .filter(it => it.indexOf('Voivodeship') < 0)
        .map(it => it.replace('Warsaw', 'Warszawa'))
        .map(it => it.replace(/\d{2}-\d{3} /, ''))
        .reverse()
        .join(', ')
}

function formatDateFromGmtString(gmtDate) {
    let timestamp = Date.parse(gmtDate)
    return formatDateFromTimestamp(timestamp)
}

function formatDate(date) {
    const offset = date.getTimezoneOffset()
    date = new Date(date.getTime() - (offset*60*1000))
    return date.toISOString()
        .replace('T', ' ')
        .replace('Z', '')
        .replace('.000', '')
}

function formatDuration(durationSeconds) {
    const seconds = durationSeconds % 60
    const minutes = Math.floor(durationSeconds / 60) % 60
    const hours = Math.floor(durationSeconds / (60 * 60)) % 60
    let result = ''
    if (hours > 0) {
        result += `${hours}h `
    }
    if (minutes > 0) {
        result += `${minutes}m `
    }
    result += `${seconds}s`
    return result

}

function tripClicked() {
    M.Modal.getInstance(document.querySelector('#loading-modal')).open()
    let tripId = this.dataset.tripId
    $.get(`/toyota/trip?id=${tripId}`, (data) => {
        console.log(data)
        M.Modal.getInstance(document.querySelector('#trip-modal')).open()
        let polyline = data.tripEvents.map(it => {return {lat: it.lat, lng: it.lon}})
        TripMap.setTrip(polyline)
        document.querySelector('#stat-distance').innerHTML = `${data.statistics.totalDistanceInKm} km`
        document.querySelector('#stat-duration').innerHTML = `${formatDuration(data.statistics.totalDurationInSec)}`
        document.querySelector('#stat-max-speed').innerHTML = `${data.statistics.maxSpeedInKmph} km/h`
        document.querySelector('#stat-avg-speed').innerHTML = `${data.statistics.averageSpeedInKmph} km/h`
        document.querySelector('#stat-total-fuel').innerHTML = `${data.statistics.fuelConsumptionInL} l`
        document.querySelector('#stat-avg-fuel').innerHTML = `${data.statistics.averageFuelConsumptionInL} l/100km`
        M.Modal.getInstance(document.querySelector('#loading-modal')).close()
    })
}

$(() => {
    getNavigationLinks('#mobile-nav, #desktop-nav')

    $.get('/toyota/apikey', (data) => {
        let googleMapsScript = document.createElement('script');
        googleMapsScript.setAttribute('src',`https://maps.googleapis.com/maps/api/js?key=${data.apikey}&callback=initMap`);
        document.head.appendChild(googleMapsScript);
    })

    M.AutoInit()
    M.Modal.init(document.querySelector('#trip-modal'), {
        endingTop: '5%'
    });
    M.Modal.init(document.querySelector('#loading-modal'), {
        dismissible: false,
        inDuration: 0
    });

    Handlebars.registerHelper('address', (string) => formatAddress(string))
    Handlebars.registerHelper('date', (string) => formatDateFromGmtString(string))
    const tripTemplate = Handlebars.compile(document.querySelector('#trip-row').innerHTML)

    M.Modal.getInstance(document.querySelector('#loading-modal')).open()

    $.get('/toyota/data', (data) => {
        console.log('Toyota data ready: ')
        console.log(data)
        document.querySelector('#fuel-left').innerHTML = `${Math.round(data.status.fuel)} %`
        document.querySelector('#odometer').innerHTML = `${data.status.odo} km`
        document.querySelector('#vin').innerHTML = `${data.status.vin}`
        document.querySelector('#plates').innerHTML = `${data.status.plates}`
        document.querySelector('#parking-lat').innerHTML = data.parking.lat
        document.querySelector('#parking-lon').innerHTML = data.parking.lon
        document.querySelector('#parking-date').innerHTML = formatDateFromTimestamp(data.parking.timestamp)
        document.querySelector('#trips').innerHTML = tripTemplate(data.trips)
        ParkingMap.setLatLon(data.parking.lat, data.parking.lon, data.parking.timestamp)

        document.querySelectorAll('#trips tbody tr').forEach(it => it.addEventListener('click', tripClicked))

        M.Modal.getInstance(document.querySelector('#loading-modal')).close()
    })


})

function initMap() {
    ParkingMap.setMap(new google.maps.Map(document.getElementById('parking-map'), {
        center: {lat: 0, lng: 0},
        zoom: 15
    }))
    TripMap.setMap(new google.maps.Map(document.getElementById('trip-map'), {
        center: {lat: 0, lng: 0},
        zoom: 15
    }))
}
