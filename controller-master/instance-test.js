const mqtt = require('mqtt');
const client = mqtt.connect('http://165.22.79.210:65020');

client.on('connect', () => {
    console.log('> Connected to Broker');

    client.subscribe('status');


    //requestStatus();
    setLightAuto();
    //setLightOff();
    //setLightOn();

});

client.on('message', (topic, message) => {
    if(topic === 'status') {
        console.log('> current status: ' + message)
    }
});
function requestStatus() {
    let msg = {
        //location: 'all'
        location: 'home/living-room'
    };
    client.publish('status-request', JSON.stringify(msg))
}

function setLightOn() {
    let msg = {
        topic: 'home/living-room',
        data: {
            type: 'light',
            state: 'on',
            color: {
                r: 255,
                g: 126,
                b: 0,
            },
            intensity: 255,
            temperature: 255
        }
    };
    client.publish('interface', JSON.stringify(msg))
}

function setLightOff() {
    let msg = {
        topic: 'home/living-room',
        data: {
            type: 'light',
            state: 'off',
            color: {
                r: 255,
                g: 126,
                b: 0,
            },
            intensity: 255,
            temperature: 255
        }
    };
    client.publish('interface', JSON.stringify(msg))
}

function setLightAuto() {
    let msg = {
        topic: 'home/living-room',
        data: {
            type: 'light',
            state: 'auto',
            color: {
                r: 255,
                g: 126,
                b: 0,
            },
            intensity: 255,
            temperature: 255
        }
    };
    client.publish('interface', JSON.stringify(msg))
}
