const mqtt = require('mqtt')
const client = mqtt.connect('http://165.22.79.210:65020')

client.on('connect', () => {

})

let id = setInterval(() => {
    let value = Math.floor(Math.random() * 60) - 20
    client.publish('temp', value.toString())
    console.log("publishing " + value)
}, 2500)
