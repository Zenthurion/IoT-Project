// Shared packages setup? https://medium.com/@Cyclodex/demystifying-npm-install-npm-ci-package-lock-json-2807fc0ee404

const mosca = require('mosca')
const winston = require('winston')

const settings = {
    port:65020
}

const server = mosca.Server(settings)
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    defaultMeta: { service: 'user-service' },
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'error.log', level: 'error'}),
        new winston.transports.File({ filename: 'server.log' })
    ]
})

server.on('ready', () => {
    logger.info('ready!')
})

server.on('clientConnected', (client) => {
    if(client == null) return
    logger.info(getPrefix(client) + ' Connected ')
})

server.on('clientDisconnected', (client) => {
    if(client == null) return
    logger.info(getPrefix(client) + ' Disconnected')
})

server.on('published', (packet, client) => {
    if(client == null) return
    logger.info(getPrefix(client) + ' Published: ' + packet.topic + " > " + JSON.stringify(packet.payload))
})

server.on('subscribed', (topic, client) => {
    if(client == null) return
    logger.info(getPrefix(client) + ' Subscribed: ' + topic)
})

server.on('unsubscribed', (topic, client) => {
    if(client == null) return
    logger.info(getPrefix(client) + ' Unsubscribed: ' + topic)
})

function getPrefix(client) {
    return getTimestamp() + '[' + client.connection.stream.remoteAddress + ']';
}

function getTimestamp() {
    var today = new Date();
    return today.getHours() + ':' + today.getMinutes() + ':' + today.getSeconds() + ':' + today.getMilliseconds();
}
