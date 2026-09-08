// Vercel hosts this static command center while Render hosts the FastAPI
// service. Local/Render-served pages continue to work with relative URLs.
window.__MQI_API_BASE__ = (window.__MQI_API_BASE__ || ((location.hostname === 'localhost' || location.hostname === '127.0.0.1') ? '' : 'https://manufacturing-quality-intelligence-api.onrender.com')).replace(/\/$/, '');
const _mqiFetch = window.fetch.bind(window);
window.fetch = (input, init) => {
  const url = typeof input === 'string' ? input : input.url;
  if (url === '/health' || url.startsWith('/v1/')) {
    return _mqiFetch(`${window.__MQI_API_BASE__}${url}`, init);
  }
  return _mqiFetch(input, init);
};
