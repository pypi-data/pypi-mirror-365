# !/usr/bin/env python3
# -*- coding: utf-8 -*-

#*******************************************************************************
# File: __init__.py
# Package: AMFTools
# Description: This module is used to control the AMF products
# Date Created: August 21, 2023
# Date Modified: June 30, 2025
# Python Version: 3.11.4
# Dependencies: pyserial, ftd2xx
# License: All right reserved : Proprietary license (Advanced Microfluidics S.A.)
# Contact: info [at] amf.ch
#*******************************************************************************

__version__ = "0.1.9"
__author__ = 'AMF'
__credits__ = 'Advanced Microfluidics S.A.'

import time
import os
import serial
import serial.tools.list_ports
import re
import threading

#if windows
if os.name == 'nt':
    import ftd2xx


class Device:
    serialnumber : str = None
    comPort : str = None
    deviceType : str = None
    deviceFamily : str = None
    connectionMode : str = None
    productAddress : str = "_"

    def __str__(self) -> str:
        return f"Device {self.deviceType} on port {self.comPort} with serial number {self.serialnumber} and connected by {self.connectionMode}"


class AMF:
    
    TIME_BETWEEN_COMMAND = 0.1  # Delay after sending a command
    serialNumber : str = None
    firmwareVersion : str = None
    serialPort : str = None     # Port to connect
    serialBaudrate : int = 9600
    serialTimeout : float = 1   # Timeout for the serial read function  
    productAddress : str = "_"
    productserial : serial.Serial = None
    connected : bool = False
    connectionMode : str = "USB/RS232"
    portnumber : int = None     #Number of valve ports
    typeProduct : str = None
    syringeSize : int = None
    responseTimeout : float = 1   # Timeout for the receive function      
    pumpSpeed : int = None
    pumpSpeedMode : int = None
    answerMode : int = 0
    valveSpeed : str = None
    acceleration : int = None
    deceleration : int = None
    microstepResolution : int = None
    valvePosition : int = None
    no_ans : bool = False
    address_range : list = ["1","2","3","4","5","6","7","8","9","A","B","C","D","E"]
    shared_serial : serial.Serial = None
    shared_serial_ref_count : int = 0
    productFamily : str = None
    maxcountError = 2   # Max allowed number of communication errors

    FIRST_CHAR = '/'
    LAST_CHAR = '\r'

    # =============================================================================
    # Global Serial Lock for RS485 thread-safe communication
    # =============================================================================
    # RS485 is a shared bus protocol, meaning only one device should communicate
    # on the bus at any given time.
    #
    # In this library, multiple AMF devices may attempt to send()
    # or receive() commands in parallel (via threads for instance).
    #
    # To prevent collisions or corrupted responses, we introduce a global
    # RLock (Reentrant Lock) named `serial_lock`, which ensures that only one
    # device at a time accesses the RS485 bus. While threads cannot acquire the RLock simultaneously, 
    # the order in which they acquire it is non-deterministic when no condition variables or queuing logic are in place.
    # 
    # This allows us to safely use the standard amfTools functions
    # (e.g., pump(), valveMove(), send(), receive(), etc.) even in multi-device
    # RS485 contexts — no need to rewrite all function calls.
    #
    # ➤ This lock is acquired automatically inside all send/receive functions.
    # ➤ It ensures compatibility with existing blocking commands (e.g. pullAndWait).
    #
    # WARNING: Never use direct threading or parallel communication without this lock, 
    # omitting the lock may result in data collisions or message corruption due to concurrent access.
    # =============================================================================
    
    serial_lock = threading.RLock()  # Global lock for all RS485 accesses


    functions = {
        'setAddress' : "@ADDR=#R", #Define the Address of the product
        'setAnswerMode' : "!50#", #Define the answer mode of the product
        'setPortNumber' : "!80#", #Set the port number of the product
        'setPlungerForce' : "!30#", #Set the plunger force (only for SPM and LSPone)
        'slowMode' : "-R", #Set the slow mode (only for the RVMFS)
        'fastMode' : "+R", #Set the fast mode (only for the RVMFS)
        'getCurrentStatus' : "Q", #Get the current status of the product
        'getRealPlungerPosition' : "?4", #Get the real plunger position (only for SPM and LSPone)
        'getPlungerPosition' : "?0", #Get the plunger position (only for SPM and LSPone)
        'getSpeedPump' : "?2", #Get the maximum pump speed (unit changes with speed mode) (only for SPM and LSPone)
        'getSpeedModePump' : "?5", #Get the speed mode of the pump
        'getValvePosition' : "?6", #Get the valve position
        'getNumberValveMovements' : "?17", #Get the number of valve movements
        'getNumberValveMovementsSinceLastReport' : "?18", #Get the number of valve movements since last call
        'getSpeedModeValve' : "?19", #Get the valve speed mode
        'getFirmwareChecksum' : "?20", #Get the firmware checksum
        'getFirmwareVersion' : "?23", #Get the firmware version
        'getAcceleration' : "?25", #Get the acceleration slope setting (only for SPM and LSPone)
        'getAddress' : "?26", #Get the product address
        'getDeceleration' : "?27", #Get the deceleration slope setting (only for SPM and LSPone)
        'getMicrostepResolution' : "?28", #Get the microstep mode (only for SPM and LSPone)
        'getProductConfiguration' : "?76", #Get the product configuration
        'getPlungerCurrent' : "?300", #Get the plunger current (only for SPM and LSPone)
        'getReductionRatio' : "?333", #Get the pump motor reduction ratio
        'getAnswerMode' : "?500", #Get the answer mode
        'getPortNumber' : "?801", #Get the number of valve ports
        'internalReset' : "$", #Restart the product
        'getSupplyVoltage' : "*", #Get the supply voltage
        'getUniqueID' : "?9000", #Get the unique ID
        'getHomedSPM' : "?9010", #Get the homed status (only for SPM and LSPone)
        'getPumpStatus' : "?9100", #Get the pump status (only for SPM and LSPone)
        'getValveStatus' : "?9200", #Get the valve status
        'executeLastCommand' : "XR", #Execute the last command
        'delay' : "M#R", #Delay in ms
        'home' : "ZR", #Move to the home position
        'forceAndHome' : "Z#R", #Home with a specific plunger force
        'enforcedShortestPath' : "B#R", #Move to the shortest path, make 360° clockwise if target port is the current position
        'shortestPath' : "b#R", #Move to the shortest path no move if target port is the current position
        'enforcedIncrementalMove' : "I#R", #Move to the clockwise path make 360° if target port is the current position
        'incrementalMove' : "i#R", #Move to the clockwise path. No move if target port is the current position
        'enforcedDecrementalMove' : "O#R", #Move to the counter-clockwise path make 360° if target port is the current position
        'decrementalMove' : "o#R", #Move to the counter-clockwise path. No move if target port is the current position
        'hardStop' : "T", #Stop the pump (only for SPM and LSPone)
        'powerOff' : "@POWEROFFR", #Power off the product (only for SPM and LSPone)
        'RS232' : "@RS232R", #Activate RS232 communication or serial-over-USB communication (activated by default)and deactivate RS485 communication
        'RS485' : "@RS485FR", #Activate RS485 communication (RS485 will not work if the mini USB cable remains plugged in)
        'absolutePumpPosition' : "A#R", #Set the pump absolute position (only for SPM and LSPone)
        'pumpPickup' : "P#R", #pump relative pickup (only for SPM and LSPone)
        'pumpDispense' : "D#R", #pump relative dispense (only for SPM and LSPone)
        'setSpeed' : "V#R", #Set the pump speed (only for SPM and LSPone)
        'setSpeedLowFlow' : "U#R", #Set the pump speed for low flow rate (only for SPM and LSPone)
        'setSpeedUltraLowFlow' : "u#R", #Set the pump speed for ultra low flow rate (only for SPM and LSPone)
        'setSpeedCode' : "S#R", #Set the pump speed with code set on the operating manual 6.2 table (only for SPM and LSPone)
        'setAcceleration' : "L#R", #Set the pump acceleration rate step/s² (only for SPM and LSPone) 
        'setDeceleration' : "l#R", #Set the pump deceleration rate step/s² (only for SPM and LSPone)
        'setMicrostepResolution' : "N#R", #Set the pump resolution mode (only for SPM and LSPone)
    }

    ERROR_CODES = {'@': [0, 'No Error'],
                "`": [0, 'No Error'],
                'A': [1, 'Initialization'],
                'B': [2, 'Invalid command'],
                'C': [3, 'Invalid operand'],
                'D': [4, 'Missing trailing [R]'],
                'G': [7, 'Device not initialized'],
                'H': [8, 'Internal failure (valve)'],
                'I': [9, 'Plunger overload'],
                'J': [10, 'Valve overload'],
                'K': [11, 'Plunger move not allowed'],
                'L': [12, 'Internal failure (plunger)'],
                'N': [14, 'A/D converter failure'],
                'O': [15, 'Command overflow'], }

    VALVE_ERROR = {
        '255': [255, 'Busy', 'Valve currently executing an instruction.'],
        '0': [0, 'Done', 'Valve available for next instruction.'],
        '128': [128, 'Unknown command', 'Check that the command is written properly'],
        '144': [144, 'Not homed', 'You forgot the homing! Otherwise, check that you have the right port configuration and try again.'],
        '224': [224, 'Blocked', 'Something prevented the valve to move.'],
        '225': [225, 'Sensor error', 'Unable to read position sensor. This probably means that the cable is disconnected.'],
        '226': [226, 'Missing main reference', ('Unable to find the valve\'s main reference magnet '
                                                'during homing. This can mean that a reference magnet '
                                                'of the valve is bad/missing or that the motor is '
                                                'blocked during homing. Please also check motor '
                                                'cables and crimp.')],
        '227': [227, 'Missing reference', ('Unable to find a valve\'s reference magnet during '
                                            'homing. Please check that you have the correct valve '
                                            'number configuration with command "/1?801". If '
                                            'not, change it according to the valve you are working '
                                            'with. This can also mean that a reference magnet of '
                                            'the valve is bad/missing or that the motor is blocked '
                                            'during homing.')],
        '228': [228, 'Bad reference polarity', ('One of the magnets of the reference valve has a bad '
                                                'polarity. Please check that you have the correct valve '
                                                'number configuration with command "/1?801". If '
                                                'not, change it according to the valve you are working '
                                                'with. This can also mean that a reference magnet has '
                                                'been assembled in the wrong orientation in the valve.')],
        '231': [231, 'Valve Overpressure', ('Valve overpressure occured, a valve maintenance is required. '
                                            'Contact support@amf.ch for further information.')],
    }

    PUMP_ERROR = {
        '255': [255, 'Busy', 'Pump currently executing an instruction.'],
        '0': [0, 'Done', 'Pump available for next instruction.'],
        '128': [128, 'Unknown command', 'Check that the command is written properly'],
        '138': [138, 'Move Aborted', 'Last move interrupted with a hardstop'],
        '144': [144, 'Not homed', 'You forgot the homing! Otherwise, check that you have the right port configuration and try again.'],
        '145': [145, 'Move out of range', 'You\'re probably trying to perform a relative positioning and are too close to the limits.'],
        '146': [146, 'Speed out of range', 'Check the speed that you\'re trying to go at.'],
        '224': [224, 'Blocked', 'Something prevented the pump to move.'],
        '225': [225, 'Sensor error', 'Unable to read position sensor. This probably means that the cable is disconnected.'],
        '227': [227, 'Position drift', 'Position drift.'],
    }
       
    SERIAL_TYPE_MAPPING = {
    "P100-L": "LSPone",
    "P100-O": "SPM",
    "P101-L": "LSPone+",
    "P101-O": "SPM+",
    "P110-L": "LSPone HD",
    "P110-O": "SPM HD",
    "P111-L": "LSPone+ HD",
    "P111-O": "SPM+ HD",
    "P200-O": "RVMLP",
    "P201-O": "RVMFS",
    }
    
    FAMILY_MAPPING = {
    "RVMLP": "RVMLP",
    "RVMFS": "RVMFS",
    "SPM": "Pump",
    "LSP": "Pump",         
    }
    

    def __init__(self, product, autoconnect=True, portnumber: int = None, syringeVolume: int = None,
                 productAddress: str = None, typeProduct: str = None, connectionMode: str = None, ) -> None:
        """
        Initialize the AMF object. Product must be specified.
    
        INPUTS:
            product: str or Device - Can be a Device object, a serial number, or a COM port string
            autoconnect: bool - If True, attempt to open connection immediately
            portnumber: int - Valve number of ports
            syringeVolume: int - Syringe size in µL
            productAddress: str - Address of the device. By default "_" to broadcast (no answer will be returned in RS485 mode)
            typeProduct: str - Product type (LSPone, SPM, RVMFS...)
            connectionMode: str - "USB/RS232" or "RS485" (If RS485 mode, shared serial connection will be automatically configured)
        """
        
        # Prepare the internal function dictionary
        # We add lowercase keys
        fun = self.functions.copy()
        for key, value in fun.items():
            self.functions[key.lower()] = value
        
        # Parse the 'product' input as a Device
        if isinstance(product, Device):
            device = product
            self.serialNumber = device.serialnumber
            self.serialPort = device.comPort
            self.typeProduct = device.deviceType
            self.connectionMode = device.connectionMode
            self.productAddress = device.productAddress
                
        elif isinstance(product, str):
            #If serial port is specified
            if product.upper().startswith('COM') or 'dev/tty' in product.lower() or 'dev/cu' in product.lower():                  
                serialPort = product
                serialNumber = None
                device = None
            else: # Serial number is specified
                serialNumber = product
                serialPort = None
                device = None
        else:
            raise ValueError("Invalid 'product' parameter: must be a Device or str")
            
        # Determine serial port or serial number if either is specified
        if device is None:
            if serialPort is not None:
                self.serialPort = serialPort
                try:
                    self.serialNumber = self.getSerialNumber()
                except Exception as e:
                    print(f"Warning: {e}")

            elif serialNumber is not None:
                self.serialNumber = serialNumber
                self.serialPort = self.getSerialPort()
            else:
                raise ConnectionError("No serial port, serial number, or device specified")
    
        # Optional configuration parameters
        if portnumber is not None:
            if not isinstance(portnumber, int) or portnumber < 1 or portnumber > 48:
                print("Unsupported number of ports. Ignoring this parameter")
            else:            
                self.portnumber = portnumber
                
        if syringeVolume is not None:
            if not isinstance(syringeVolume, int) or syringeVolume < 0 or syringeVolume > 5000:
                print("Unsupported syringe size. Ignoring this parameter")
            else:
                self.syringeSize = syringeVolume    
              
        if productAddress is not None:
            if productAddress in self.address_range:
                self.productAddress = productAddress
            else:
                print("Unsupported address specified. Using broadcast address ('_')")
            
        if typeProduct is not None:
            self.typeProduct = typeProduct

        if self.typeProduct is not None:
            # Automatically set product family based on typeProduct
            for key, fam in self.FAMILY_MAPPING.items():
                if key in self.typeProduct:
                    self.productFamily = fam
                    break
            else:
                self.productFamily = "Unknown"
                print("Warning: unknown product type specified")
                
        # Define mode if not explicitly set from Device
        if connectionMode is not None:
            if "USB"  in connectionMode.upper() or "RS232"  in connectionMode.upper():                
                self.connectionMode = "USB/RS232"
            elif "RS485" in connectionMode.upper():
                self.connectionMode = "RS485"
            else:
                print("Unsupported connection mode specified. Using default mode (USB/RS232)")
        
        # Open the connection unless already handled via RS485 auto mode
        if autoconnect:
            self.connect()
            

    def connect(self, serialTimeout: float = serialTimeout) -> bool:
        """
        Establish a connection to the device.
        """
        try:
            self.disconnect()  # In case of a previous connection
        except:
            pass
            
        if serialTimeout is not None: self.serialTimeout = serialTimeout
    
        if self.serialPort is None and self.serialNumber is not None:
            self.serialPort = self.getSerialPort()
        elif self.serialPort is None:
            raise ConnectionError("No serial port or serial number specified")
    
        # Reuse shared RS485 connection if available
        # This function won't work on multiple RS485 cables connected in parallel
        if (self.connectionMode == "RS485" and AMF.shared_serial and 
            AMF.shared_serial.is_open and AMF.shared_serial.port == self.serialPort):            
            self.productserial = AMF.shared_serial
            AMF.shared_serial_ref_count += 1
            self.connected = True
    
        else:
            # Open new serial connection (shared or not)
            try:
                serial_obj = serial.Serial(self.serialPort, self.serialBaudrate, timeout=self.serialTimeout)
                self.productserial = serial_obj
        
                #  Create a shared serial object in case RS485 mode is used
                if self.connectionMode == "RS485":
                    AMF.shared_serial = serial_obj
                    AMF.shared_serial_ref_count = 1
                self.connected = True
                
            except serial.SerialException as e:
                self.connected = False
                raise ConnectionError(f"Could not connect to product on port {self.serialPort}: {e}")
            except Exception as e:
                raise Exception(e)
        
        if self.typeProduct is None:
            self.getType()
            
        if self.portnumber is None:
            self.portnumber = self.getPortNumber()
        else: 
            self.setPortNumber(self.portnumber)
        
        return True
    
    
    def disconnect(self) -> None:
        """
        Disconnect from the product.
        """
        try : 
            if self.connected and self.productserial:
                if self.productserial == AMF.shared_serial:
                    AMF.shared_serial_ref_count -= 1
                    if AMF.shared_serial_ref_count < 1:
                        AMF.shared_serial.close()
                        AMF.shared_serial = None
                        AMF.shared_serial_ref_count = 0
                else:
                    self.productserial.close()
            self.connected = False
    
        except Exception as e:
            print(f"Warning: Failed to disconnect: {e}")
    

    @staticmethod
    def close_shared_serial()->None:
        """
        Close the serial connection for RS485 mode
        """
        if AMF.shared_serial:
            try:
                AMF.shared_serial.close()
                AMF.shared_serial = None
                AMF.shared_serial_ref_count = 0
            except:
                pass
               
    
    def send(self, command: str, data: bool = False, integer: bool = False, full_ans: bool = False, force_ans: bool = False) -> None:
        """
        Send a command to the product and returns its response.
    
        INPUTS:
            command: str # The full command to send. Ex: "/1ZR" for a homing
            data: bool # If True, remove the status bit from the product response
            integer: bool # If True, extract an int from the product response
            full_ans: bool # If True, the response will be returned as is, without removing the leading and trailing characters
            force_ans: bool # If True, returns the product repsonse even if the attribute no_ans is set to False
        OUTPUTS:
            str or int or None # Depends on flags
        """
        if not self.connected or not self.productserial:
            raise ConnectionError("Product is not connected")

        command = command + self.LAST_CHAR
        response = None

        # In RS485 mode, we use serial_lock to ensure shared serial is not used by another thread
        if self.connectionMode == "RS485":
            with AMF.serial_lock:
                self.productserial.reset_input_buffer()  # Clear input buffer BEFORE sending
                self.productserial.write(command.encode())
                
                if not self.no_ans or force_ans:
                    response = self.receive(data=data, integer=integer, full=full_ans)
        else:
            self.productserial.reset_input_buffer()  # Clear input buffer BEFORE sending
            self.productserial.write(command.encode())
            
            if not self.no_ans or force_ans:
                response = self.receive(data=data, integer=integer, full=full_ans)
                
        time.sleep(self.TIME_BETWEEN_COMMAND)
        
        if response is not None:
            return response

    
    def receive(self, data=False, integer=False, full=False) -> str:
        """
        Receive a response from the device.
    
        INPUTS:
            data: bool # If True, remove the status bit from the product response
            integer: bool # If True, extract an int from the product response
            full: bool # If True, the response will be returned as is, without removing the leading and trailing characters
        OUTPUTS:
            str or int # Response from the product
        """
        if not self.connected or self.productserial is None:
            raise ConnectionError("Attempted to read from device while not connected")
        
        response = ""
        timeout = time.time() + self.responseTimeout
        
        # In RS485 mode, we use serial_lock to ensure shared serial is not used by another thread
        if self.connectionMode == "RS485":
            with AMF.serial_lock:
                response = self.productserial.read_until(b"\r").decode("ascii", errors="ignore")
                
                while response == "" and time.time() < timeout:
                    response = self.productserial.read_until(b"\r").decode("ascii", errors="ignore")
                    if response.endswith('\r'):
                        break
                    time.sleep(0.1)
        else:
            response = self.productserial.read_until(b"\r").decode("ascii", errors="ignore")
            
            while response == "" and time.time() < timeout:
                response = self.productserial.read_until(b"\r").decode("ascii", errors="ignore")
                if response.endswith('\r'):
                    break
                time.sleep(0.1)            

        if response != "":
            if full:
                return response
            
            # Remove the leading and trailng characters
            response = response.replace("/0", "").replace("\x03", "").replace("\r", "").replace("\n", "")
            
            if data:
                try:
                    return response[1:] # Remove the status bit
                except Exception as e:
                    raise ValueError(f"Unable to extract data from '{response}': {e}")

            if integer:
                try:
                    match = re.search(r"\d+", response)      # Search the first number in the response string
                    if match:
                        val = int(match.group())
                        return val           
                    else:
                        raise ValueError(f"No numeric value found in response: '{response}'")
                except ValueError as e:
                    raise ValueError(f"Failed to convert response to integer: {e}")
                except Exception as e:
                    raise Exception(e)

            return response
        else:
            raise ConnectionError(f"No answer from the product on port {self.serialPort}. Check that the product is properly connected")


    def prepareCommand(self, command : str, parameter = None) -> str:
        """
        Function used to prepare the command to be sent for a function from the command set
        
        INPUTS:
            command: command function to send to the product
            parameter: value of the parameter
        OUTPUTS:
            formatted command, ready to be sent to the device
        """        
        preparedCommand : str = self.FIRST_CHAR + str(self.productAddress) + self.functions[command.lower()]
        
        if '#' in  preparedCommand and parameter is not None:
             preparedCommand =  preparedCommand.replace('#', str(parameter))
        elif '#' in  preparedCommand and parameter is None:
            raise ValueError("Command "+command+ " needs a parameter")
        return preparedCommand  
    
              
    def pullAndWait(self, homing_mode=False) -> None:
        """
        Wait for the product to be ready while checking its status 
        """
        valvebusy = True
        pumpbusy = True
        
        countError = 0
        
        while valvebusy or pumpbusy:
            try:
                time.sleep(self.TIME_BETWEEN_COMMAND*2)
                
                ##################### Checking Valve #####################
                if valvebusy :
                    responseValve = self.getValveStatus()
                    try : 
                        valve_status_code = self.VALVE_ERROR[str(responseValve)]
                    except KeyError:
                        raise KeyError(f"Unknown valve error code: {responseValve}")
                    except Exception as e:
                        raise Exception(e)
                        
                    if valve_status_code[0] == 0:
                        valvebusy = False
                        countError = 0
                    elif homing_mode and valve_status_code[0] == 144: #Valve may answer 144 during homing, we won't raise it as an issue during homing
                        valvebusy = True
                        countError = 0
                    elif valve_status_code[0] != 255: 
                        raise Exception("Valve error: "+str(valve_status_code[1]+": "+valve_status_code[2]))
                    else: 
                        valvebusy = True

                ##################### Checking Pump #####################
    
                if self.productFamily == "Pump":
                    if not homing_mode or not valvebusy:
                        if pumpbusy:
                            responsePump = self.getPumpStatus()
                            try : 
                                pump_status_code = self.PUMP_ERROR[str(responsePump)]
                            except KeyError: 
                                raise KeyError(f"Unknown pump error code: {responsePump}")
                            except Exception as e:
                                raise Exception(e)
                                
                            if pump_status_code[0] == 0:
                                pumpbusy = False
                                countError = 0
                            elif homing_mode and pump_status_code[0] == 144: #Pump may answer 144 during homing, we won't raise it as an issue during homing
                                pumpbusy = True
                                countError = 0
                            elif pump_status_code[0] == 138: #Pump may answer 138 if hardstop was used before
                                pumpbusy = True
                                countError = 0
                            elif pump_status_code[0] != 255:
                                raise Exception("Pump error: "+str(pump_status_code[1]+": "+pump_status_code[2]))
                            else:
                                pumpbusy = True
                                countError = 0
                else:
                    pumpbusy = False
                    if not valvebusy:
                        countError = 0
            except Exception as e:
                countError += 1
                if countError > self.maxcountError:
                    countError = 0
                    raise Exception(f"PullAndWait error: {e}")
                else:
                    #print(f"WARNING: PullAndWait error ({countError}/{self.maxcountError} allowed): {e}")
                    pass
        
    def __check_status__(self, response: str) -> None:
        """
        Check the status byte of a response from a product and raise an error if needed
        The response provided should come from the receive() function, with no arguments passed
        """
        if response and response != '':
            status_bit = response[0].upper()
            code = self.ERROR_CODES[status_bit]
            error_msg = f"Error: {code[1]} (error code: {response[0]})"
            if code[0] != 0:
                try:
                    self.checkValveStatus()
                except Exception as e:
                    error_msg += '\n' + str(e) 
                try:
                    self.checkPumpStatus()
                except Exception as e:
                    error_msg += '\n' + str(e) 
                    
                raise Exception(error_msg)
        else:
            raise Exception("Error when checking status: response is empty")
            
                    
