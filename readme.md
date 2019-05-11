# To run:
- Start the master controller
    - node controller-master/app.js
- Start the controller instance
    - py controller-instance/app.py
- Start dummy devices
    - node samples/dummy-emitter.js
    - node samples/dummy-sensor.js
- Start pycom devices
    - connect and run pycom/light-emitter (main.py) 
    - connect and run pycom/light-sensor (main.py)


- For quick debugging of the controller instance, there is also the file 'master-controller/instance-test.js'