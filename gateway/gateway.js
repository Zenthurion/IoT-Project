const mosca = require('mosca');

const gatewayServer = mosca.Server({ port:65023 });

gatewayServer.on('ready', () => {
    console.log('gateway ready!')
})