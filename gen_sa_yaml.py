import sys

if len(sys.argv) < 2:
    print("Error: Missing file argument!")
    sys.exit(1)

target = sys.argv[1]

if target not in ['sa1', 'sa2']:
    print("target must be sa1 or sa2!")
    sys.exit(1)

print(f"Generating to: {target}.yaml")

# Open your log file (use 'w' to overwrite, or 'a' to append)
sys.stdout = open(f"{target}.yaml", "w", encoding="utf-8")

# SUBS:

if target == 'sa1':
    print('''
substitutions:
  name: solark-stats-sa1
  friendly_name: SolArk Stats SA1
  static_ip: 192.168.0.3
  gateway: 192.168.0.1
  subnet: 255.255.255.0
  api_key: "KRdmkbCh4KTyxUxzLYVjHjLH3wJIJEh7sGN+f/J//Pc="
  ota_pass: "676ad1f83d8f61e5537730d2b6a55f46"
    ''')

else:
    print('''
substitutions:
  name: solark-stats-sa2
  friendly_name: SolArk Stats SA2
  static_ip: 192.168.0.4
  gateway: 192.168.0.1
  subnet: 255.255.255.0
  api_key: "IQlPPneFbznTPCOgixFHw+9eDFFw9esG52Jzv+XgjW4="
  ota_pass: "bd272b999fbb83e8055dc423ba252e3b"
    ''')

## All my rig-a-ma-roll for the WESP32 device I'll be using
print('''
#
# SUBS ABOVE
#

esphome:
  name: ${name}
  friendly_name: ${friendly_name}
  min_version: 2024.6.0
  name_add_mac_suffix: false
  project:
    name: esphome.web
    version: dev
  # this is a bit of a hack; setting the status to online blindly.
  # however, the offline'ing script will eventually clear it if, on startup, the modbus doesn't connect
  on_boot:
    priority: 600.0
    then:
      - binary_sensor.template.publish:
          id: device_online_status
          state: ON
  
esp32:
  board: esp32dev
  framework:
    type: arduino

logger:
  #level: VERY_VERBOSE   #useful for debugging modbus
  # this turns off the warning about "slow" components; which modbus just takes time, yo. Chill.
  logs:
    component: ERROR

api:
  encryption:
    key: ${api_key}

ota:
  - platform: esphome
    password: ${ota_pass}

## Disabled since this is ETHERNET based
#improv_serial:
#wifi:
#  ap: {}
#captive_portal:

# for board rev.7 and up
ethernet:
  type: "RTL8201"
  mdc_pin: GPIO16
  mdio_pin: GPIO17
  clk:
    mode: CLK_EXT_IN
    pin:
      number: 0
      ignore_strapping_warning: true
  phy_addr: 0
  phy_registers:
    - address: 0x10
      value: 0x1FFA
      page_id: 0x07
  manual_ip:
    static_ip: ${static_ip}
    gateway: ${gateway}
    subnet: ${subnet}

web_server:
  port: 80
  ota: False
  version: 3
  local: True

# time:
#   - platform: homeassistant
#     id: homeassistant_time

## MODBUS STUFF

uart:
  - id: uart_modbus_client_sa
    rx_pin: 32
    tx_pin: 23
    baud_rate: 9600
    data_bits: 8
    parity: NONE
    stop_bits: 1

modbus:
  - id: modbus_sa
    uart_id: uart_modbus_client_sa
    send_wait_time: 500ms

modbus_controller:
- id: modbus_client_sa
  modbus_id: modbus_sa
  address: 0x01  # it's ALWAYS 0x1; per the docs: 
                 #
                 #   The inverter’s Slave ID is 0x01. This cannot be changed. The “Modbus SN” under
                 #   the “Parallel” tab does not affect the Slave ID for this map and is only relevant
                 #   to parallel configurations
                 #
  command_throttle: 150ms
  on_online:
    then:
      - logger.log: "Controller back online!"
      - binary_sensor.template.publish:
          id: device_online_status
          state: ON
  on_offline:
    then:
      - logger.log: "Controller goes offline!"
      - binary_sensor.template.publish:
          id: device_online_status
          state: OFF
  on_command_sent:
    then:
      - logger.log: "Commands sent!"

### Stats Below!

''')

