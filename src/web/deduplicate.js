$(() => {
    let deduplicate_timeout = null
    //
    // function deduplicate(fn) {
    //     if (deduplicate_timeout == null) {
    //         let self = this
    //         deduplicate_timeout = setTimeout(() => {
    //             fn.call(self)
    //             deduplicate_timeout = null
    //         }, 50)
    //     }
    // }

    Function.prototype.deduplicate = function () {
        let original = this
        return function () {
            if (deduplicate_timeout == null) {
                let originalThis = this
                deduplicate_timeout = setTimeout(() => {
                    original.call(originalThis)
                    deduplicate_timeout = null
                }, 50)
            }
        }
    }
})
