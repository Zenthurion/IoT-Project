const mqtt = require('mqtt')
const client = mqtt.connect('http://165.22.79.210:65020')

const deviceType = 'light'
const location = 'home/living-room'
const controlTopic = location + '/' + deviceType

const reRegisterTopic = 'registration-request'
const registrationTopic = 'device-registration'

client.on('connect', () => {
    console.log('Light connected to Broker')
    subscribe()
    register()
})

client.on('message', (topic, message) => {
    if(topic === controlTopic) {
        console.log('Light control update: ' + message)
    } else if(topic === reRegisterTopic) {
        register()
    }
})

function subscribe() {
    client.subscribe(controlTopic)
    client.subscribe(reRegisterTopic)
}

function register () {
    console.log("Registered to master through " + registrationTopic)
    client.publish(registrationTopic, JSON.stringify({ "id": 0, "location": location, "deviceType": deviceType }))
}