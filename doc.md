# Modbus RTU Protocol,

Sol-Ark Hybrid Inverters:

## 5k, 8k, 12k, 15k


| Version | Changelog                                                   | Editor                           | Date of Revision      |
|---------|-------------------------------------------------------------|----------------------------------|-----------------------|
| V1.0    | Initial Release                                             | W. Hopkins, Y. Chen              | 2021-03-31            |
| V1.1    | Updated Disclaimer & Notes                                  | W. Hopkins                       | 2021-04-15            |
| V1.2    | Document Cleanup                                            | W. Hopkins                       | 2021-07-28            |
| V1.3    | Added “Sol-Ark 15K”                                         | V. Wei, Daniel Oyedapo           | 2022-06-29 2022-09-15 |
| V1.4    | Added registers for total energy data, misc. clarifications | Jonathan Nesbitt, Daniel Oyedapo | 2023-10-13            |


# Disclaimer:

Sol-Ark does not offer technical support for 3rd party Modbus devices nor this Modbus map. 

The inverter only supports read operations.

Any damage caused to the inverter due to the use of any Modbus device is NOT covered by Sol-Ark’s warranty. 

## Important notes before use:

1. The inverter must be in “BMS Lithium Batt” mode “00” for this protocol to function. The check box next to “BMS Lithium Batt” can be either checked or unchecked so long as the value in this field is “00”. 

2. The Sol-Ark Modbus RTU Protocol cannot be used simultaneously with Modbus or RS-485 based battery communications. 

3. If a battery is using CAN Bus based battery communications with “BMS Lithium Batt” set to “00”, this protocol can still be used to read data from the system. 

4. A 120 Ohm termination resistor should be used on the master side of the communication cable. The inverter already has termination internally. 

5. The inverter’s Slave ID is 0x01. This cannot be changed. The “Modbus SN” under the “Parallel” tab does not affect the Slave ID for this map and is only relevant to parallel configurations. 

6. Ground MUST be connected between the inverter and master device. Without ground connected, communication can be easily disrupted by external noise sources.

7. Sol-Ark Support WILL NOT provide support for this document nor communications with 3rd party controllers! Sol-Ark Technical Support will still be able to help with normal system questions but will not be able to solve problems relating to this document nor the information in it. 

## Inverter Pinouts:

## Sol-Ark 8K: 

Communications on the Sol-Ark 8K are achieved through either of the 2 RJ-45 ports labeled “RJ45_485” and “RJ45_CAN” or the terminal connectors for RS-485 and CAN. 

The ports are shown below alongside pin diagrams and detailed pin configurations for each port. 

