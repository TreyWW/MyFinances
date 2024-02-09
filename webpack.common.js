const path = require('path')

module.exports = {
    entry: './assets/scripts/init.js',
    output: {
        'filename': 'bundle.js',
        'path': path.resolve(__dirname, 'frontend', 'static', 'js')
    }
}