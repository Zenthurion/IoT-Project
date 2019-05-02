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

function startAmbientRequest() {
    let id = setInterval(() => { // requesting ambient light
        //let value = Math.floor(Math.random() * 60) - 20
        client.publish('home/living-room/ambient/request', JSON.stringify({ acceptedAge: 25000 }))
        console.log("Requesting ambient light")
    }, 7500)    
}

function startColorPush() {
    var arr = 0, gee = 255, bee = 0, strength = 0
    setInterval(() =>{
        //client.publish('home/living-room/light', JSON.stringify({color: {r:(arr+=25) % 255, g: (gee+=5) % 255, b: (bee+=25) % 255}, intensity: strength}))
        client.publish('home/living-room/light', JSON.stringify({color: {r:(arr), g: (gee+=5) % 255, b: (bee)}, intensity: (strength += 25) % 255}))
        console.log('pushing light color {' + (arr % 255) + ", " + (gee % 255) + ", " + (bee % 255) + '} at ' + (strength % 255) + ' intensity')
    }, 1000)    
}

//startAmbientRequest()
startColorPush()
