const mqtt = require('mqtt')
const client = mqtt.connect('http://165.22.79.210:65020')

client.on('connect', () => {

})

client.subscribe('home/living-room/ambient/publish')

client.on('message', (topic, message) => {
    if(topic === 'home/living-room/ambient/publish') {
        console.log(message.toString())
    }
})

let id = setInterval(() => {
    //let value = Math.floor(Math.random() * 60) - 20
    client.publish('home/living-room/ambient/request', "")
    console.log("Requesting ambient light")
}, 2500)
