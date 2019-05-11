const mqtt = require('mqtt');
const client = mqtt.connect('http://165.22.79.210:65020');

const deviceType = 'ambient-light-sensor';
const location = 'home/living-room';
const baseTopic = location + '/' + deviceType;
const collectTopic = baseTopic + '/collect';
const publishTopic = baseTopic + '/publish';

const reRegisterTopic = 'registration-request';
const registrationTopic = 'device-registration';

const id = 1;

client.on('connect', () => {
    console.log('Ambient light sensor connected to Broker');
    subscribe();
    register();
});

client.on('message', (topic, message) => {
    if(topic === collectTopic) {
        console.log('Request to collect sensor data');
        let randomLight = Math.floor(Math.random() * 120);
        client.publish(publishTopic, JSON.stringify({ "location": location, "id": id, "sensor": deviceType, "value": randomLight, "age": 0, "isCache": false}));
        console.log('Published ' + randomLight)
    } else if(topic === reRegisterTopic) {
        register()
    }
});

function subscribe() {
    client.subscribe(collectTopic);
    client.subscribe(reRegisterTopic)
}

function register () {
    console.log("Registered to master through " + registrationTopic);
    client.publish(registrationTopic, JSON.stringify({ "id": id, "location": location, "deviceType": deviceType }))
}