############################################################################################################
#                                                                                                          #
#                                           LIST OF SET FUNCTIONS                                          #
#                                                                                                          #
############################################################################################################

    def setAddress(self, address: str) -> None:
        """
        Set product address (must be in [1–9, A–E])
        """
        address_range : list = ["1","2","3","4","5","6","7","8","9","A","B","C","D","E"]
        
        address = str(address).upper()
        if address not in address_range :
            raise ValueError("Address must be between 1 and 9 or between A and E")
        
        self.__check_status__(self.send(self.prepareCommand('setAddress', address)))
        self.productAddress = address

    def setAnswerMode(self, mode : int) -> None:
        """
        Answer mode [0; 2] 0: Synchronous, 1: Asynchronous, 2: Asynchronous with command count
        """
        if mode < 0 or mode > 2:
            raise ValueError("Mode must be between 0 and 2")
        
        self.__check_status__(self.send(self.prepareCommand('setAnswerMode', mode)))
        self.answerMode = mode

    def setPortNumber(self, portnumber : int = portnumber) -> None:
        """
        Number of ports of the valve
        """
        if portnumber < 1 or portnumber > 48:
            raise ValueError("Port number must be between 1 and 48")
            
        self.__check_status__(self.send(self.prepareCommand('setPortNumber', portnumber)))        
        self.portnumber = portnumber

    def setSpeed(self, speed : int) -> None:
        """
        Speed in 10 µm/s, [0; 1600] for standard series or [0;500] for HD variant
        """
        if self.productFamily != "Pump":
            raise ValueError("Set speed is only for SPM and LSPone")
            
        self.__check_status__(self.send(self.prepareCommand('setSpeed', speed)))
        self.pumpSpeed = speed
        self.pumpSpeedMode = 2

    def setSpeedLowFlow(self, speed : int) -> None:
        """
        Speed in 0.5 µm/s, [1;32000] for standard series of [1;10000] for HD variant
        """
        if self.productFamily != "Pump":
            raise ValueError("Set speed is only for SPM and LSPone")
        
        self.__check_status__(self.send(self.prepareCommand('setSpeedLowFlow', speed)))
        self.pumpSpeed = speed
        self.pumpSpeedMode = 1

    def setSpeedUltraLowFlow(self, speed : int) -> None:
        """
        Speed in 74.5 nm/s, [1;214750] for standard series, or speed in 5.52 nm/s, [1;905970] for HD variant
        """
        if self.productFamily != "Pump":
            raise ValueError("Set speed is only for SPM and LSPone")
        
        self.__check_status__(self.send(self.prepareCommand('setSpeedUltraLowFlow', speed)))
        self.pumpSpeed = speed
        self.pumpSpeedMode = 0

    def setFlowRate(self, flowRate : float, speedMode : int = 0,  syringeVolume: int = syringeSize) -> int:
        """
        Set the pump speed with a flow rate input in µl/min. It will be converted into a speed in pump units.
        As the pump only accept int as an input, the real flowrate may be slightly different.
        
        INPUTS:
            flowRate: Flow rate in µl/min [0; 160000]
            speedMode: 0 for ultraLow (u command), 1 for low (U command), 2 for standard (V command)
            syringeVolume: Syringe volume in µl [25; 5000]
        """

        if self.productFamily != "Pump":
            raise ValueError("Set flow rate is only for SPM and LSPone")
        if flowRate < 0:
            raise ValueError("Flow rate must be positive")
        
        if self.syringeSize is None or self.syringeSize < 25 or self.syringeSize > 5000:
            raise ValueError("Syringe volume must be between 25 and 5000")
            
        if syringeVolume != self.syringeSize and syringeVolume is not None:
            self.syringeSize = syringeVolume
        
        # Pump speed should be in pulse/s
        # There are 3000 pulses over the full syringe stroke
        # We divide by 60 to convert from pulses/min to pulses/s
        # speed_V_raw = flowRate * 3000 / (self.syringeSize*60)
        # We simplify 3000 / 60 by 50

        speed_V_raw = flowRate * 50 / self.syringeSize
        speed_V = int(speed_V_raw)
        
        # We also compute speed equivalent with U and u commands to have a better resolution
        speed_U = int(speed_V_raw*20)           # U speed is 20 times slower than V
        speed_u = int(speed_V_raw*134.217728)   # u speed is 134.22 time slower than V
        
        
        # Try using u command, then U, then V
        # Depending on the FW version, commands u and U may fail
        
        invalid_command = False
        
        if speedMode == 0:
            try:
                # We get the reducer value and we apply it to the u command
                reducer = self.getReductionRatio()
                self.setSpeedUltraLowFlow(int(speed_u*reducer))
            except Exception as e:
                if "invalid command" in str(e).lower():
                    # We will try using the setSpeedLowFlow function
                    speedMode = 1
                    invalid_command = True
                    print("Failed to use setSpeedUltraLowFlow function. Firmware upgrade is recommended")
                else:
                    raise Exception(e)
                    
        if speedMode == 1:
            try:
                self.setSpeedLowFlow(speed_U)
                if invalid_command:
                    print("Function setSpeedLowFlow used instead")
            except Exception as e:
                if "invalid command" in str(e).lower():
                    # We will try using the setSpeed function
                    speedMode = 2
                    invalid_command = True
                    print("Failed to use setSpeedLowFlow function. Firmware upgrade is recommended")
                else:
                    raise Exception(e)
                    
        if speedMode == 2:
            self.setSpeed(speed_V)
            if invalid_command:
                print("Function setSpeedLowFlow used instead")

    def setSyringeSize(self, volume : int) -> None:
        """
        Volume of the syringe in µL [25; 5000]
        Warning: this value is not stored in the product memory, it is just used by the python script to compute flow rate and volume
        """
        if volume < 25 or volume > 5000:
            raise ValueError("Volume must be between 25 and 5000")
        self.syringeSize = volume

    def setSpeedCode(self, speed : int) -> None:
        """
        Set speed using speed code table (see operating manual).
        speed in [10;40] for standard series, or speed in [16;40] for HD variant
        """
        if self.productFamily != "Pump":
            raise ValueError("Set speed code is only for SPM and LSPone")
        
        self.__check_status__(self.send(self.prepareCommand('setSpeedCode', speed)))
        
        # Update pump speed
        self.getSpeedPump()
       
    def setAccelerationRate(self, rate : int) -> None:
        """
        Acceleration rate in step/s² [100; 59590]
        """
        if self.productFamily != "Pump" :
            raise ValueError("acceleration rate is only for SPM and LSPone")
        if rate < 100 or rate > 59590:
            raise ValueError("Rate must be between 100 and 59590")
        self.__check_status__(self.send(self.prepareCommand('setAcceleration', rate)))
        self.acceleration = rate

    def setDecelerationRate(self, rate : int) -> None:
        """
        Deceleration rate in step/s² [100; 59590]
        """
        if self.productFamily != "Pump":
            raise ValueError("Deceleration rate is only for SPM and LSPone")
        if rate < 100 or rate > 59590:
            raise ValueError("Rate must be between 100 and 59590")
        self.__check_status__(self.send(self.prepareCommand('setDeceleration', rate)))
        self.deceleration = rate

    def setMicrostepResolution(self, argument : int) -> None:
        """
        Pump resolution mode: [0; 1] # 0 : 0.01mm resolution, 1 : 0.00125mm resolution
        """
        if self.productFamily != "Pump":
            raise ValueError("Scaling argument is only for SPM and LSPone")
        if argument < 0 or argument > 1:
            raise ValueError("Argument must be between 0 and 1")
        self.__check_status__(self.send(self.prepareCommand('setMicrostepResolution', argument)))
        self.microstepResolution = argument
 
    def setSlowMode(self) -> None:
        """
        Set the valve to slow mode
        """
        if self.productFamily != "RVMFS":
            raise ValueError("Slow mode is only for RVMFS")
        self.__check_status__(self.send(self.prepareCommand('slowMode')))
        self.valveSpeed = "Slow"
    
    def setFastMode(self) -> None:
        """
        Set the valve to fast mode
        """
        if self.productFamily != "RVMFS":
            raise ValueError("Fast mode is only for RVMFS")
        self.__check_status__(self.send(self.prepareCommand('fastMode')))
        self.valveSpeed = "Fast"
        
    def setRS232Mode(self) -> None:
        """
        Set communication mode to RS232
        """
        self.__check_status__(self.send(self.prepareCommand('RS232')))
        self.connectionMode = "USB/RS232"
    
    def setRS485Mode(self) -> None:
        """
        Set communication mode to RS485
        """
        self.__check_status__(self.send(self.prepareCommand('RS485')))
        self.connectionMode = "RS485"
    
    def setPumpStrengthAndHome(self, force : int, block : bool = True) -> None:
        """
        Set plunger force and home the pump 
        
        INPUTS:
            force: [0;3]: 0: high force, 1: normal force, 2: medium force, 3: low force
            block: If True, function will block until the product is ready for a new command
        """
        if self.productFamily != "Pump":
            raise ValueError("Force and home is only for SPM and LSPone")
        self.__check_status__(self.send(self.prepareCommand('forceAndHome', force)))

        if block: self.pullAndWait(homing_mode=True)
    
    def setPlungerForce(self, force : int) -> None:
        """
        Set plunger force
        
        INPUTS:
            force: [0;3]: 0: high force, 1: normal force, 2: medium force, 3: low force 
            block: If True, function will block until the product is ready for a new command
        """
        if self.productFamily != "Pump":
            raise ValueError("Plunger force is only for SPM and LSPone")
        self.__check_status__(self.send(self.prepareCommand('setPlungerForce', force)))

    def setNoAnswer(self, no_ans = True) -> None:
        """
        If True, disable answers for the AMF object (answers can be forced by using the force_ans parameter)
        """
        self.no_ans = no_ans


