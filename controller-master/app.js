const TimerJob = require( 'timerjobs' ).TimerJobs;
const mqtt = require('mqtt');
const client = mqtt.connect('http://165.22.79.210:65020');

const topics = {
    sub: {
        interface: 'interface',
        registration: 'device-registration',
        statusRequest: 'status-request', // Should be fragment?
        sensorPublishFragment: 'publish'
    },
    pub: {
        registrationRequest: 'registration-request',
        status: 'status', // Should be fragment?
        collectFragment: 'collect',
        lightCommandFragment: 'light'
    }
};
const deviceTypes = {
    light: 'light',
    ambientLightSensor: 'ambient-light-sensor'
};

const controller = new Controller();


client.on('connect', () => {
    console.log('> Connected to Broker');

    subscribe();
    client.publish(topics.pub.registrationRequest);
});

function subscribe() {
    client.subscribe(topics.sub.interface);
    client.subscribe(topics.sub.registration);
    client.subscribe(topics.sub.statusRequest);

    console.log('\n# SUBSCRIBING TO:');
    console.log('> ' + topics.sub.interface);
    console.log('> ' + topics.sub.registration);
    console.log('> ' + topics.sub.statusRequest);
    console.log()
}

client.on('message', (topic, data) => {
    const message = JSON.parse(data);
    if(topic === topics.sub.interface) // Interface command received
    {
        console.log('> received interface command: \n\t' + data);
        interfaceCommand(message);
    } 
    else if(topic === topics.sub.registration) // Device registration received
    {        
        console.log('> received device registration: \n\t' + data);
        deviceRegistrationCommand(message);
    } 
    else if(topic === topics.sub.statusRequest) // Status request received
    {
        console.log('> received status request for \n\t' + topic);
        statusRequestCommand(message);
    } 
    else if(topic.endsWith(topics.sub.sensorPublishFragment)) // Sensor data received
    {
        console.log('> received sensor data for \n\t' + topic);
        sensorDataReceived(message);
    }
});

function interfaceCommand(message) {
    // Sample message:
    // {
    //     topic: home/living-room,
    //     data: {
    //         type: STRING (device-type),
    //         state: "auto" // "on", "off",
    //         color: {
    //             r: 255,
    //             g: 255,
    //             b: 255
    //         },
    //         intensity: 255,
    //         temperature: 255
    //     }
    // }
    if(!validateInterfaceCommand(message)) return;
    if(!controller.children.hasOwnProperty(message.topic)) return;
    const room = controller.children[message.topic];

    if(message.data.type === deviceTypes.light) {
        console.log('configuring room ' + message.topic);
        room.configure(message.data)
    }

    function validateInterfaceCommand(message) {
        if(message.hasOwnProperty('topic') && message.hasOwnProperty('data')) {
            if(message.data.hasOwnProperty('type') && message.data.type === 'light') {
                return message.data.hasOwnProperty('state') && message.data.hasOwnProperty('color')
                    && message.data.hasOwnProperty('intensity') && message.data.hasOwnProperty('temperature')
                    && message.data.color.hasOwnProperty('r') && message.data.color.hasOwnProperty('g')
                    && message.data.color.hasOwnProperty('b');
            } // Add additional if-s chained to this to support additional device types
            console.log('Interface command doesn\'t contain the correct message data: ' + message);
        }
        return false;
    }
}
function deviceRegistrationCommand(message) {
    // Sample message:
    // {
    //     id: INT
    //     location: home/living-room,
    //     deviceType: ambient-light-sensor
    // }
    if(!validateRegistrationCommand(message)) return;

    if(!controller.children.hasOwnProperty(message.location)) // Entity doesn't exist yet
        controller.addEntity(new Entity(message.location));

    if(!controller.children[message.location].hasDevice(message.id))
        controller.children[message.location].addDevice(new Device(message.id, message.deviceType));


    function validateRegistrationCommand(message) {
        return message.hasOwnProperty('id') && message.hasOwnProperty('location')
            && message.hasOwnProperty('deviceType');
    }
}
function statusRequestCommand(message) {
    // Sample message:
    // {
    //     location: STRING (home/living-room)
    // }

    if(!validateStatusRequest(message)) return;

    if(message.location === 'all') {
        let entities = [];
        for(let e in controller.children) {
            entities.push(e);
        }
        let msg = {
            "type": 'all',
            "identifiers": entities,
            "entities": controller.children
        };
        client.publish(topics.pub.status, JSON.stringify(msg))
    } else {
        if(!controller.children.hasOwnProperty(message.location)) {
            let msg = {
                type: 'single',
                identifier: message.location,
                entity: undefined
            };
            client.publish(topics.pub.status, JSON.stringify(msg))
        } else {
            let entity = controller.children[message.location];
            let msg = {
                type: 'single',
                identifier: entity.identifier,
                entity: entity
            };
            client.publish(topics.pub.status, JSON.stringify(msg))
        }
    }
    console.log('status returned');


    function validateStatusRequest(message) {
        return message.hasOwnProperty('location')
    }
}
function sensorDataReceived(message) {
    // Sample message:
    // {
    //     location: STRING (home/living-room),
    //     id: INT,
    //     sensor: ambient-light-sensor,
    //     value: INT,
    //     age: INT (millis),
    //     isCache: BOOL
    // }

    if(!validateSensorData(message)) return;
    if(!controller.children.hasOwnProperty(message.location)) return; // Entity doesn't exist

    let entity = controller.children[message.location];

    entity.light.automator.samples.push(parseInt(message.value));

    function validateSensorData(message) {
        return message.hasOwnProperty('location') && message.hasOwnProperty('id')
            && message.hasOwnProperty('sensor') && message.hasOwnProperty('value')
            && message.hasOwnProperty('age') && message.hasOwnProperty('isCache')
    }
}

