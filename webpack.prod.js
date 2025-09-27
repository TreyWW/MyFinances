const path = require('path')
const common = require('./webpack.common.js');
const {merge} = require('webpack-merge');
const BundleTracker = require('webpack-bundle-tracker'); 

module.exports = merge(common, {
  mode: 'production',
  devtool: 'inline-source-map',
  plugins: [
      new BundleTracker({
          filename: 'webpack-stats.json' // creates at project root
      }),
  ],
});