# Begin the sensors; first text, then floats, then binary
print('''
text_sensor:

  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Serial Number"
    register_type: holding
    address: 3
    raw_encode: ANSI
    response_size: 10
''')

# gen side relay has a number of options; turn them into text
# | 195            | Generator side relay status                 | R              |                 |                | Low 4 indicates the state of generator relay 0 Open 1 Closed  2 No Connection 3 Closed when Generator is on.    |
print('''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Generator side relay status"
    register_type: holding
    address: 195
    raw_encode: HEXBYTES
    response_size: 2
    lambda: |-
      // Extract the FIRST byte (index 0) from the hex string payload
      uint8_t raw_byte = modbus::helpers::byte_from_hex_str(x, 0);
      
      // Isolate the low 4 bits by masking with 0x0F (binary 00001111)
      uint8_t state = raw_byte & 0x0F;
      
      switch (state) {
        case 0: return {"Open"};
        case 1: return {"Closed"};
        case 2: return {"No Connection"};
        case 3: return {"Closed, Generator is on"};
        default: return {"Unknown State"};
      }
''')

print('''
sensor:
''')

kwhs = [
    (  60,  "Day Active Power"                , "S_WORD"),
    (  63,  "Total Active Power"              , "S_DWORD_R"),
    (  70,  "Day Batt Charge Power"           , "U_WORD"),
    (  71,  "Day Batt Discharge Power"        , "U_WORD"),
    (  72,  "Total Batt charge Power"         , "U_DWORD_R"),
    (  74,  "Total Batt Discharge Power"      , "U_DWORD_R"),
    (  76,  "Day Grid Buy Power"              , "U_WORD"),
    (  77,  "Day Grid Sell Power"             , "U_WORD"),
## I have no idea how to deal with this -- the split of the low/high values across non-sequential registers and the register in the middle is Grid Frequency.
# | 78             | Total Grid Buy Power (Wh) low word          | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
# | 80             | Total Grid Buy Power (Wh) high word         | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
# EDIT: I kinda figured something out, but MAN it's a hack. See lower in the file...
    (  81,  "Total Grid Sell Power"           , "U_DWORD_R"),
    (  84,  "SG: Day Load Power"              , "U_WORD"),
    (  85,  "Total Load Power"                , "U_DWORD_R"),
    (  96,  "Total PV Power over all time"    , "U_DWORD_R"),
    ( 108,  "Daily PV Power"                  , "U_WORD"),
]

for (address, name, word_type) in kwhs:
    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    id: "sensor_{address}"
    address: {address}
    unit_of_measurement: "kWh"
    device_class: "energy"
    state_class: "total_increasing"
    register_type: holding
    value_type: {word_type}
    filters:
    - multiply: 0.1
''')

watts = [
    ( 166, "Gen or AC Coupled power input",     "S_WORD"),
    ( 167, "Grid side L1 power",                "S_WORD"),
    ( 168, "Grid side L2 power",                "S_WORD"),
    ( 169, "Total power of grid side L1-L2",    "S_WORD"),
    ( 170, "Grid external Limter1 power (CT1)", "S_WORD"),
    ( 171, "Grid external Limter2 power (CT2)", "S_WORD"),
    ( 172, "Grid external Total Power",         "S_WORD"),
    ( 173, "Inverter outputs L1 power",         "S_WORD"),
    ( 174, "Inverter outputs L2 power",         "S_WORD"),
    ( 175, "Inverter output Total power",       "S_WORD"),
    ( 176, "Load side L1 power",                "S_WORD"),
    ( 177, "Load side L2 power",                "S_WORD"),
    ( 178, "Load side Total power",             "S_WORD"),
    ( 186, "PV1 input power",                   "U_WORD"),
    ( 187, "PV2 input power",                   "U_WORD"),
    ( 188, "PV3 input power",                   "U_WORD"),
    ( 189, "PV4 input power",                   "U_WORD"),
    ( 190, "Battery output power",              "S_WORD"),
]

for (address, name, word_type) in watts:
    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    id: "sensor_{address}"
    address: {address}
    unit_of_measurement: "W"
    device_class: "power"
    state_class: "measurement"
    register_type: holding
    value_type: {word_type}
''')



