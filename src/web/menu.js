function getNavigationLinks(selector) {
    return fetch('/navigation')
        .then(response => response.json())
        .then(response => {
            console.log(response)
            const html = response.navigation.map(it => `<li><a href="${it.link}" target="${it.new_window ? '_blank' : '_self'}">${it.name}</a>`).join('')
            document.querySelectorAll(selector).forEach(it => it.innerHTML = html)
            return response
        })
}
