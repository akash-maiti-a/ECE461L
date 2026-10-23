// npm start loads this file automatically and forwards /api requests to the
// Flask API on port 5001.
//
// This replaces the "proxy" setting in package.json. With that setting,
// Create React App 5 crashes on start ("options.allowedHosts[0] should be a
// non-empty string") on machines where it can't find a LAN address.
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function setupProxy(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5001',
      changeOrigin: true,
    })
  );
};