voltages = [
  ( 109, "DC (PV) voltage 1"                     ),
  ( 111, "DC (PV) voltage 2"                     ),
  ( 113, "DC (PV) voltage 3"                     ),
  ( 150, "Grid side voltage L1-N"                ),
  ( 151, "Grid side voltage L2-N"                ),
  ( 152, "Grid side voltage L1-L2"               ),
  ( 153, "Voltage at middle side of relay L1-L2" ),
  ( 154, "Inverter output voltage L1-N"          ),
  ( 155, "Inverter output voltage L2 N"          ),
  ( 156, "Inverter output voltage L1 L2"         ),
  ( 157, "Load voltage L1"                       ),
  ( 158, "Load voltage L2"                       ),
  ( 181, "Gen Port Voltage L1-L2"                ),
]

for (address, name) in voltages:
    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    id: "sensor_{address}"
    address: {address}
    unit_of_measurement: "V"
    device_class: "voltage"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
    filters:
    - multiply: 0.1
''')

# Battery voltage is stored sliiightly different than the others (more precises, I guess), so hardcoding it
#    | 183            | Battery voltage                             | R              |                 | 0.01V          | 4100 mark of 41.0 V                                                                                             |
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Battery voltage"
    id: "sensor_183"
    address: 183
    unit_of_measurement: "V"
    device_class: "voltage"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
    filters:
    - multiply: 0.01
''')

# battery state of charge (SOC) is like nothing else, also hardcoding
# | 184            | Battery capacity SOC                        | R              | [0,100]         | 1%             |                                                                                                                 |
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Battery capacity SOC"
    id: "sensor_184"
    address: 184
    unit_of_measurement: "%"
    device_class: "battery"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
''')

# battery cap is also a bit unique
# | 107            | Corrected Batt Capacity                     | R              | [0,1000]        | 1AH            | 100 is 100AH                                                                                                    |
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Corrected Batt Capacity"
    id: "sensor_107"
    address: 107
    unit_of_measurement: "Ah"
    device_class: "energy_storage"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
''')


# pv amps
pvamps = [
  ( 110, "DC (PV) current 1"),
  ( 112, "DC (PV) current 2"),
  ( 114, "DC (PV) current 3"),
]
for (address, name) in pvamps:
    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    id: "sensor_{address}"
    address: {address}
    unit_of_measurement: "A"
    device_class: "current"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
    filters:
    - multiply: 0.1
''')

# temps are weirdly stored and inconsistent...
# | 90  | DC/DC Transformer temperature               | R | [0,3000] | 0.1℃ | Same offset as register 91. Not used in 15K.
# | 91  | IGBT Heat Sink temperature                  | R | [0,3000] | 0.1℃ | -56.2℃ indicated as 438 0℃ indicated as 1000 50.5 ℃ indicated as 1505
# | 182 | Battery temperature                         | R | [0,3000] | 0.1℃ | Real value of offset + 1000 1200 is 20.0 ℃

print(f'''    
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "IGBT Heat Sink"
    id: "sensor_91"
    register_type: holding
    address: 91
    unit_of_measurement: "°C"
    device_class: "temperature"
    state_class: "measurement"
    value_type: U_WORD
    filters:
    - calibrate_linear:
      - 438 -> -56.2
      - 1000 -> 0
      - 1505 -> 50.5

  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Battery temperature"
    id: "sensor_182"
    address: 182
    unit_of_measurement: "°C"
    device_class: "temperature"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
    filters:
    #- offset: -1000  # the docs say to offset by 1000, but I was getting values like "250" when pulled raw
    # which seems a whole lot more like *.1 instead.
    - multiply: 0.1