############################################################################################################
#                                                                                                          #
#                                           LIST OF GET FUNCTIONS                                          #
#                                                                                                          #
############################################################################################################

    def getSerialPort(self) -> str:
        """
        Find the serial port (ex: COM3) of the product with the specified serial number. 

        WARNING : With RS485/RS232 communication, the serial number is not the one of the AMF product but the one of the USB to RS232/RS485 device        
        """
        if self.serialPort is not None :         #If serial port already known, return it
            return self.serialPort 
            
        if self.connected:                              
            self.disconnect()
            
        if self.serialNumber is not None and self.serialNumber != '':
            if os.name == 'nt': #if windows
                list_available_device = ftd2xx.listDevices()                
                if list_available_device is not None:
                    for i in range(len(list_available_device)):
                        try:
                            if list_available_device[i].decode() == self.serialNumber:
                                device = ftd2xx.open(i)
                                comport = device.getComPortNumber()
                                device.close()
                                if comport is not None:
                                    self.serialPort = "COM" + str(comport)
                                    return self.serialPort
                        except:
                            pass
                            
            #If Linux/Lac or Windows & not an FTDI device
            list_com_port = serial.tools.list_ports.comports()
            for com in list_com_port:
                # On windows, the serial number given by serial.tools.list_ports will usually have an A at the end
                # If the SN includes an hyphen, the returned SN will be cut before the hyphen
                # Therefore we do not check equality but we check if one SN is included in the other one
                if os.name == 'nt':
                    if (com.serial_number and com.serial_number.upper() != '' and 
                    (self.serialNumber.upper() in com.serial_number.upper() or com.serial_number.upper() in self.serialNumber.upper())):
                        self.serialPort = com.device
                        return self.serialPort
                    
                elif com.serial_number == self.serialNumber:
                    self.serialPort = com.device
                    return self.serialPort

        raise ConnectionError(f"Could not find the serial port. Check that the serial number {self.serialNumber} exists")
            
        
    def getSerialNumber(self) -> str:
        """ 
        Get the serial number of the product connedcted to the specified port.
        
        WARNING: True product serial number (ex: P201-O12345678) is not reachable by RS232/RS485.
        With RS485/RS232 communication, the serial number is not the one of the AMF product but the one of the USB to RS232/RS485 device
        """
        if self.serialNumber is not None:
            return self.serialNumber
        
        if self.connected:                              
            self.disconnect()
            
        if self.serialPort is not None and self.serialPort != '': 
            if os.name == 'nt': #if windows
                list_available_device = ftd2xx.listDevices()
                if list_available_device is not None:
                    for i in range(len(list_available_device)):
                        try:
                            device = ftd2xx.open(i)
                            comport = device.getComPortNumber()
                            device.close()
                            if ("com"+str(comport)).lower().replace(" ", "") == self.serialPort.lower().replace(" ", ""):
                                self.serialNumber = list_available_device[i].decode()
                                return self.serialNumber
                        except:
                            pass
                        
            #If Linux/Lac or Windows & not an FTDI device
            list_com_port = serial.tools.list_ports.comports()
            for com in list_com_port:
                if com.device.lower().replace(" ", "") == self.serialPort.lower().replace(" ", ""):
                    self.serialNumber = com.serial_number
                    return self.serialNumber

        raise ConnectionError(f"Could not find serial number. Check that the port {self.serialPort} exists")    

    
    def getType(self) -> str:
        """
        Automatically determine and assign the type of product (LSPone, SPM, RVMFS...).           
        """  
            
        if self.serialNumber.startswith("P"):
            # Extract a pattern like P101-L from serial number
            match = re.match(r"^(P\d{3}-[LO])", self.serialNumber)
            if match:
                serial_prefix = match.group()
                if serial_prefix in self.SERIAL_TYPE_MAPPING:
                    self.typeProduct = self.SERIAL_TYPE_MAPPING[serial_prefix]
                    
                    # Assign product family based on type
                    for key, fam in self.FAMILY_MAPPING.items():
                        if key in self.typeProduct:
                            self.productFamily = fam
                            break
                    else:
                        self.productFamily = "Unknown"
                    return self.typeProduct

        if not self.connected:
            raise ConnectionError("Product is not connected")

        # Unable to get type from the SN, we check the product configuration instead
        response = self.send(self.prepareCommand('getProductConfiguration'), data=True, force_ans=True)

        if response is None or response == '':
            raise Exception("No response received from product")
    
        if "RVMFS" in response:
            self.typeProduct = "RVMFS"
        elif "LSP" in response:
            self.typeProduct = "SPM"
        elif "RVMLP" in response:
            self.typeProduct = "RVMLP"
        else :
            raise Exception(f"Unrecognized product type: '{response}'")
            
        # Assign product family based on type
        for key, fam in self.FAMILY_MAPPING.items():
            if key in self.typeProduct:
                self.productFamily = fam
                break
        else:
            self.productFamily = "Unknown"            
        return self.typeProduct

    def getPortNumber(self) -> int:
        """
        Number of valve ports
        """
        self.portnumber = self.send(self.prepareCommand('getPortNumber'), integer = True, force_ans=True)
        return self.portnumber
    
    def getCurrentStatus(self) -> str:
        """
        Current status of the product
        """
        return self.send(self.prepareCommand('getCurrentStatus'), force_ans=True)
    
    def getValvePosition(self) -> int:
        """
        Current valve position
        """
        return self.send(self.prepareCommand('getValvePosition'), integer = True, force_ans=True)
    
    def getNumberValveMovements(self) -> int:
        """
        Number of valve movements
        """
        return self.send(self.prepareCommand('getNumberValveMovements'), integer = True, force_ans=True)
    
    def getNumberValveMovementsSinceLastReport(self) -> int:
        """
        Number of valve movements since last report
        """
        return self.send(self.prepareCommand('getNumberValveMovementsSinceLastReport'), integer = True, force_ans=True)
    
    def getSpeedModeValve(self) -> str:
        """
        Valve speed mode ("Slow" or "Fast")
        """
        if self.productFamily != "RVMFS":
            raise ValueError("Speed mode is only for RVMFS")
        valveSpeed = self.send(self.prepareCommand('getSpeedModeValve'), force_ans=True)
        if "slow" in valveSpeed:
            self.valveSpeed = "Slow"
        elif "fast" in valveSpeed:
            self.valveSpeed = "Fast"
        return self.valveSpeed
    
    def getFirmwareChecksum(self) -> str:
        """
        Firmware checksum
        """
        return self.send(self.prepareCommand('getFirmwareChecksum'),data=True, force_ans=True)
        
    def getFirmwareVersion(self) -> str:
        """
        Firmware version
        """
        self.firmwareVersion = self.send(self.prepareCommand('getFirmwareVersion'),data=True, force_ans=True)
        return self.firmwareVersion  
    
    def getAddress(self) -> int:
        """
        Product communication address: [0;9] or [A;E]
        """
        self.productAddress = self.send(self.prepareCommand('getAddress'), data = True, force_ans=True)
        return self.productAddress
        
    def getProductConfiguration(self) -> int:
        """
        Product configuration
        """
        return self.send(self.prepareCommand('getProductConfiguration'),data=True, force_ans=True) 
    
    def getSpeedPump(self) -> int: 
        """
        Get pump speed (units depend on the pump speed mode)
        """
        if self.productFamily != "Pump":
            raise ValueError("Pump speed is only for SPM and LSPone")
        self.pumpSpeed = self.send(self.prepareCommand('getSpeedPump'), integer = True, force_ans=True)
        return self.pumpSpeed
    
    def getSpeedModePump(self) -> int: 
        """
        Speed mode of the pump [0;2]:
            0: Ultra low speed mode (speed unit: 74.5 nm/s for standard series or 5.52 nm/s for HD variant)
            1: Low speed mode (speed unit: 0.5 µm/s)
            2: Standard speed mode (speed unit: 10 µm/s)
        """
        if self.productFamily != "Pump":
            raise ValueError("Pump speed mode is only for SPM and LSPone")
        self.pumpSpeedMode = self.send(self.prepareCommand('getSpeedModePump'), integer = True, force_ans=True)
        return self.pumpSpeedMode
    
    def getFlowRate(self, syringeVolume: int = syringeSize) -> float:
        """
        Returns the flow rate, in µl/min
        
        INPUTS:
            syringeVolume: Syringe volume in µl [25; 5000]
        """
        
        if self.syringeSize is None or self.syringeSize < 25 or self.syringeSize > 5000:
            raise ValueError("Syringe volume must be between 25 and 5000")
        
        if syringeVolume != self.syringeSize and syringeVolume is not None:
            self.syringeSize = syringeVolume
        
        try:
            self.getSpeedModePump()
        except:
            # Assume speedMode = 2 with old firmwares
            if self.pumpSpeedMode is None:
                self.pumpSpeedMode = 2
            pass
        
        self.getSpeedPump()
        
        # Conversion formula is explained in setFlowRate function
        # If a command V was used to set the speed
        if self.pumpSpeedMode == 2:
            return round(self.pumpSpeed * self.syringeSize / 50, 4)
        
        # If a command U was used to set the speed
        elif self.pumpSpeedMode == 1:
            return round(self.pumpSpeed * self.syringeSize / (50 * 20), 4)
        
        # If a command u was used to set the speed
        elif self.pumpSpeedMode == 0:
            # We get the reducer value and we take it into account
            reducer = self.getReductionRatio()
            return round(self.pumpSpeed * self.syringeSize / (50 * 134.217728 * reducer), 4)
    
    def getSyringeSize(self) -> int:
        """
        Size of the syringe in µL
        Warning: this value is not stored in the product memory, it is just used by the python script to compute flow rate and volume
        """
        if self.syringeSize is None:
            print("Syringe size is not defined")
            
        return self.syringeSize
    
    def getMicrostepResolution(self) -> int:
        """
        Resolution mode: [0; 1] # 0: 0.01mm resolution, 1: 0.00125mm resolution
        """
        if self.productFamily != "Pump":
            raise ValueError("Microstep resolution is only for SPM and LSPone")
        self.microstepResolution = self.send(self.prepareCommand('getMicrostepResolution'), integer = True, force_ans=True)
        return self.microstepResolution
    
    def getPlungerCurrent(self) -> int:
        """
        Current x 10 mA (ex: 50 = 500 mA)
        """
        if self.productFamily != "Pump" :
            raise ValueError("Plunger current is only for SPM and LSPone")
        return self.send(self.prepareCommand('getPlungerCurrent'), integer = True, force_ans=True)
    
    def getReductionRatio(self) -> float:
        """
        Pump motor reduction ratio (1 for standard series, 13.5 for HD variant)
        """
        if self.productFamily != "Pump" :
            raise ValueError("Reduction ratio is only for SPM and LSPone")
        # We divide the received value by 100 to get the real reduction ratio
        return self.send(self.prepareCommand('getReductionRatio'), integer = True, force_ans=True)/100

    def getAnswerMode(self) -> str:
        """
        Answer mode (ex: Synchronous mode)"
        """
        return self.send(self.prepareCommand('getAnswerMode'),data=True, force_ans=True)

    def getAcceleration(self) -> int:
        """
        Pump motor acceleration value in step/s²
        """
        if self.productFamily != "Pump" :
            raise ValueError("Acceleration is only for SPM and LSPone")
        return self.send(self.prepareCommand('getAcceleration'), integer = True, force_ans=True)
    
    def getDeceleration(self) -> int:
        """
        Pump motor deceleration value in step/s²
        """
        if self.productFamily != "Pump" :
            raise ValueError("Deceleration is only for SPM and LSPone")
        return self.send(self.prepareCommand('getDeceleration'), integer = True, force_ans=True)

    def getSupplyVoltage(self) -> int:
        """
        Supply voltage x 0.1 V (ex: 180 = 18.0 V)
        """
        return self.send(self.prepareCommand('getSupplyVoltage'),integer=True, force_ans=True)
    
    def getUniqueID(self) -> str:
        """
        Product unique ID
        """
        time.sleep(0.1)
        return self.send(self.prepareCommand('getUniqueID'),data = True, force_ans=True)
    
    def getValveStatus(self) -> int:
        """
        Valve detailed status
        """
        return self.send(self.prepareCommand('getValveStatus'),integer = True, force_ans = True)
    
    def getPumpStatus(self) -> int:
        """
        Pump detailed status
        """
        if self.productFamily != "Pump":
            raise ValueError("Pump status is only for SPM and LSPone")
        return self.send(self.prepareCommand('getPumpStatus'), integer = True, force_ans = True)
    
    def getHomeStatus(self) -> bool:
        """
        Product homed status
        """
        if "RVM" in self.productFamily:
            resp = self.send(self.prepareCommand('getValvePosition'), integer = True, force_ans=True)
            if resp == 0:
                return False
            else:
                return True
        else:
            resp = self.send(self.prepareCommand('getHomedSPM'), integer = True, force_ans=True)
            if resp == 0:
                return False
            
            else:
                return True
            
    def getRealPlungerPosition(self) -> int:
        """
        Plunger position from the encoder ([0;3000] or [0;24000] depending on resolution mode)
        """
        if self.productFamily != "Pump":
            raise ValueError("Real plunger position is only for SPM and LSPone")
        return self.send(self.prepareCommand('getRealPlungerPosition'), integer = True, force_ans=True)
        
    
    def getPlungerPosition(self) -> int:
        """
        Theoretical plunger position
        """
        if self.productFamily != "Pump":
            raise ValueError("Plunger position is only for SPM and LSPone")
        return self.send(self.prepareCommand('getPlungerPosition'), integer = True, force_ans=True)
            
    def getDeviceInformation(self, full : bool = False ) -> dict:
        """
        Read device information (short or full)
        """
        info = {}
        
        try: info["serialNumber"] = self.getSerialNumber() 
        except : info["serialNumber"] = None
        try : info["serialPort"] = self.getSerialPort()
        except : info["serialPort"] = None
        try: info["typeProduct"] = self.getType()
        except : info["typeProduct"] = None
        try: info["portNumber"] = self.getPortNumber()
        except : info["portNumber"] = None
        try: info["productAddress"] = self.getAddress()
        except : info["productAddress"] = None
        try: info["currentStatus"] = self.getCurrentStatus()
        except : info["currentStatus"] = None
        try: info["homed"] = self.getHomeStatus()
        except : info["homed"] = None
        try: info["valveStatus"] = self.getValveStatus()
        except : info["valveStatus"] = None
        
        if self.productFamily == "RVMFS" :
            try: info["speedModeValve"] = self.getSpeedModeValve() 
            except : info["speedModeValve"] = None
        
        elif self.productFamily == "Pump":
            try: info["pumpStatus"] = self.getPumpStatus() 
            except : info["pumpStatus"] = None
        
        if full:           
            try: info["firmwareVersion"] = self.getFirmwareVersion()
            except : info["firmwareVersion"] = None
            try: info["valvePosition"] = self.getValvePosition()
            except : info["valvePosition"] = None
            try: info["productConfiguration"] = self.getProductConfiguration()
            except : info["productConfiguration"] = None
            try: info["numberValveMovements"] = self.getNumberValveMovements()
            except : info["numberValveMovements"] = None            
            try: info["numberValveMovementsSinceLastReport"] = self.getNumberValveMovementsSinceLastReport()
            except : info["numberValveMovementsSinceLastReport"] = None
            try: info["answerMode"] = self.getAnswerMode()
            except : info["answerMode"] = None

            if self.productFamily == "Pump":
                try: info["syringeSize"] = self.syringeSize 
                except : info["syringeSize"] = None
                try: info["pumpSpeed"] = self.getSpeedPump() 
                except : info["pumpSpeed"] = None
                try: info["pumpSpeedMode"] = self.getSpeedModePump() 
                except : info["pumpSpeedMode"] = None
                try: info["plungerPosition"] = self.getPlungerPosition() 
                except : info["plungerPosition"] = None
                try: info["realPlungerPosition"] = self.getRealPlungerPosition() 
                except : info["realPlungerPosition"] = None
                try: info["microstepResolution"] = self.getMicrostepResolution() 
                except : info["microstepResolution"] = None
                try: info["plungerCurrent"] = self.getPlungerCurrent() 
                except : info["plungerCurrent"] = None            
                try : info['acceleration'] = self.getAcceleration() 
                except : info['acceleration'] = None
                try : info['deceleration'] = self.getDeceleration() 
                except : info['deceleration'] = None
                
            try: info["uniqueID"] = self.getUniqueID()
            except : info["uniqueID"] = None
            try: info["firmwareChecksum"] = self.getFirmwareChecksum()
            except : info["firmwareChecksum"] = None
            try : info['Supply Voltage'] = self.getSupplyVoltage()
            except : info['Supply Voltage'] = None
            
        return info


