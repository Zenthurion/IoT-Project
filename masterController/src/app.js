const TimerJob = require( 'timerjobs' ).TimerJobs;
const mqtt = require('mqtt');

const client = mqtt.connect('http://165.22.79.210:65020')

var topDomain = createController();
var subscribedTopics = [];


client.on('connect', () => {
    client.subscribe('interface');
})

client.on('message', (topic, data) => {
    var message = JSON.parse(data);
    if(topic === 'interface') {
        if (!subscribedTopics.includes(message.topic))
        {
            client.subscribe('collect/'+message.topic);
        }

        var parts = message.topic.split("/");
        updateControllers(topDomain, parts, message.data, message.topic);
    }
    if (topic.startsWith("collect/"))
    {
        saveCollectedData(topDomain, topic.substring("collect/".length).split("/"), message);
    }
    if (topic.startsWith("statusRequest/"))
    {
        var clearTopic = topic.substring("statusRequest/".length);
        publishStatus(topDomain, clearTopic.split("/"), clearTopic);
    }
    console.log(topDomain);
})

function saveCollectedData(parent, parts, data) {
    var domain = parts.shift();
    if (parent.childs[domain] === undefined)
    {
        return;
    }

    if (parts.length == 0)
    {
        if (parent.childs[domain].samples !== undefined) {
            parent.childs[domain].samples.push(data.value);
        }
        else
        {
            console.log("Recieved data with undefined sample!");
        }
    }
    else
    {
        saveCollectedData(parent.childs[domain],parts, data);
    }
}

function publishStatus(parent, parts, topic) {
    var domain = parts.shift();
    if (parent.childs[domain] === undefined)
    {
        return;
    }

    if (parts.length == 0)
    {
        semdMsg('status', topic, parent.childs[domain].data);
    }
    else
    {
        saveCollectedData(parent.childs[domain],parts, data);
    }
}

function createController()
{
    return {
        data: {},
        childs: {}
    };
}

// Every data (light, color, etc...) have tree states ON/OFF/AUTO if field is missing its the same as AUTO (was not overriden yet)
function updateControllers(parent, parts, data, topic) {
    var domain = parts.shift()
    if (parent.childs[domain] === undefined)
    {
        parent.childs[domain] = createController();
    }

    if (parts.length === 0)
    {
        if (data.state === 'AUTO' && parent.childs[domain].data.state !== undefined)
        {
            var value = findValueForAuto(topDomain, topic.split("/"), 'AUTO');
            if (value === 'AUTO') {
                //No other controller in use, turn off
                value = 'OFF';
            }
            //Emit appropriet event (change value just for command, save auto to controller)
            resolveCommand(topic, {...data, ...{state: value}}, parent.childs[domain]);
            parent.childs[domain].data = data;
        }
        else {
            //Emit appropriet events
            resolveCommand(topic, data, parent.childs[domain]);
            parent.childs[domain].data = data;
        }

    }
    else
    {
        updateControllers(parent.childs[domain], parts, data, topic);
    }
}

//Traverse from top to specific find if there is ON/OFF value for newly specify auto to set correct state to domain
function findValueForAuto(parent, parts, value) {
    var domain = parts.shift()
    if (parent.childs[domain] === undefined) {
        return value;
    }

    if (parts.length <= 1) {
        return value;
    }

    if (parent.childs[domain].data.state !== undefined && parent.childs[domain].data.state !== 'AUTO')
    {
        value = parent.childs[domain].data.state;
    }

    return findValueForAuto(parent.childs[domain], parts, value);
}

function resolveCommand(topic, data, contoller) {
    var oldData = contoller.data;

    if (oldData.reccuringEvent !== data.reccuringEvent ||
        (oldData.state === 'ON' && data.state !== oldData.state))
    {
        if (contoller.timer !== undefined)
        {
            contoller.timer.stop();
            contoller.timer = undefined;
            contoller.samples = [];
        }
    }

    if (data.reccuringEvent !== undefined && data.state === 'ON')
    {
        contoller.samples = [];
        var interval = max(data.interval, 10000);
        var timeout = max(5000, min(data.timeout, interval - 5000));
        contoller.timer = new TimerJob({
                interval: interval,
                autoStart: true,
                ignoreErrors: true,
                immediate: true
            }, function( done ) {
                contoller.samples = [];
                semdMsg('collectRequest', topic, data);
                setTimeout( function(){
                    if (contoller.samples.length === 0)
                    {
                        return;
                    }
                    //Do average
                    let sum = contoller.samples.reduce((previous, current) => current += previous);
                    let avg = sum / contoller.samples.length;
                    //MinMax normalization
                    let value = (avg - contoller.data.min) / (contoller.data.max - contoller.data.min);
                    // If change is significant enough (or not mix change is definined)
                    if (!contoller.data.minChange || abs(contoller.data.value - value) > contoller.data.minChange)
                    {
                        contoller.data.value = value;
                        //Send update command
                        semdMsg('command', topic, data);
                    }
                }, timeout );
                done();
            }
        );
    }
    // send data
    semdMsg('command', topic, data);
}

function min(a, b) {
    return a < b ? a : b;
}
function max(a, b) {
    return a > b ? a : b;
}

// send mqtt message
function semdMsg(channel, topic, data) {
    var newData = data;
    if (channel === "command")
    {
        var exclude = buildExclude(findController(topDomain, topic.split("/")), topic);
        newData = {...data,...{exclude: exclude}};
    }
    client.publish(channel+'/'+topic, JSON.stringify(newData));
}

function findController(parent, parts) {
    var domain = parts.shift();

    if (parts.length === 0)
    {
        return parent.childs[domain];
    }

    return findController(parent.childs[domain], parts);

}
function buildExclude(controller, topic) {
    var excluded = [];
    for( var key in controller.childs) {
        if (controller.childs.hasOwnProperty(controller)) {
            var newTopic = topic+"/"+key;
            if (controller.childs[key].data.state === 'AUTO')
            {
                excluded.concat(buildExclude(controller.childs[key], newTopic));
            }
            else
            {
                excluded.push(newTopic);
            }
        }
    }
    return excluded;
}