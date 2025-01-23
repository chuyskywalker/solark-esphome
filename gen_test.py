print('''
esphome:
  name: solark-testbed
  friendly_name: SolArk-TestBed

esp32:
  board: esp32dev
  framework:
    type: arduino

# Enable logging
logger:

# # Enable Home Assistant API
# api:
#   encryption:
#     key: "xe6ypGzuDrIvxlPPpWkFvJWHL//QySPRJUD2D7my130="

ota:
  - platform: esphome
    password: "91030198f9e312e5175a44a357b12385"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: True

web_server:
  port: 80
  ota: False
  version: 3
  local: True

#   # Enable fallback hotspot (captive portal) in case wifi connection fails
#   ap:
#     ssid: "Solark-Testbed Fallback Hotspot"
#     password: "4qzzbkDQcB1M"

# captive_portal:


uart:
  - id: uart_modbus_server
    tx_pin: 26
    rx_pin: 25
    baud_rate: 9600
    data_bits: 8
    parity: NONE
    stop_bits: 1

modbus:
  - uart_id: uart_modbus_server
    id: modbus_server
    role: server

modbus_controller:
  - modbus_id: modbus_server
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

    server_registers:
''')

for n in range(1,197):
    print(f'''
      - address: {n}
        value_type: U_WORD
        read_lambda: |-
          return atoi(id(register_{n:03}).state.c_str());''')


print('''

text:

''')

def low(i:int):
    return str(i & 0xFFFF)
def high(i:int):
    return str((i >> 16) & 0xFFFF)

default_values = {
    3: "20819",
    4: "14649",
    5: "14136",
    6: "12849",
    7: "13108",
    60: "214",

    63: low(174054),
    64: high(174054),

    70: "800",
    71: "1678",

    72: low(229324),
    73: high(229324),

    74: low(429324),
    75: high(429324),

    76: "323",
    77: "4523",

    78: low(78934),
    80: high(78934),

    81: low(128934),
    82: high(128934),

    91: "1201"

}

for n in range(1,197):
    print(f'''
  - platform: template
    id: "register_{n:03}"
    name: "register {n:03}"
    mode: text
    optimistic: true
    initial_value: "''' + (default_values[n] if n in default_values else "0") + '"')
