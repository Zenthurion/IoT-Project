const mqtt = require('mqtt')
const client = mqtt.connect('http://165.22.79.210:65020')

client.on('connect', () => {
    client.subscribe('temp')
})

client.on('message', (topic, message) => {
    if(topic === 'temp') {
        console.log(message.toString())
    }
})