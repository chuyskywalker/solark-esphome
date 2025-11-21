# solark-esphome
An ESPHome configuration for reading SolArk inverter data over Modbus

`doc.md` is a PDF-to-markdown version of the solark modbus documentation pdf (requested on 2025-01-15 over email, was told it's the latest). 

`gen_sa_yaml.py` is a python script to generate the esphome configuration for the solark inverter monitor. The preamble of the file is configured for using a wesp32 board to power the setup (this makes deployment easier as you just drag a POE cable over to the box and then a regular ethernet cable out to the solark). Change it up however you like, because the **important bits** are the sections which loop through all of the modbus holding registers that the documentation gives out and turns them into sensors for esphome. _(And, sheee, there are some doozies in there -- like the 32bit int which is split across non-contiguous registers. Eeesh!)_

`gen_test.py` is an awesome little esphome configuration generator that will create an espboard that can serve as a SolArk Inverter Dummy. Once it's booted up, you can access it's webpage and configure any of the registers you want to whatever values you want, allowing you to test the logic/import/read of the main modbus client generated above.

Wiring diagram, pinouts, and specific devices are not included at this time.

Generation: I use a quick docker container to run these scripts:

```bash
cd ~/your/checkout/directory
docker run -ti --rm -v ./:/app python bash
```

Then execute `python gen_sa_yaml.py > output.yaml`, etc, etc.