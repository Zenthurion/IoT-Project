var net = require('net')
var mqttCon = require('mqtt-connection')
var server = new net.Server()

server.on('connection', (stream) => {
    var client = mqttCon(stream)

    client.on('connect', (packet) => {
        client.connacl({returnCode: 0})
        console.log('Client connected')
    })

    client.on('publish', (packet) => {
        client.puback({messageId: packet.messageId})
        console.log('pub: ' + packet)
    })

    client.on('message', (packet) => {
        client.puback({messageId: packet.messageId})
        console.log('pub: ' + packet)
    })

    client.on('pingreq', () =>{
        client.pingresp()
    })

    client.on('subscribe', (packet) =>{
        client.suback({granted:[packet.qos], messageId: packet.messageId})
        console.log('client subscribing')
    })

    stream.setTimeout(1000 * 60 * 5)

    client.on('close', () => {
        console.log('Closing')
        client.destroy()})
    client.on('error', () => {
        console.log('Error')
        client.destroy()})
    client.on('disconnect', () => {
        console.log('Disconnect')
        client.destroy()})

    stream.on('timeout', ()=> {
        console.log('Timeout')
        client.destroy()})
})

server.listen(65020)