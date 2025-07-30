const path = require('path');

module.exports = {
  entry: './render.js', // Your main JS file
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'), // Output directory
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // This is optional, for transpiling ES6+ code
        },
      },
    ],
  },
};



