$(() => {
    let deduplicate_timeout = null

    Function.prototype.deduplicate = function (timeout = 50) {
        let original = this
        return function () {
            let originalThis = this
            let originalArguments = arguments
            if (deduplicate_timeout != null) {
                clearTimeout(deduplicate_timeout)
            }
            deduplicate_timeout = setTimeout(() => {
                original.apply(originalThis, originalArguments)
                deduplicate_timeout = null
            }, timeout)
        }
    }
})