function Controller() {
    this.data = {};
    this.children = {};
    this.dynamicSubscriptions = [];

    this.isSubscribed = (topic) => {
        return this.dynamicSubscriptions.includes(topic)
    };
    this.addSubscription = (topic) => {
        if(this.isSubscribed(topic)) return;
        this.dynamicSubscriptions.push(topic);
        client.subscribe(topic)
        console.log('> subscribing to ' + topic);
    };

    this.removeSubscription = (topic) => {
        if(!this.isSubscribed(topic)) return;
        this.dynamicSubscriptions = this.dynamicSubscriptions.filter(e => e !== topic);
        client.unsubscribe(topic)
        console.log('> unsubscribing from ' + topic);
    };

    this.addEntity = (entity) => {
        this.children[entity.identifier] = entity;
    };
}

function Entity(identifier) {
    this.identifier = identifier;
    this.devices = {};

    this.light = {
        state: 'on', // 'on' | 'off' | 'auto'
        color: {
            r: 0,
            g: 0,
            b: 0,
        },
        intensity: 0,
        temperature: 0,
        automator: {
            timerTask: undefined,
            collectionTimeout: undefined,
            samples: []
        }
    };

    const that = this;

    function updateLight() {
        let msg = JSON.stringify({ "color": that.light.color, "intensity": that.light.intensity });
        // console.log(msg);
        client.publish(that.identifier + '/' + topics.pub.lightCommandFragment, msg);

        console.log('> updating light ' + msg);
    }

    this.configure = (data) => {
        this.light.color = data.color;

        switch(data.state) {
            case 'on':
                switch(this.light.state) {
                    case 'off':
                        break;
                    case 'auto':
                        this.light.automator.timerTask.stop();
                        if(this.light.automator.collectionTimeout !== undefined) {
                            clearTimeout(this.light.automator.collectionTimeout);
                        }
                        controller.removeSubscription(this.identifier + '/' + deviceTypes.ambientLightSensor + '/' + topics.sub.sensorPublishFragment);
                        this.light.intensity = data.intensity;
                        updateLight();
                        break;
                    case 'on':
                        break;
                }
                this.light.intensity = data.intensity;
                updateLight();
                break;
            case 'auto':
                if(this.light.state !== 'auto') {
                    if(this.light.automator.timerTask !== undefined && this.light.automator.timerTask.started()) {
                        this.light.automator.timerTask.stop();
                    }
                    if(this.light.automator.collectionTimeout !== undefined) {
                        clearTimeout(this.light.automator.collectionTimeout);
                    }

                    this.light.automator.timerTask = new TimerJob({
                        interval: 10000,
                        autoStart: true,
                        ignoreErrors: true,
                        immediate: true
                    }, (done) => {
                        this.light.automator.samples = []; // TODO: add any existing data to history? Perhaps after being averaged and normalised?
                        controller.addSubscription(this.identifier + '/' + deviceTypes.ambientLightSensor + '/' + topics.sub.sensorPublishFragment);
                        client.publish(this.identifier + '/' + deviceTypes.ambientLightSensor + '/' + topics.pub.collectFragment, JSON.stringify({ acceptedAge: 25000 }));
                        this.light.automator.collectionTimeout = setTimeout(() => {
                            if(this.light.automator.samples.length === 0) {
                                console.log('\t> received no samples!');
                                return;
                            }
                            // Do average
                            let sum = this.light.automator.samples.reduce((previous, current) => current += previous);
                            let avg = sum / this.light.automator.samples.length;
                            // MinMax normalization
                            let value = (Math.min(avg, 150) / 150) * 255; // we should identify the min and max outputs of the ambient light sensors to set this to a good value
                            let intensity = 255 - value;
                            // If change is significant enough
                            if(Math.abs(this.light.intensity - intensity) > 10) {
                                this.light.intensity = intensity;
                                updateLight()
                            }
                        }, 5000);
                        done();
                    });
                }
                break;
            case 'off':
                switch(this.light.state) {
                    case 'off':
                        break;
                    case 'auto':
                        this.light.automator.timerTask.stop();
                        if(this.light.automator.collectionTimeout !== undefined) {
                            clearTimeout(this.light.automator.collectionTimeout);
                        }
                        controller.removeSubscription(this.identifier + '/' + deviceTypes.ambientLightSensor + '/' + topics.sub.sensorPublishFragment);
                        this.light.intensity = 0;
                        updateLight();
                        break;
                    case 'on':
                        this.light.intensity = 0;
                        updateLight();
                        break;
                }
                break;
        }
        this.light.state = data.state
    };

    this.addDevice = (device) => {
        if(!this.devices.hasOwnProperty(device.id))
            this.devices[device.id] = device;
    };

    this.hasDevice = (id) => {
        for(let d in this.devices)
            if(d.hasOwnProperty('id') && d.id === id) return true;
        return false;
    };
}

function Device(id, type) {
    this.id = id;
    this.type = type;
    //this.history = {}; // move to entity and collect on a per-device-type basis?
}