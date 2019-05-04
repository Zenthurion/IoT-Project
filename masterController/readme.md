# IoTMasterContoller
```
Request from clients go to "interface" topic, data object must have this structure
Example:
topic: "interface"
data: {
  topic: "sdu/b44/165/...", // real topic
  data:  data_object // Controll object explained below
}

data_object
{
  state: "AUTO", // ON, OFF, AUTO
  reccuringEvent: true, // True for event that request data every X miliseonds and send comands based on average from them
  interval: 30000, // Interval to send data collection command - min 10s # needed for recurring only
  timeout: 10000, // Time afte comand is send to wait for collection min 5s max (interval - 5s) # needed for recurring only
  min: 0, // min value expected from data used for normalization # needed for recurring only
  max: 100, // max value expected from data used for normalization # needed for recurring only
  //value: 0.4, // initial value for reccuring event / value for not recurring event
  //minChange: 0.1, // optional minChange of value and newly calculate reccurent value in order to send comand # for recurring only
  command: "intensity" // name of command for py devices
}

Server also accepts from client topics starting "statusRequest", these topics are answered only if controller for topic exists
Example:
topic: "statusRequest/sdu/b44"
data: null

will result (data_object) in datastructure returned into topic "status/do/ma/in

Last thing server acceprs is topic "collect/do/ma/in" with data
Example:
topic: "collect/sdu/b44"
data: {
  value: value // number
}


SEND
server send tree commands
1] status/do/ma/in // sends data_object
2] command/do/ma/in // sends data_object extended with key exclude[] which containt string of exluded subtrees
3] collectRequest/do/ma/in // sends data_object


```