############################################################################################################
#                                                                                                          #
#                                          GLOBAL ACTION FUNCTIONS                                         #
#                                                                                                          #
############################################################################################################
             
    def checkValveStatus(self) -> str:
        """
        Check the valve status and returns it with its description. Raise an error if the valve is in an error state.
        """
        response = self.getValveStatus()
        try : 
            status = self.VALVE_ERROR[str(response)]
        except KeyError:
            raise KeyError(f"Unknown valve error code: {response}")
        except Exception as e:
            raise Exception(e)
        
        # We check the status and raise an error if it's not 'Done' or 'Busy'
        if status[1] == 'Done' or status[1] == 'Busy':
            return status
        else:
            raise ValueError(f"Valve error: {status}")

    def sendBrute(self, command : str, block : bool = True, force_ans : bool = False) -> None:
        """
        Send raw command to the product
        
        INPUTS:
            command: Command to send (ex: ZR for a homing)
            block: If True, function will block until the product is ready for a new command
            force_ans: If True, returns the product repsonse even if the attribute no_ans is set to False
        """
        if self.connected:
            preparedCommand : str = self.FIRST_CHAR + str(self.productAddress) + command
            ans = self.send(preparedCommand, force_ans=force_ans)
            if not self.no_ans or force_ans:    
                self.__check_status__(ans)
            if block :
                self.pullAndWait()
            if not(self.no_ans) or force_ans:
                return ans
        else:
            raise ConnectionError("Product is not connected")

    def internalReset(self, block : bool = True) -> None:
        """
        Restart the product
        
        INPUTS:
            block: If True, function will block until the product is ready for a new command
        """
        self.send(self.prepareCommand('internalReset'))
        if block:
            time.sleep(0.2)

    def executeLastCommand(self, block : bool = True) -> None:
        """
        Execute last command again
        
        INPUTS:
            block: If True, function will block until the product is ready for a new command
        """
        self.send(self.prepareCommand('executeLastCommand'))
        if block :
            self.pullAndWait()
            
    def delay(self, delay : int, block : bool = True) -> None:
        """
        Ask the product to wait for some time in ms [0; +inf]
        """
        if delay < 0:
            raise ValueError("Delay must be positive")
        self.__check_status__(self.send(self.prepareCommand('delay', delay)))
        if block :
            time.sleep(delay/1000)
        
    def home(self, block= True) -> None:
        """
        Perform a homing of the product. The valve will be positonned on port 1 in case of success
        
        INPUTS:
            block: If True, function will block until the product is ready for a new command
        """
        self.__check_status__(self.send(self.prepareCommand('home')))
        if block: self.pullAndWait(homing_mode=True)

    def valveShortestPath(self, target: int, enforced : bool = False, block : bool = True) -> None:
        """
        Move to the target port using the shortest path
        
        INPUTS:
            target:  Target port [1; nbPorts]
            enforced: Force movement
            block: If True, function will block until the product is ready for a new command
        """
        if target < 1 or target > self.portnumber:
            raise ValueError("Target must be between 1 and "+str(self.portnumber))
        if enforced:
            self.__check_status__(self.send(self.prepareCommand('enforcedShortestPath', target)))
        else:
            self.__check_status__(self.send(self.prepareCommand('ShortestPath', target)))
        
        if block: self.pullAndWait()
    
    def valveIncrementalMove(self, target: int, enforced : bool = False, block : bool = True) -> None:
        """
        Move to the target port using incremental rotation 
        
        INPUTS:
            target:  Target port [1; nbPorts]
            enforced: Force movement
            block: If True, function will block until the product is ready for a new command
        """
        if target < 1 or target > self.portnumber:
            raise ValueError("Target must be between 1 and "+str(self.portnumber))
        if enforced:
            self.__check_status__(self.send(self.prepareCommand('enforcedIncrementalMove', target)))
        else:
            self.__check_status__(self.send(self.prepareCommand('incrementalMove', target)))

        if block: self.pullAndWait()
    
    def valveDecrementalMove(self, target: int, enforced : bool = False, block : bool = True) -> None:
        """
        Move to the target port using decremental rotation
        
        INPUTS:
            target:  Target port [1; nbPorts]
            enforced: Force movement
            block: If True, function will block until the product is ready for a new command
        """
        if target < 1 or target > self.portnumber:
            raise ValueError("Target must be between 1 and "+str(self.portnumber))
        if enforced:
            self.__check_status__(self.send(self.prepareCommand('enforcedDecrementalMove', target)))
        else:
            self.__check_status__(self.send(self.prepareCommand('decrementalMove', target)))

        if block: self.pullAndWait()

    def valveMove(self, target: int, mode:int = 0, enforced: bool = False, block : bool = True):
        """
        Move the valve to the target port
        
        INPUTS:
            target: Target port [1; nbPorts]
            mode: 0: ShortestPath, 1: IncrementalMove, 2: DecrementalMove
            enforced: Force movement
            block: If True, function will block until the product is ready for a new command
        """
        if mode == 0:
            self.valveShortestPath(target, enforced, block)
        elif mode == 1:
            self.valveIncrementalMove(target, enforced, block)
        elif mode == 2:
            self.valveDecrementalMove(target, enforced, block)
        else:
            raise ValueError("Mode must be between 0 and 2")
        
        if block: self.pullAndWait()
              
    def valveMoveBy(self, delta_ports: int, shortest_path: bool = True, enforced: bool = False, block: bool = True) -> None:
        """
        Move the valve by a relative number of ports, optionally forcing rotation direction.
    
        INPUTS:
            delta_ports: Number of ports to move, should not exceed valve port number (+ for incremental, - for decremental)
            shortest_path: use shortest path move (valve may move in incemental direction even if a negative delta_ports is given)
            enforced: Force movement
            block: If True, function will block until the product is ready for a new command
        OUTPUTS:
            None
        """
        current_port = self.getValvePosition()
        total_ports = self.portnumber
        
        mode = 0
        if not shortest_path and delta_ports > 0:
            mode = 1
        elif not shortest_path and delta_ports < 0:
            mode = 2
    
        new_port = (current_port + delta_ports) % total_ports
        if new_port == 0:
            new_port = total_ports
        
        self.valveMove(new_port, mode = mode, enforced=enforced, block=block)

    def hardStop(self) -> None:
        """
        Stop the product
        """       
        self.send(self.prepareCommand('hardStop'))
        

