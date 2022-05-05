$(() => {
    getNavigationLinks('#mobile-nav, #desktop-nav')
        .then(response => {
            const linkTemplate = Handlebars.compile($('#link-template').html())
            document.querySelector('#links').innerHTML = linkTemplate(response)
        })
})
