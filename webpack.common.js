const path = require('path')
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  entry: {
    init: './assets/scripts/init.js',
    htmx: {
      import: './assets/scripts/htmx.js',
      dependOn: 'init'
    },
    receipt_downloads: {
      import: './assets/scripts/receipt_downloads.js'
    },
    font_awesome: {
      import: './assets/scripts/font_awesome.js'
    }
  },
  output: {
    filename: '[id]-[contenthash].js',
    path: path.resolve(__dirname, 'frontend', 'static', 'js', 'c'),
    publicPath: "auto",
  },
  devServer: {
    writeToDisk: true
  },
  // optimization: {
  //   splitChunks: {
  //     chunks: 'all',
  //     minSize: {
  //       javascript: 900000
  //     },
  //     maxSize: {
  //       javascript: 1000000
  //     }
  //   }
  // },
  plugins: [
    new BundleTracker({path: __dirname, filename: "webpack-stats.json"}),
  ],
}