<!-- 8 7 6 5 4 3 2 P∈ Function 1 RS-485 B- 2 RS-485 A+ 3 GND 4 5 6 GND 7 RS-485 A+ 8 RS-485 B-  -->
![](https://web-api.textin.com/ocr_image/external/5fe7a5647d3dba47.jpg)

Communications on the Sol-Ark 12K are achieved through the RJ-45 ports labeled “RS-485” and “CAN”. 

The ports are shown below alongside pin diagrams and detailed pin configurations for each port. 


![](https://web-api.textin.com/ocr_image/external/26068b1aeca3eee4.jpg)


![](https://web-api.textin.com/ocr_image/external/d691c3bda6a2aae5.jpg)


| Pin | Function  |
|-----|-----------|
| 1   | RS-485 B- |
| 2   | RS-485 A+ |
| 3   | GND       |
| 4   |           |
| 5   |           |
| 6   | GND       |
| 7   | RS-485 A+ |
| 8   | RS-485 B- |


## Outdoor Sol-Ark 5K, 8K & 12K: 

Communications on the Outdoor rated units are achieved through a single RJ-45 port labeled “Battery CAN Bus”. This port combines the pin configurations of the RS-485 and CAN ports on the indoor rated 12K. 

The port is shown below alongside a pin diagram and detailed pin configuration.

<!-- Pin Function 1 RS-485 B- 2 RS-485 3 4 CAN Hi 5 CAN Lo 6 GND 7 RS-485 A+ 8 RS-485 B-  -->
![](https://web-api.textin.com/ocr_image/external/52daa5009d5578a2.jpg)


| Pin | Function  |
|-----|-----------|
| 1   | RS-485 B- |
| 2   | RS-485    |
| 3   |           |
| 4   | CAN Hi    |
| 5   | CAN Lo    |
| 6   | GND       |
| 7   | RS-485 A+ |
| 8   | RS-485 B- |


Note: The “Modbus RS-485” port on the outdoor rated systems is not for battery communications and is currently not implemented. 

## Sol-Ark 15K:

Communications on the Outdoor rated units are achieved through a single RJ-45 port labeled “Battery CAN Bus”. Similar to the Outdoor Sol-Ark series, this port combines the pin configurations of the RS-485 and CAN ports on the indoor rated 12K. 

The port is shown below alongside a pin diagram and detailed pin configuration.


| Pin | Function  |
|-----|-----------|
| 1   | RS-485 B- |
| 2   | RS-485 A+ |
| 3   |           |
| 4   | CAN Hi    |
| 5   | CAN Lo    |
| 6   | GND       |
| 7   | RS-485 A+ |
| 8   | RS-485 B- |


<!-- Pin Function 1 RS-485 B- 2 RS-485 A+ 3 4 CAN Hi 5 CAN Lo 6 GND 7 RS-485 A+ 8 RS-485 B-  -->
![](https://web-api.textin.com/ocr_image/external/5bee9c95a06f27c6.jpg)

Note: The “Modbus RS-485” port on the Sol-Ark 15K systems is not for battery communications and is currently not implemented. 

## RTU Settings: Baud rate: 9600bps, Parity: None, Data Bits: 8, Stop Bits: 1

[Note]  Reserved words, reserved bytes, reserved bits, and unsupported registers are all filled with 0x00. 

## Function codes of the Modbus RTU protocol 

The following table lists only the function codes to which this protocol applies. 


| Function code | Function code type   | Name                            | Description                                                       |
|---------------|----------------------|---------------------------------|-------------------------------------------------------------------|
| 0x03 (FC3)    | Public function code | Read Multiple Holding Registers | Contents read from either a single register or multiple registers |


## Reading Multiple Holding Registers (function code: 0x03) 

## (1) Request PDU 


| Data structure            | Data length | Data range      |
|---------------------------|-------------|-----------------|
| Function code             | 1 byte      | 0x03            |
| Starting register address | 2 bytes     | 0x0000\~0xFFFF  |
| Number of registers       | 2 bytes     | 0x0001\~ 0x007D |


## (2) Normal Response PDU 


| Data structure  | Data length | Data range |
|-----------------|-------------|------------|
| Function code   | 1 byte      | 0x03       |
| Byte count      | 1 byte      | N×2        |
| Register values | N×2 byte    |            |


Note: N = number of registers 

## (3) Abnormal response PDU 


| Data structure | Data length | Data range                        |
|----------------|-------------|-----------------------------------|
| Error code     | 1 byte      | 0x83                              |
| Exception code | 1 byte      | See "exception code" for details. |


## (4) Example 

Request to read from three consecutive registers starting at address 107 (the following describes only the PDU): 


| Request                | Request | Normal response   | Normal response | Abnormal response | Abnormal response |
|------------------------|---------|-------------------|-----------------|-------------------|-------------------|
| Field name             | Value   | Field name        | Value           | Field name        | Value             |
| Function code          | 0x03    | Function code     | 0x03            | Error code        | 0x83              |
| Starting address Hi    | 0x00    | Byte count        | 0x06            | Exception code    | 0x04              |
| Starting address Lo    | 0x6B    | Register [107] Hi | 0x02            |                   |                   |
| Number of registers Hi | 0x00    | Register [107] Lo | 0x2B            |                   |                   |
| Number of registers Lo | 0x03    | Register [108] Hi | 0x00            |                   |                   |
|                        |         | Register [108] Lo | 0x00            |                   |                   |
|                        |         | Register [109] Hi | 0x00            |                   |                   |
|                        |         | Register [109] Lo | 0x64            |                   |                   |

| Addr | Register description | R/W | Data range         | Unit | Note                                                                                                                                                                  |
|------|----------------------|-----|--------------------|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3    | SN byte 01           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 3    | SN byte 02           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 4    | SN byte 03           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 4    | SN byte 04           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 5    | SN byte 05           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 5    | SN byte 06           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 6    | SN byte 07           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 6    | SN byte 08           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 7    | SN byte 09           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |
| 7    | SN byte 10           | R   | ‘0’\~’9’; ‘A’\~’Z’ |      | The serial number is ten ASCII characters, If "AH12345678", Byte 01 is 0x41 (A), The 02nd byte is 0x48 (H), …… The 09th byte is 0x37 (7), The tenth byte is 0x38 (8). |



| Addr           | Register description                        | R/W            | Data range      | Unit           | Note                                                                                                            |
|----------------|---------------------------------------------|----------------|-----------------|----------------|-----------------------------------------------------------------------------------------------------------------|
| 60             | Day Active Power (Wh)                       | R              | [-32768, 32767] | 0.1kWh         | Signed int. Inverter Grid port energy                                                                           |
| 63             | Total Active Power (Wh) low word            | R              | [0,0xFFFFFFFF]  | 0.1kWh         | Signed int. Inverter Grid port energy                                                                           |
| 64             | Total Active Power (Wh) high word           | R              | [0,0xFFFFFFFF]  | 0.1kWh         | Signed int. Inverter Grid port energy                                                                           |
| 70             | Day Batt Charge Power (Wh)                  | R              | [0,9999]        | 0.1kwh         |                                                                                                                 |
| 71             | Day Batt Discharge Power (Wh)               | R              | [0,9999]        | 0.1kwh         |                                                                                                                 |
| 72             | Total Batt charge Power (Wh) low word       | R              | [0,9999]        | 0.1kwh         |                                                                                                                 |
| 73             | Total Batt charge Power (Wh) high word      | R              | [0,9999]        | 0.1kwh         |                                                                                                                 |
| 74             | Total Batt Discharge Power (Wh) low word    | R              | [0,9999]        | 0.1kwh         |                                                                                                                 |
| 75             | Total Batt Discharge Power (Wh) high word   | R              | [0,9999]        | 0.1kwh         |                                                                                                                 |
| 76             | Day Grid Buy Power (Wh)                     | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
| 77             | Day Grid Sell Power (Wh)                    | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
| 78             | Total Grid Buy Power (Wh) low word          | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
| 79             | Grid frequency                              | R              | [0,9999]        | 0.01Hz         |                                                                                                                 |
| 80             | Total Grid Buy Power (Wh) high word         | R              | [0,65535]       | 0.1kwh         |                                                                                                                 |
| 81             | Total Grid Sell Power (Wh) low word         | R              | [0,0xFFFFFFFF]  | 0.1kwh         |                                                                                                                 |
| 82             | Total Grid Sell Power (Wh) high word        | R              | [0,0xFFFFFFFF]  | 0.1kwh         |                                                                                                                 |
| 84             | SG: Day Load Power (Wh)                     | R              | [0,0xFFFF]      | 0.1kwh         |                                                                                                                 |
| 85             | Total Load Power (Wh) low word              | R              | [0,0xFFFF]      | 0.1kwh         |                                                                                                                 |
| 86             | Total Load Power (Wh) high word             | R              | [0,0xFFFF]      | 0.1kwh         |                                                                                                                 |
| 90             | DC/DC Transformer temperature               | R              | [0,3000]        | 0.1℃           | Same offset as register 91. Not used in 15K.                                                                    |
| 91             | IGBT Heat Sink temperature                  | R              | [0,3000]        | 0.1℃           | -56.2℃ indicated as 438 0℃ indicated as 1000 50.5 ℃ indicated as 1505                                           |
| 96             | Total PV Power over all time (Wh) low word  | R              | [0,0xFFFFFFFF]  | 0.1kWh         |                                                                                                                 |
| 97             | Total PV Power over all time (Wh) high word | R              | [0,0xFFFFFFFF]  | 0.1kWh         |                                                                                                                 |
| 103            | Fault information word 1                    | R              | [0,65535]       |                | See “Fault Table” at the end of the document for values Uses bit flags, 64 separate bits One bit for each fault |
| 104            | Fault information word 2                    | R              | [0,65535]       |                | See “Fault Table” at the end of the document for values Uses bit flags, 64 separate bits One bit for each fault |
| 105            | Fault information word 3                    | R              | [0,65535]       |                | See “Fault Table” at the end of the document for values Uses bit flags, 64 separate bits One bit for each fault |
| 106            | Fault information word 4                    | R              | [0,65535]       |                | See “Fault Table” at the end of the document for values Uses bit flags, 64 separate bits One bit for each fault |
| 107            | Corrected Batt Capacity                     | R              | [0,1000]        | 1AH            | 100 is 100AH                                                                                                    |
| 108            | Daily PV Power (Wh)                         | R              | [0,65535]       | 0.1kWh         | Total PV energy produced daily                                                                                  |
| 109            | DC (PV) voltage 1                           | R              | [0,65535]       | 0.1V           |                                                                                                                 |
| 110            | DC (PV) current 1                           | R              | [0,65535]       | 0.1A           |                                                                                                                 |
| 111            | DC (PV) voltage 2                           | R              | [0,65535]       | 0.1V           |                                                                                                                 |
| 112            | DC (PV) current 2                           | R              | [0,65535]       | 0.1A           |                                                                                                                 |
| 113            | DC (PV) voltage 3                           | R              | [0,65535]       | 0.1V           | Applies to 15K only                                                                                             |
| 114            | DC (PV) current 3                           | R              | [0,65535]       | 0.1A           | Applies to 15K only                                                                                             |
| 150            | Grid side voltage L1-N                      | R              |                 | 0.1V           |                                                                                                                 |
| 151            | Grid side voltage L2-N                      | R              |                 | 0.1V           |                                                                                                                 |
| 152            | Grid side voltage L1-L2                     | R              |                 | 0.1V           |                                                                                                                 |
| 153            | Voltage at middle side of relay L1-L2       | R              |                 | 0.1V           |                                                                                                                 |
| 154            | Inverter output voltage L1-N                | R              |                 | 0.1V           |                                                                                                                 |
| 155            | Inverter output voltage L2 N                | R              |                 | 0.1V           |                                                                                                                 |
| 156            | Inverter output voltage L1 L2               | R              |                 | 0.1V           |                                                                                                                 |
| 157            | Load voltage L1                             | R              |                 | 0.1V           |                                                                                                                 |
| 158            | Load voltage L2                             | R              |                 | 0.1V           |                                                                                                                 |
| 160            | Grid side current L1                        | R              |                 | 0.01A          | Signed int                                                                                                      |
| 161            | Grid side current L2                        | R              |                 | 0.01A          | Signed int                                                                                                      |
| 162            | Grid external Limiter current L1            | R              |                 | 0.01A          | Signed int                                                                                                      |
| 163            | Grid external Limiter current L2            | R              |                 | 0.01A          | Signed int                                                                                                      |
| 164            | Inverter output current L1                  | R              |                 | 0.01A          | Signed int                                                                                                      |
| 165            | Inverter output current L2                  | R              |                 | 0.01A          | Signed int                                                                                                      |
| 166            | Gen or AC Coupled power input               | R              |                 | 1W             | As load output: Output P is positive As AC input: Input P is negative                                           |
| 167            | Grid side L1 power                          | R              |                 | 1W             | Signed int                                                                                                      |
| 168            | Grid side L2 power                          | R              |                 | 1W             | Signed int                                                                                                      |
| 169            | Total power of grid side L1-L2              | R              |                 | 1W             | Signed int &gt; 0 BUY &lt; 0 SELL                                                                               |
| 170            | Grid external Limter1 power (CT1)           | R              |                 | 1W             | Signed int                                                                                                      |
| 171            | Grid external Limter2 power (CT2)           | R              |                 | 1W             | Signed int                                                                                                      |
| 172            | Grid external Total Power                   | R              |                 | 1W             | Signed int                                                                                                      |
| 173            | Inverter outputs L1 power                   | R              |                 | 1W             | Signed int                                                                                                      |
| 174            | Inverter outputs L2 power                   | R              |                 | 1W             | Signed int                                                                                                      |
| 175            | Inverter output Total power                 | R              |                 | 1W             | Signed int                                                                                                      |
| 176            | Load side L1 power                          | R              |                 | 1W             | Signed int                                                                                                      |
| 177            | Load side L2 power                          | R              |                 | 1W             | Signed int                                                                                                      |
| 178            | Load side Total power                       | R              |                 | 1W             | Signed int                                                                                                      |
| 179            | Load current L1                             | R              |                 | 0.01A          | Signed int                                                                                                      |
| 180            | Load current L2                             | R              |                 | 0.01A          | Signed int                                                                                                      |
| 181            | Gen Port Voltage L1-L2                      | R              |                 | 0.1V           |                                                                                                                 |
| 182            | Battery temperature                         | R              | [0,3000]        | 0.1℃           | Real value of offset + 1000 1200 is 20.0 ℃                                                                      |
| 183            | Battery voltage                             | R              |                 | 0.01V          | 4100 mark of 41.0 V                                                                                             |
| 184            | Battery capacity SOC                        | R              | [0,100]         | 1%             |                                                                                                                 |
| 186            | PV1 input power                             | R              |                 | 1W             |                                                                                                                 |
| 187            | PV2 input power                             | R              |                 | 1W             |                                                                                                                 |
| 188            | PV3 input power                             | R              |                 | 1W             | Applies to 15K only                                                                                             |
| 189            | PV4 input power                             | R              |                 | 1W             |                                                                                                                 |
| 190            | Battery output power                        | R              |                 | 1W             | Signed int                                                                                                      |
| 191            | Battery output current                      | R              |                 | 0.01A          | Signed int                                                                                                      |
| 192            | Load frequency                              | R              |                 | 0.01Hz         |                                                                                                                 |
| 193            | Inverter output frequency                   | R              |                 | 0.01Hz         |                                                                                                                 |
| 194            | Grid side relay status                      | R              |                 |                | 1 is Open (Disconnect) 2 is Closed                                                                              |
| 195            | Generator side relay status                 | R              |                 |                | Low 4 indicates the state of generator relay 0 Open 1 Closed  2 No Connection 3 Closed when Generator is on.    |
| 196            | Generator relay Frequency                   | R              |                 | 0.01Hz         |                                                                                                                 |



| Fault Table | Fault Table | Fault Table                | Fault Table                                                                                                                                                                                                        |
|-------------|-------------|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Bit Value   | Fault Code  | Fault                      |                                                                                                                                                                                                                    |
| Bit 7       | F08         | GFDI_Relay_Failure         |                                                                                                                                                                                                                    |
| Bit 12      | F13         | Grid_Mode_changed          | Can happen when not using batteries or if Grid Input settings are changed. This is a notification, NOT a fault.                                                                                                    |
| Bit 13      | F14         | DC_OverCurr_Fault          |                                                                                                                                                                                                                    |
| Bit 14      | F15         | SW_AC_OverCurr_Fault       | Usually caused by Loads being too large for the inverter. If off-grid, the battery discharge amps programmed too low. Overloads can result in F15, F18, F20, or F26.                                               |
| Bit 15      | F16         | GFCI_Failure               | Ground fault. Check PV+ or PV- wiring (which must be ungrounded). Exposed PV conductors + rain can also cause. Check that neutral line and Ground is not double bonded (which is common with portable generators). |
| Bit 17      | F18         | HW_Ac_OverCurr_Fault       | Overloaded the Load Output, reduce loads. Wiring Short on the AC Side can also cause this error. Overloads can result in F15, F18, F20, or F26.                                                                    |
| Bit 19      | F20         | Tz_Dc_OverCurr_Fault       | Usually caused by DC current from battery that are too large (ex: 4 Ton AC Unit). Overloads can result in F15, F18, F20, or F26.                                                                                   |
| Bit 21      | F22         | Tz_EmergStop_Fault         | Contact Sol-Ark.com                                                                                                                                                                                                |
| Bit 22      | F23         | Tz_GFCI_OC_Fault           | PV Ground fault. Check PV+ or PV- wiring (which must be ungrounded or damage can occur). Typically caused by pinched PV wire grounding the PV+ or PV-. Grounded PV wire can cause F20, F23 or F26.                 |
| Bit 23      | F24         | DC_Insulation_ISO_Fault    | Exposed PV conductor combined with moisture is faulting (can cause F16, F24, F26).                                                                                                                                 |
| Bit 25      | F26         | BusUnbalance_Fault         | Too much load one leg (L1 or L2) Vs the other leg or DC loads on the AC output when off-grid. Grounded PV wire can cause F20, F23 or F26.                                                                          |
| Bit 28      | F29         | Parallel_Fault             | One or more Paralleled systems have error,                                                                                                                                                                         |
| Bit 32      | F33         | AC_OverCurr_Fault          |                                                                                                                                                                                                                    |
| Bit 33      | F34         | AC_Overload_Fault          |                                                                                                                                                                                                                    |
| Bit 40      | F41         | AC_WU_OverVolt_Fault       | Contact Sol-Ark.com                                                                                                                                                                                                |
| Bit 42      | F43         | AC_VW_OverVolt_Fault       |                                                                                                                                                                                                                    |
| Bit 44      | F45         | AC_UV_OverVolt_Fault       | Grid under voltage causes disconnect. This will self reset when grid stabilizes.                                                                                                                                   |
| Bit 45      | F46         | Parallel_Aux_Fault         | Cannot communicate with other parallel systems. Check Master = 1, Slaves are 2-9, ethernet cables are connected.                                                                                                   |
| Bit 46      | F47         | AC_OverFreq_Fault          | Grid over Frequency (common in power outages) causes disconnect. Will self-reset when grid stabilizes.                                                                                                             |
| Bit 47      | F48         | AC_UnderFreq_Fault         | Grid under Frequency (common in power outages) causes disconnect. Will self-reset when grid stabilizes.                                                                                                            |
| Bit 54      | F55         | DC_VoltHigh_Fault          | PV maybe higher than 500V. Battery voltage should not be above 59V or 63V (depending on model).                                                                                                                    |
| Bit 55      | F56         | DC_VoltLow_Fault           | Batteries are overly discharged or Lithium BMS has shutdown.                                                                                                                                                       |
| Bit 57      | F58         | AC_U_GridCurr_High_Fault   |                                                                                                                                                                                                                    |
| Bit 60      | F61         | Button_Manual_OFF          |                                                                                                                                                                                                                    |
| Bit 61      | F62         | AC_B_InductCurr_High_Fault |                                                                                                                                                                                                                    |
| Bit 62      | F63         | Arc_Fault                  | Can be a bad PV connector/connection. And sometimes a false alarm due to powerful lightning storms.                                                                                                                |
| Bit 63      | F64         | Heatsink_HighTemp_Fault    | Check the built-in fans are running, ambient temp may be to high                                                                                                                                                   |




