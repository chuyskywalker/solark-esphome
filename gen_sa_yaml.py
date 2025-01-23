## All my rig-a-ma-roll for the WESP32 device I'll be using
print('''
substitutions:
  name: sol-ark-stats-sa1
  friendly_name: SolArk Stats SA1

esphome:
  name: ${name}
  friendly_name: ${friendly_name}
  min_version: 2024.6.0
  name_add_mac_suffix: false
  project:
    name: esphome.web
    version: dev

esp32:
  board: esp32dev
  framework:
    type: arduino

# Enable logging
logger:

# Enable Home Assistant API
api:

# Allow Over-The-Air updates
ota:
- platform: esphome

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
  clk_mode: GPIO0_IN
  phy_addr: 0
  phy_registers:
    - address: 0x10
      value: 0x1FFA
      page_id: 0x07
  manual_ip:
    static_ip: 192.168.1.90
    gateway: 192.168.1.1
    subnet: 255.255.255.0

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

modbus_controller:
- id: modbus_client_sa
  modbus_id: modbus_sa
  address: 0x1
  on_online:
    then:
      - logger.log: "Controller back online!"
  on_offline:
    then:
      - logger.log: "Controller goes offline!"
  on_command_sent:
    then:
      - logger.log: "Commands sent!"

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
    lambda: |-
      uint16_t value = modbus_controller::word_from_hex_str(x, 0);
      switch (value) {{
        case 0: return std::string("Open");
        case 1: return std::string("Closed");
        case 2: return std::string("No Connection");
        case 3: return std::string("Closed, Generator is on"); 
      }}
      return std::string("Unknown State");;
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
    address: {str(address)}
    unit_of_measurement: "kwh"
    register_type: holding
    value_type: {word_type}
    filters:
    - multiply: 0.1
''')

## I have no idea how to deal with this -- the split the low/high values across non-sequential registers and the register in the middle is Grid Frequency.
# | 78             | Total Grid Buy Power (Wh) low word          | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
# | 80             | Total Grid Buy Power (Wh) high word         | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
# EDIT: I kinda figured something out, but MAN it's a hack. See lower in the file...
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
    address: {address}
    unit_of_measurement: "watts"
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
    address: {address}
    unit_of_measurement: "V"
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
    address: 183
    unit_of_measurement: "V"
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
    address: 184
    unit_of_measurement: "%"
    register_type: holding
    value_type: U_WORD
''')

# battery cap is also a bit unique
# | 107            | Corrected Batt Capacity                     | R              | [0,1000]        | 1AH            | 100 is 100AH                                                                                                    |
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Corrected Batt Capacity"
    address: 107
    unit_of_measurement: "Ah"
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
    address: {address}
    unit_of_measurement: "A"
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
    register_type: holding
    address: 91
    unit_of_measurement: "C"
    value_type: U_WORD
    filters:
    - calibrate_linear:
      - 438 -> -56.2
      - 1000 -> 0
      - 1505 -> 50.5

  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Battery temperature"
    address: 182
    unit_of_measurement: "C"
    register_type: holding
    value_type: U_WORD
    filters:
    - offset: -1000
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
    address: {address}
    unit_of_measurement: "Hz"
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
    address: {address}
    unit_of_measurement: "A"
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
    address: 78
    unit_of_measurement: "wh"
    register_type: holding
    register_count: 3
    accuracy_decimals: 1
    value_type: U_QWORD  # just to, hopefully, inform everyone up the chain what's going on
    lambda: |-
      uint64_t return_data = data[item->offset + 4] << 24
                           | data[item->offset + 5] << 16
                           | data[item->offset + 0] << 8
                           | data[item->offset + 1];
      return return_data * 100;
    filters:
      - multiply: 0.1

''')




print('''
binary_sensor:
''')

# relay on/off binary
# | 194            | Grid side relay status                      | R              |                 |                | 1 is Open (Disconnect) 2 is Closed                                                                              |
print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "Grid side relay status"
    address: 103
    register_type: holding
    lambda: |-
        if (static_cast<int>(data[1]) == 2) {{
            return true;
        }}
        return false;
''')

alarms = {
     7: "Alarm: F08 GFDI_Relay_Failure",
    12: "Alarm: F13 Grid_Mode_changed",
    13: "Alarm: F14 DC_OverCurr_Fault",
    14: "Alarm: F15 SW_AC_OverCurr_Fault",
    15: "Alarm: F16 GFCI_Failure",
    17: "Alarm: F18 HW_Ac_OverCurr_Fault",
    19: "Alarm: F20 Tz_Dc_OverCurr_Fault",
    21: "Alarm: F22 Tz_EmergStop_Fault",
    22: "Alarm: F23 Tz_GFCI_OC_Fault",
    23: "Alarm: F24 DC_Insulation_ISO_Fault",
    25: "Alarm: F26 BusUnbalance_Fault",
    28: "Alarm: F29 Parallel_Fault",
    32: "Alarm: F33 AC_OverCurr_Fault",
    33: "Alarm: F34 AC_Overload_Fault",
    40: "Alarm: F41 AC_WU_OverVolt_Fault",
    42: "Alarm: F43 AC_VW_OverVolt_Fault",
    44: "Alarm: F45 AC_UV_OverVolt_Fault",
    45: "Alarm: F46 Parallel_Aux_Fault",
    46: "Alarm: F47 AC_OverFreq_Fault",
    47: "Alarm: F48 AC_UnderFreq_Fault",
    54: "Alarm: F55 DC_VoltHigh_Fault",
    55: "Alarm: F56 DC_VoltLow_Fault",
    57: "Alarm: F58 AC_U_GridCurr_High_Fault",
    60: "Alarm: F61 Button_Manual_OFF",
    61: "Alarm: F62 AC_B_InductCurr_High_Fault",
    62: "Alarm: F63 Arc_Fault",
    63: "Alarm: F64 Heatsink_HighTemp_Fault",
}

# Setup alarms for any potential bit; even if undocumented
for n in range(64):  # range will go 0-63
    name = alarms[n] if n in alarms else f"Alarm: F{n+1:02} UNDOCUMENTED"

    # since we can't access 103 as a single 4byte value, we have to fetch
    # each register and reconfigure the alarm bit to match what it would be
    # for that register instead
    temp_bitmask_position = n
    address = 103
    while temp_bitmask_position > 15:
        temp_bitmask_position = temp_bitmask_position - 16
        address = address + 1

    print(f'''
  - platform: modbus_controller
    modbus_controller_id: modbus_client_sa
    name: "{name}"
    address: {address}
    register_type: holding
    bitmask: {format(1 << temp_bitmask_position, '#x')}  # position {str(n)}, adjusted to {temp_bitmask_position} for register {address}
''')