############################################################################################################
#                                                                                                          #
#                                           PUMP ACTION FUNCTIONS                                          #
#                                                                                                          #
############################################################################################################

    def checkPumpStatus(self) -> None:
        """
        Check the pump status and returns it with its description. Raise an error if the pump is in an error state.
        """
        response = self.getPumpStatus()
        try : 
            status = self.PUMP_ERROR[str(response)]
        except KeyError: 
            raise KeyError(f"Unknown pump error code: {response}")
        except Exception as e:
            raise Exception(e)
        
        # We check the status and raise an error if it's not 'Done' or 'Busy'
        if status[1] == 'Done' or status[1] == 'Busy':
            return status
        else:
            raise ValueError(f"Pump error: {status}")
            
    def pumpAbsolutePosition(self, position : int, block : bool = True) -> None:
        """
        Move the plunger to target position (absolute move)
        
        INPUTS:
            position: target position in pump units [0;3000] or [0;24000] depending on the resolution mode
            block: If True, function will block until the product is ready for a new command
        """
        if self.productFamily != "Pump":
            raise ValueError("Absolute pump position is only for SPM and LSPone")
        self.__check_status__(self.send(self.prepareCommand('absolutePumpPosition', position)))

        if block: self.pullAndWait()
    
    def pump(self, position : int, block : bool = True) -> None:
        """
        Same as pumpAbsolutePosition
        """
        self.pumpAbsolutePosition(position, block = block)

    def pumpVolume(self, volume : int, syringeVolume: int = syringeSize, block : bool = True) -> None:
        """
        Move the pump until the syringe contains the target volume
        pumpVolume(0) will empty the syringe
        pumpVolume(self.syringeSize) will fill the syringe
        
        INPUTS:
            volume: target volume inside the syringe in µL
            syringeVolume: volume of the syringe mounted on the pump in µL
            block: If True, function will block until the product is ready for a new command

        """
        if syringeVolume != self.syringeSize and syringeVolume is not None:
            self.syringeSize = syringeVolume
        if self.syringeSize == None: raise ValueError("Syringe volume must be specified")
        if self.microstepResolution == None: self.getMicrostepResolution()
        if self.microstepResolution == 0:
            to_pump = int(volume * 3000 / self.syringeSize)
        else:
            to_pump = int(volume * 24000 / self.syringeSize)
        self.pumpAbsolutePosition(to_pump, block = block)

    def pumpPickup(self, move_length : int, block : bool = True) -> None:
        """
        Make a relative pickup. The target position is equal to current position + move_length
        
        INPUTS:
            move_length: move length in pump units. Target position must be in [0;3000] or [0;24000] depending on the resolution mode
            block: If True, function will block until the product is ready for a new command
        """
        if self.productFamily != "Pump":
            raise ValueError("Relative pump pickup is only for SPM and LSPone")
        self.__check_status__(self.send(self.prepareCommand('pumpPickup', move_length)))

        if block: self.pullAndWait()
        
    def pumpRelativePickup(self, move_length : int, block : bool = True) -> None:
        """
        Same as pumpPickup

        """
        self.pumpPickup(move_length, block = block)

    def pumpPickupVolume(self, volume : int, syringeVolume: int = syringeSize, block : bool = True) -> None:
        """
        Make a relative pickup, defined with a volume in µL
        
        INPUTS:
            volume: volume to pickup in µL [0;self.syringeSize]
            syringeVolume: volume of the syringe mounted on the pump in µL
            block: If True, function will block until the product is ready for a new command
        """
        if syringeVolume != self.syringeSize and syringeVolume is not None:
            self.syringeSize = syringeVolume
        if self.syringeSize == None: raise ValueError("Syringe volume must be specified")
        if self.microstepResolution == None: self.getMicrostepResolution()
        if self.microstepResolution == 0:
            to_pickup = int(volume * 3000 / self.syringeSize)
        else:
            to_pickup = int(volume * 24000 / self.syringeSize)
        
        self.pumpPickup(to_pickup, block = block)
    
    def pumpDispense(self, move_length : int, block : bool = True) -> None:
        """
        Make a relative dispense. The target position is equal to current position - move_length
        
        INPUTS:
            move_length: move length in pump units. Target position must be in [0;3000] or [0;24000] depending on the resolution mode
            block: If True, function will block until the product is ready for a new command
        """
        if self.productFamily != "Pump":
            raise ValueError("Relative pump dispense is only for SPM and LSPone")
        self.__check_status__(self.send(self.prepareCommand('pumpDispense', move_length)))
        if block: self.pullAndWait()
        
    def pumpRelativeDispense(self, move_length : int, block : bool = True) -> None:
        """
        Same as pumpDispense

        """
        self.pumpDispense(move_length, block = block)

    def pumpDispenseVolume(self, volume : int, syringeVolume: int = syringeSize, block : bool = True) -> None:
        """
        Make a relative dispense, defined with a volume in µL
        
        INPUTS:
            volume: volume to dispense in µL [0;self.syringeSize]
            syringeVolume: volume of the syringe mounted on the pump in µL
            block: If True, function will block until the product is ready for a new command
        """
        if syringeVolume != self.syringeSize and syringeVolume is not None:
            self.syringeSize = syringeVolume
        if self.syringeSize == None: raise ValueError("Syringe volume must be specified")
        if self.microstepResolution == None: self.getMicrostepResolution()
        if self.microstepResolution == 0:
            to_dispense = int(volume * 3000 / self.syringeSize)
        else:
            to_dispense = int(volume * 24000 / self.syringeSize)
        
        self.pumpDispense(to_dispense, block = block)
    
    def powerOff(self) -> None:
        """
        Power off the pump (It cannot be powered on with a command)
        """
        if self.productFamily != "Pump":
            raise ValueError("Power off is only for SPM and LSPone")
        self.send(self.prepareCommand('powerOff'))
    
    