''')
# pv amps
hertz = [
    (79 , "Grid frequency"),
    (192, "Load frequency"),
    (193, "Inverter output frequency"),
    (196, "Generator relay Frequency"),
]
for (address, name) in hertz:
    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    id: "sensor_{address}"
    address: {address}
    unit_of_measurement: "Hz"
    device_class: "frequency"
    state_class: "measurement"
    register_type: holding
    value_type: U_WORD
    filters:
    - multiply: 0.01
''')

# other amps
otheramps = [
    ( 160, "Grid side current L1"),
    ( 161, "Grid side current L2"),
    ( 162, "Grid external Limiter current L1"),
    ( 163, "Grid external Limiter current L2"),
    ( 164, "Inverter output current L1"),
    ( 165, "Inverter output current L2"),
    ( 179, "Load current L1"),
    ( 180, "Load current L2"),
    ( 191, "Battery output current"),
]
for (address, name) in otheramps:
    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    id: "sensor_{address}"
    address: {address}
    unit_of_measurement: "A"
    device_class: "current"
    state_class: "measurement"
    register_type: holding
    value_type: S_WORD
    filters:
    - multiply: 0.01
''')


print('''

  # https://community.home-assistant.io/t/esphome-modbus-and-non-sequential-low-high-registers/832600/6
  #
  # This value is STUPID. They took the high/low values of a 32bit int and split them across non-contiguous
  # registers. Any modbus utility has the ability to say "grab a 8/16/32/64 bit value starting at X address"
  # but none of them are setup to understand the frustrating non-contiguous split that SolArk did for 
  # "Total Grid Buy Power" where it's low word is in register 78 and its high word is in 80, while register
  # 79 (right in the middle) is Grid Hertz. Cool!
  #
  # Therefor, you must pull 3 registers and run a lambda to recombine the register 78 and 80 back
  # into the sensible 32bit int it's supposed to be.
  #
  # UGH
  #
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Total Grid Buy Power"
    id: "sensor_78"
    address: 78
    unit_of_measurement: "kWh"
    device_class: "energy"
    state_class: "total_increasing"
    register_type: holding
    register_count: 3
    accuracy_decimals: 1
    force_new_range: true  # this one is quirky; force it to be fetched on its own
    lambda: |-
      uint64_t return_data = data[item->offset + 4] << 24
                           | data[item->offset + 5] << 16
                           | data[item->offset + 0] << 8
                           | data[item->offset + 1];
      return return_data;
    filters:
      - multiply: 0.1

''')

# Read the entire bitmask 64bit int into this field
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Error Code Bitmask"
    id: "error_code_bitmask"
    address: 103
    register_type: holding
    value_type: U_QWORD_R
    accuracy_decimals: 0
    force_new_range: true
''')




print('''
binary_sensor:
''')

print(f'''
  - platform: template
    name: "Modbus Device Status"
    id: device_online_status
    device_class: connectivity
''')

# relay on/off binary
# | 194            | Grid side relay status                      | R              |                 |                | 1 is Open (Disconnect) 2 is Closed                                                                              |
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Grid side relay status"
    id: "sensor_194"
    address: 194
    register_type: holding
    lambda: |-
        if (static_cast<int>(data[1]) == 2) {{
            return true;
        }}
        return false;