class util:    
    """ 
    Utilitary class used to detect AMF devices connected to the computer
    """

    def getProductList(connection_mode=None, port=None, address_list=None) -> list:
        """
        Detect connected AMF devices depending on connection type and OS.
    
        Parameters:
            connection_mode (str or None): "USB/RS232", "RS485", or None for auto-detection
            port (str or list or None): COM port for detection (None = scan all the ports)
            address_list (str iterable or None): Addresses to scan (only for RS485, as we browse every address possible)
        Returns:
            list: List of Device instances (populated with serial number, port, type, address)
        """        
        
        result = []
    
        if address_list is None:
            address_list  = ["1","2","3","4","5","6","7","8","9","A","B","C","D","E"]  
            
        if port is not None:
            if isinstance(port, str):
                port = [port]
            elif not isinstance(port, list):
                raise TypeError("port should be of type str, list or None")

        ports_to_scan = port if port else [p.device for p in serial.tools.list_ports.comports()] 

        # Auto mode if no connection_type is specified
        if connection_mode is None:
                        
            # Try USB/RS232 detection
            print("\nTrying USB/RS232 Connection...")
            usb_rs232_devices = util.getProductList(connection_mode="USB/RS232", port = ports_to_scan)
            if usb_rs232_devices:
               result.extend(usb_rs232_devices)
            else:
                print("No USB/RS232 device found")
                
            ports_found = [dev.comPort for dev in result]
            # We do not check ports already identified
            ports_to_scan = [p for p in ports_to_scan if p not in ports_found]
            
            # Try RS485 detection
            print("\nTrying RS485 Connection...")
            rs485_devices = util.getProductList(connection_mode = "RS485", port = ports_to_scan, address_list = address_list)                    
            if rs485_devices:
               result.extend(rs485_devices)
            else:
                print("No RS485 device found")
            
            return result        
    
        # ======================== USB/RS232 Mode ========================== #
        if "USB" in connection_mode.upper() or "RS232" in connection_mode.upper():                        
        # We check USB/RS232 together because the products will answer to broadcast address                 
            for p in ports_to_scan:
                try:
                    product = AMF(p, autoconnect = False)
                    product.responseTimeout = 0.1   # Use a short timeout as the product will answer quickly to the questions sent
                    product.connect(serialTimeout = 0.1)    # This function will fail if the address does not match the product's one
                    
                    dev = Device()
                    # If an RS232 adapter is used, it is the adapter S/N and not the AMF product S/N
                    dev.serialnumber = product.serialNumber
                    dev.comPort = p
                    dev.deviceType = product.typeProduct
                    dev.deviceFamily = product.productFamily
                    dev.connectionMode = product.connectionMode
                    dev.productAddress = product.getAddress()
                    product.disconnect()
                    result.append(dev)
                except:
                    try:
                        product.disconnect()
                    except:
                        pass
                  
        #======================== RS485 Mode =========================== #
        elif "RS485" in connection_mode.upper():
            
            # We test with no address so broadcast will be used, to check that the device is not in RS232 mode
            address_list = [None] + address_list
            for p in ports_to_scan:
                    for addr in address_list:
                        try:
                            product = AMF(p, autoconnect = False, productAddress=addr, connectionMode="RS485")
                            product.responseTimeout = 0.1   # Use a short timeout as the product will answer quickly to the questions sent
                            product.connect(serialTimeout = 0.1)   
                            
                            # If we are connected and broadcast address is used, we are not in RS485 mode so we skip this serial port
                            if addr == None:
                                #print("USB/RS232 device detected, skipping it")
                                break
                            dev = Device()
                            # If an RS485 adapter is used, it is the adapter S/N and not the AMF product S/N
                            dev.serialnumber = product.serialNumber  
                            dev.comPort = p                             
                            dev.deviceType = product.typeProduct
                            dev.deviceFamily = product.productFamily
                            dev.connectionMode = product.connectionMode
                            dev.productAddress = product.getAddress()                            
                            product.disconnect()
                            result.append(dev)
                            break
                        except:
                            try:
                                product.disconnect()
                            except:
                                pass
        return result 
    

if __name__ == "__main__":

    print("Scanning for connected AMF devices...")
    list_product = util.getProductList()    
    
    if not list_product:
        print("\nNo products found. Please check your connection and try again.")
    else:
        print(f"\nFound {len(list_product)} device(s):")
        for product in list_product:
            print(f"→ {product}")
        devices = []
        try:
            for idx, product in enumerate(list_product):
                amf = AMF(product)
                devices.append(amf)
                print(f"\n***************** Data from AMF product {idx+1} ******************")
                data = amf.getDeviceInformation(full=False)
                for key, value in data.items():
                    print(f"{key}: {value}")
                print("**************************************************************")
        except Exception as e:
            print(f"\n[ERROR] Failed while reading device info: {e}")
        finally:
            for dev in devices:
                try:
                    dev.disconnect()
                except Exception as e:
                    print(f"Warning: Could not disconnect device: {e}")