''')

# The MODBUS docs and latest manual don't agree on all the error codes :/
alarms = {
     0: "DC_Inversed_Failure",
     7: "GFDI_Relay_Failure",
    12: "Grid_Mode_changed",
    13: "DC_OverCurr_Fault",
    14: "AC_OverCurr_Failure",
    15: "GFCI_Failure",
    17: "HW_Ac_OverCurr_Fault",
    19: "Tz_Dc_OverCurr_Fault",
    21: "Tz_EmergStop_Fault",
    22: "Tz_GFCI_OC_Fault",
    23: "DC_Insulation_ISO_Fault",
    24: "DC_Feedback_Fault",
    25: "BusUnbalance_Fault",
    28: "Parallel_Fault",
    30: "Soft_Start_Failed",
    32: "AC_OverCurr_Fault",
    33: "AC_Overload_Fault",
    34: "AC_NoUtility_Fault",
    36: "DCLLC_Soft_Over_Cur",
    38: "DCLLC_Over_Current",
    39: "Batt_Over_Current",
    40: "AC_WU_OverVolt_Fault", # F41 Parallel_System_Stop_Fault - If one system faults in parallel, this normal fault will register on the other units as they disconnect fromthe grid.
    42: "AC_VW_OverVolt_Fault",
    44: "AC_UV_OverVolt_Fault",
    45: "Parallel_Aux_Fault",  # F46 Battery_Backup_Fault - Cannot communicate with other parallel systems. Check Master = 1, Slaves = 2-9 and that ethernet are connected.
    46: "AC_OverFreq_Fault",
    47: "AC_UnderFreq_Fault",
    54: "DC_VoltHigh_Fault",
    55: "DC_VoltLow_Fault",
    57: "AC_U_GridCurr_High_Fault", # F58 BMS_Communication_Fault - Sol-Ark is programmed to BMS Lithium Battery Mode but cannot communicate with a BMS. BMS_Err_Stop is enabled, but cannot communicate with a battery BMS
    59: "Gen_Volt_or_Fre_Fault",
    60: "Button_Manual_OFF",
    61: "AC_B_InductCurr_High_Fault",
    62: "Arc_Fault",
    63: "Heatsink_HighTemp_Fault",
}


# the modbus binarysensor only fetches a single word so we can't read 4 registers,
# get a single 64bit value and bitmath against that. Instead, we've fetched the entire bitmask int
# above in `error_code_bitmask` and can just bitmask our way into all the data
#
# I have also confirmed that the data is stored low word first; ie:
#   combinedl = data['106'][2:].zfill(16) \
#             + data['105'][2:].zfill(16) \
#             + data['104'][2:].zfill(16) \
#             + data['103'][2:].zfill(16)
# is how you put together the data (if it's all strings of the binary data; see explore.py)

for original_bitmask in range(64): # the original bit ranges

    name = f'Alarm: F{original_bitmask + 1:02} ' + (alarms[original_bitmask] if original_bitmask in alarms else "UNDOCUMENTED")

    print(f'''
  - platform: template
    device_class: "safety"
    name: "{name}"
    lambda: |-
      uint64_t mask = id(error_code_bitmask).state;
      return (mask & (1ULL << {original_bitmask})) != 0;''')

###
### I don't know exactly what's up; but setting some of these things to NaN is really fucking with the
### incoming metrics to where I'm getting absolute garbage data.
###
# # install a script that will NaN all the numbers if the system
# # goes "offline" so we don't report bogus data up to HomeAssistant
# print(f'''
# script:
#   - id: modbus_watchdog
#     mode: single
#     then:
#       - delay: 5min # after the system goes "offline", this delays for 5 minutes to see if it was a fluke
#                     # the "online" will cancel this script (if running)
#       - logger.log: "Modbus timeout reached; resetting sensors"
#       - lambda: |-
#           // Force sensors to NaN (renders as 'unavailable' in Home Assistant)
#           ''')
#
# for (address, name, word_type) in kwhs:
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
# for (address, name, word_type) in watts:
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
# for (address, name) in voltages:
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
# for (address, name) in pvamps:
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
# for (address, name) in hertz:
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
# for (address, name) in otheramps:
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
# for (address) in [183, 184, 107, 91, 182, 78, 103]:  # manually derived sensors; nor part of above lists
#     print(f'''          id(sensor_{address}).publish_state(NAN);''')
#
# print(f'''
#       - logger.log: "...reset complete"
# ''')
