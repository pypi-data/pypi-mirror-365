"""This module binds low-level API classes for all Mesoscope-VR components (cameras, microcontrollers, Zaber motors).
These bindings streamline the API used to interface with these components during experiment and training runtimes."""

from pathlib import Path

import numpy as np
from ataraxis_time import PrecisionTimer
from sl_shared_assets import ZaberPositions
from ataraxis_video_system import (
    VideoCodecs,
    VideoSystem,
    VideoFormats,
    CameraBackends,
    GPUEncoderPresets,
    InputPixelFormats,
    OutputPixelFormats,
)
from ataraxis_base_utilities import LogLevel, console
from ataraxis_data_structures import DataLogger
from ataraxis_time.time_helpers import convert_time
from ataraxis_communication_interface import MicroControllerInterface

from .tools import get_system_configuration
from .zaber_bindings import ZaberAxis, ZaberConnection
from ..shared_components import (
    TTLInterface,
    LickInterface,
    BreakInterface,
    ValveInterface,
    ScreenInterface,
    TorqueInterface,
    EncoderInterface,
)


class ZaberMotors:
    """Interfaces with Zaber motors that control the position of the HeadBar, LickPort, and the running Wheel inside the
    mesoscope cage.

    This class abstracts working with Zaber motors that move the HeadBar in Z, Pitch, and Roll axes, the LickPort in
    X, Y, and Z axes, and the Wheel in X axis. It is used by the major runtime classes, such as _MesoscopeExperiment,
    to position various Mesoscope-VR components and the mouse in a way that promotes data acquisition and task
    performance.

    Notes:
        The class is designed to transition the motors between a set of predefined states and should not be used
        directly by the user. It does not contain the guards that notify users about risks associated with moving the
        motors. Do not use any methods from this class unless you know what you are doing. It is possible to damage
        the motors, the mesoscope, or harm the animal.

        To fine-tune the position of any Zaber motors in real time, use the main Zaber Launcher interface
        (https://software.zaber.com/zaber-launcher/download) installed on the VRPC.

        Unless you know that the motors are homed and not parked, always call the prepare_motors() method before
        calling any other methods. Otherwise, Zaber controllers will likely ignore the issued commands.

    Args:
        zaber_positions_path: The path to the zaber_positions.yaml file that stores the motor positions saved during the
            previous runtime.

    Attributes:
        _headbar: Stores the Connection class instance that manages the USB connection to a daisy-chain of Zaber
            devices (controllers) that allow repositioning the headbar holder.
        _headbar_z: The ZaberAxis class instance for the headbar z-axis motor.
        _headbar_pitch: The ZaberAxis class instance for the headbar pitch-axis motor.
        _headbar_roll: The ZaberAxis class instance for the headbar roll-axis motor.
        _wheel: Stores the Connection class instance that manages the USB connection to a daisy-chain of Zaber
            devices (controllers) that allow repositioning the running wheel.
        _wheel_x: The ZaberAxis class instance for the running-wheel X-axis motor.
        _lickport: Stores the Connection class instance that manages the USB connection to a daisy-chain of Zaber
            devices (controllers) that allow repositioning the lickport.
        _lickport_z: Stores the Axis (motor) class that controls the position of the lickport along the Z axis.
        _lickport_x: Stores the Axis (motor) class that controls the position of the lickport along the X axis.
        _lickport_y: Stores the Axis (motor) class that controls the position of the lickport along the Y axis.
        _previous_positions: An instance of _ZaberPositions class that stores the positions of Zaber motors during a
           previous runtime. If this data is not available, this attribute is set to None to indicate there are no
           previous positions to use.
    """

    def __init__(self, zaber_positions_path: Path) -> None:
        # Retrieves the Mesoscope-VR system configuration parameters.
        system_configuration = get_system_configuration()

        # Initializes the connection classes first to ensure all classes exist in case the runtime encounters
        # an error during connection.
        self._headbar: ZaberConnection = ZaberConnection(port=system_configuration.additional_firmware.headbar_port)
        self._wheel: ZaberConnection = ZaberConnection(port=system_configuration.additional_firmware.wheel_port)
        self._lickport: ZaberConnection = ZaberConnection(port=system_configuration.additional_firmware.lickport_port)

        # HeadBar controller (zaber). This is an assembly of 3 zaber controllers (devices) that allow moving the
        # headbar attached to the mouse's head in Z, Roll, and Pitch axes. Note, this assumes that the chaining
        # order of individual zaber devices is fixed and is always Z-Pitch-Roll.
        self._headbar.connect()
        self._headbar_z: ZaberAxis = self._headbar.get_device(0).axis
        self._headbar_pitch: ZaberAxis = self._headbar.get_device(1).axis
        self._headbar_roll: ZaberAxis = self._headbar.get_device(2).axis

        # Lickport controller (zaber). This is an assembly of 3 zaber controllers (devices) that allow moving the
        # lick tube in Z, X, and Y axes. Note, this assumes that the chaining order of individual zaber devices is
        # fixed and is always Z-X-Y.
        self._lickport.connect()
        self._lickport_z: ZaberAxis = self._lickport.get_device(0).axis
        self._lickport_y: ZaberAxis = self._lickport.get_device(1).axis
        self._lickport_x: ZaberAxis = self._lickport.get_device(2).axis

        # Wheel controller (zaber). Currently, this assembly includes a single controller (device) that allows moving
        # the running wheel in the X axis.
        self._wheel.connect()
        self._wheel_x: ZaberAxis = self._wheel.get_device(0).axis

        # If the previous positions path points to an existing .yaml file, loads the data from the file into
        # _ZaberPositions instance. Otherwise, sets the previous_positions attribute to None to indicate there are no
        # previous positions.
        self._previous_positions: None | ZaberPositions = None
        if zaber_positions_path.exists():
            self._previous_positions = ZaberPositions.from_yaml(zaber_positions_path)  # type: ignore
        else:
            message = (
                "No previous position data found when attempting to load Zaber motor positions used during a previous "
                "runtime. Setting all Zaber motors to use the default positions cached in non-volatile memory of each "
                "motor controller."
            )
            console.echo(message=message, level=LogLevel.ERROR)

    def restore_position(self) -> None:
        """Restores the Zaber motor positions to the states recorded at the end of the previous runtime.

        For most runtimes, this method is used to restore the motors to the state used during a previous experiment or
        training session for each animal. Since all animals are slightly different, the optimal Zaber motor positions
        will vary slightly for each animal.

        Notes:
            If previous positions are not available, the method falls back to moving the motors to the general
            'mounting' positions saved in the non-volatile memory of each motor controller. These positions are designed
            to work for most animals and provide an initial position for the animal to be mounted into the VR rig.

            This method moves all Zaber axes in parallel to optimize runtime speed. This relies on the Mesoscope-VR
            system to be assembled in a way where it is safe to move all motors at the same time.
        """

        # Disables the safety motor lock before moving the motors.
        self.unpark_motors()

        # If previous position data is available, restores all motors to the positions used during previous sessions.
        # Otherwise, sets HeadBar and Wheel to mounting position and the LickPort to parking position. For LickPort,
        # the only difference between parking and mounting positions is that the mounting position is retracted further
        # away from the animal than the parking position.
        self._headbar_z.move(
            amount=self._headbar_z.mount_position
            if self._previous_positions is None
            else self._previous_positions.headbar_z,
            absolute=True,
            native=True,
        )
        self._headbar_pitch.move(
            amount=self._headbar_pitch.mount_position
            if self._previous_positions is None
            else self._previous_positions.headbar_pitch,
            absolute=True,
            native=True,
        )
        self._headbar_roll.move(
            amount=self._headbar_roll.mount_position
            if self._previous_positions is None
            else self._previous_positions.headbar_roll,
            absolute=True,
            native=True,
        )
        self._wheel_x.move(
            amount=self._wheel_x.mount_position
            if self._previous_positions is None
            else self._previous_positions.wheel_x,
            absolute=True,
            native=True,
        )
        self._lickport_z.move(
            amount=self._lickport_z.park_position
            if self._previous_positions is None
            else self._previous_positions.lickport_z,
            absolute=True,
            native=True,
        )
        self._lickport_x.move(
            amount=self._lickport_x.park_position
            if self._previous_positions is None
            else self._previous_positions.lickport_x,
            absolute=True,
            native=True,
        )
        self._lickport_y.move(
            amount=self._lickport_y.park_position
            if self._previous_positions is None
            else self._previous_positions.lickport_y,
            absolute=True,
            native=True,
        )

        # Waits for all motors to finish moving before returning to caller.
        self.wait_until_idle()

        # Prevents further interaction with the motors without manually disabling the parking lock.
        self.park_motors()

    def prepare_motors(self) -> None:
        """Unparks and homes all motors.

        This method should be used at the beginning of each runtime (experiment, training, etc.) to ensure all Zaber
        motors can be moved (are not parked) and have a stable point of reference. The motors are left at their
        respective homing positions at the end of this method's runtime, and it is assumed that a different class
        method is called after this method to set the motors into the desired position.

        Notes:
            This method moves all motor axes in parallel to optimize runtime speed.
        """

        # Disables the safety motor lock before moving the motors.
        self.unpark_motors()

        # Homes all motors in-parallel.
        self._headbar_z.home()
        self._headbar_pitch.home()
        self._headbar_roll.home()
        self._wheel_x.home()
        self._lickport_z.home()
        self._lickport_x.home()
        self._lickport_y.home()

        # Waits for all motors to finish moving before returning to caller.
        self.wait_until_idle()

        # Prevents further interaction with the motors without manually disabling the parking lock.
        self.park_motors()

    def park_position(self) -> None:
        """Moves all motors to their parking positions and parks (locks) them preventing future movements.

        This method should be used at the end of each runtime (experiment, training, etc.) to ensure all Zaber motors
        are positioned in a way that guarantees that they can be homed during the next runtime.

        Notes:
            The motors are moved to the parking positions stored in the non-volatile memory of each motor controller.
            This method moves all motor axes in parallel to optimize runtime speed.
        """

        # Disables the safety motor lock before moving the motors.
        self.unpark_motors()

        # Moves all Zaber motors to their parking positions
        self._headbar_z.move(amount=self._headbar_z.park_position, absolute=True, native=True)
        self._headbar_pitch.move(amount=self._headbar_pitch.park_position, absolute=True, native=True)
        self._headbar_roll.move(amount=self._headbar_roll.park_position, absolute=True, native=True)
        self._wheel_x.move(amount=self._wheel_x.park_position, absolute=True, native=True)
        self._lickport_z.move(amount=self._lickport_z.park_position, absolute=True, native=True)
        self._lickport_x.move(amount=self._lickport_x.park_position, absolute=True, native=True)
        self._lickport_y.move(amount=self._lickport_y.park_position, absolute=True, native=True)

        # Waits for all motors to finish moving before returning to caller.
        self.wait_until_idle()

        # Prevents further interaction with the motors without manually disabling the parking lock.
        self.park_motors()

    def maintenance_position(self) -> None:
        """Moves all motors to the Mesoscope-VR system maintenance position.

        This position is stored in the non-volatile memory of each motor controller. Primarily, this position is used
        during the water valve calibration and during running-wheel maintenance (cleaning, replacing surface material,
        etc.).

        Notes:
            This method moves all motor axes in parallel to optimize runtime speed.

            Formerly, the only maintenance step was the calibration of the water-valve, so some low-level functions
            still reference it as 'valve-position' and 'calibrate-position'.
        """

        # Disables the safety motor lock before moving the motors.
        self.unpark_motors()

        # Moves all motors to their maintenance positions
        self._headbar_z.move(amount=self._headbar_z.valve_position, absolute=True, native=True)
        self._headbar_pitch.move(amount=self._headbar_pitch.valve_position, absolute=True, native=True)
        self._headbar_roll.move(amount=self._headbar_roll.valve_position, absolute=True, native=True)
        self._wheel_x.move(amount=self._wheel_x.valve_position, absolute=True, native=True)
        self._lickport_z.move(amount=self._lickport_z.valve_position, absolute=True, native=True)
        self._lickport_x.move(amount=self._lickport_x.valve_position, absolute=True, native=True)
        self._lickport_y.move(amount=self._lickport_y.valve_position, absolute=True, native=True)

        # Waits for all motors to finish moving before returning to caller.
        self.wait_until_idle()

        # Prevents further interaction with the motors without manually disabling the parking lock.
        self.park_motors()

    def mount_position(self) -> None:
        """Moves all motors to the animal mounting position.

        This position is stored in the non-volatile memory of each motor controller. This position is used when the
        animal is mounted into the VR rig to provide the experimenter with easy access to the head bar holder.

        Notes:
            This method moves all MOTOR axes in parallel to optimize runtime speed.
        """

        # Disables the safety motor lock before moving the motors.
        self.unpark_motors()

        # Moves all lickport motors to the mount position
        self._lickport_z.move(amount=self._lickport_z.mount_position, absolute=True, native=True)
        self._lickport_x.move(amount=self._lickport_x.mount_position, absolute=True, native=True)
        self._lickport_y.move(amount=self._lickport_y.mount_position, absolute=True, native=True)

        # If previous positions are not available, moves the rest of the motors to the default mounting positions
        if self._previous_positions is None:
            self._headbar_z.move(amount=self._headbar_z.mount_position, absolute=True, native=True)
            self._headbar_pitch.move(amount=self._headbar_pitch.mount_position, absolute=True, native=True)
            self._headbar_roll.move(amount=self._headbar_roll.mount_position, absolute=True, native=True)
            self._wheel_x.move(amount=self._wheel_x.mount_position, absolute=True, native=True)

        # If previous positions are available, restores other motors to the position used during the previous runtime.
        # This relies on the idea that mounting is primarily facilitated by moving the lickport away, while all mouse
        # positioning motors can be set to the parameters optimal for the mouse being mounted.
        else:
            self._headbar_z.move(amount=self._previous_positions.headbar_z, absolute=True, native=True)
            self._headbar_pitch.move(amount=self._previous_positions.headbar_pitch, absolute=True, native=True)
            self._headbar_roll.move(amount=self._previous_positions.headbar_roll, absolute=True, native=True)
            self._wheel_x.move(amount=self._previous_positions.wheel_x, absolute=True, native=True)

        # Waits for all motors to finish moving before returning to caller.
        self.wait_until_idle()

        # Prevents further interaction with the motors without manually disabling the parking lock.
        self.park_motors()

    def unmount_position(self) -> None:
        """Moves the lick-port back to the mount position in all axes while keeping all other motors in their current
        positions.

        This command facilitates removing (unmounting) the animal from the VR rig while being safe to execute when the
        mesoscope objective and other mesoscope-VR elements are positioned for imaging.

        Notes:
            Technically, calling the mount_position() method after generating a new ZaberMotors snapshot will behave
            identically to this command. However, to improve runtime safety and the clarity of the class API, it is
            highly encouraged to use this method to unmount the animal.
        """

        # Disables the safety motor lock before moving the motors.
        self.unpark_motors()

        # Moves the lick-port back to the mount position, while keeping all other motors in their current positions.
        self._lickport_y.move(amount=self._lickport_y.mount_position, absolute=True, native=True)
        self._lickport_z.move(amount=self._lickport_z.mount_position, absolute=True, native=True)
        self._lickport_x.move(amount=self._lickport_x.mount_position, absolute=True, native=True)

        # Waits for all motors to finish moving before returning to caller.
        self.wait_until_idle()

        # Prevents further interaction with the motors without manually disabling the parking lock.
        self.park_motors()

    def generate_position_snapshot(self) -> ZaberPositions:
        """Queries the current positions of all managed Zaber motors, packages the position data into a ZaberPositions
        instance, and returns it to the caller.

        This method is used by runtime classes to update the ZaberPositions instance cached on disk for each animal.
        The method also updates the local ZaberPositions copy stored inside the class instance with the data from the
        generated snapshot. Primarily, this has to be done to support the Zaber motor shutdown sequence.
        """
        self._previous_positions = ZaberPositions(
            headbar_z=int(self._headbar_z.get_position(native=True)),
            headbar_pitch=int(self._headbar_pitch.get_position(native=True)),
            headbar_roll=int(self._headbar_roll.get_position(native=True)),
            wheel_x=int(self._wheel_x.get_position(native=True)),
            lickport_z=int(self._lickport_z.get_position(native=True)),
            lickport_x=int(self._lickport_x.get_position(native=True)),
            lickport_y=int(self._lickport_y.get_position(native=True)),
        )
        return self._previous_positions

    def wait_until_idle(self) -> None:
        """Blocks in-place while at least one motor in the managed motor group(s) is moving.

        Primarily, this method is used to issue commands to multiple motor groups and then block until all motors in
        all groups finish moving. This optimizes the overall time taken to move the motors.
        """

        # Waits for the motors to finish moving. Note, motor state polling includes the built-in delay mechanism to
        # prevent overwhelming the communication interface.
        while (
            self._headbar_z.is_busy
            or self._headbar_pitch.is_busy
            or self._headbar_roll.is_busy
            or self._wheel_x.is_busy
            or self._lickport_z.is_busy
            or self._lickport_x.is_busy
            or self._lickport_y.is_busy
        ):
            pass

    def disconnect(self) -> None:
        """Disconnects from the communication port(s) of the managed motor groups.

        This method should be called after the motors are parked (moved to their final parking position) to release
        the connection resources. If this method is not called, the runtime will NOT be able to terminate.
        """
        self._headbar.disconnect()
        self._wheel.disconnect()
        self._lickport.disconnect()

    def park_motors(self) -> None:
        """Parks all managed motor groups, preventing them from being moved via this library or Zaber GUI until
        they are unparked via the unpark_motors() command."""
        self._headbar_pitch.park()
        self._headbar_roll.park()
        self._headbar_z.park()
        self._wheel_x.park()
        self._lickport_x.park()
        self._lickport_y.park()
        self._lickport_z.park()

    def unpark_motors(self) -> None:
        """Unparks all managed motor groups, allowing them to be moved via this library or the Zaber GUI."""
        self._headbar_pitch.unpark()
        self._headbar_roll.unpark()
        self._headbar_z.unpark()
        self._wheel_x.unpark()
        self._lickport_x.unpark()
        self._lickport_y.unpark()
        self._lickport_z.unpark()

    @property
    def is_connected(self) -> bool:
        """Returns True if all managed motor connections are active and False if at least one connection is inactive."""
        connections = [
            self._headbar.is_connected,
            self._lickport.is_connected,
            self._wheel.is_connected,
        ]
        return all(connections)


class MicroControllerInterfaces:
    """Interfaces with all Ataraxis Micro Controller (AMC) devices that control Mesoscope-VR system hardware and acquire
    non-video behavior data.

    This class interfaces with the three AMC controllers used during various runtimes: Actor, Sensor, and Encoder. The
    class exposes methods to send commands to the hardware modules managed by these microcontrollers. In turn, these
    modules control specific components of the Mesoscope-Vr system, such as rotary encoders, solenoid valves, and
    conductive lick sensors.

    Notes:
        This class is primarily intended to be used internally by the _MesoscopeExperiment and _BehaviorTraining
        classes. Our maintenance CLI (sl-maintain) is the only exception to this rule, as it directly uses this class to
        facilitate Mesoscope-VR maintenance tasks.

        Calling the initializer does not start the underlying processes. Use the start() method before issuing other
        commands to properly initialize all remote processes. This design is intentional and is used during experiment
        and training runtimes to parallelize data preprocessing for the previous session and runtime preparation for the
        following session.

    Args:
        data_logger: The initialized DataLogger instance used to log the data generated by the managed microcontrollers.
            For most runtimes, this argument is resolved by the _MesoscopeExperiment or _BehaviorTraining classes that
            initialize this class.

    Attributes:
        _started: Tracks whether the VR system and experiment runtime are currently running.
        _system_configuration: Stores the configuration parameters used by the Mesoscope-VR system.
        _sensor_polling_delay: Stores the delay, in microseconds, between any two consecutive sensor readout polls. This
            delay is the same for most sensor modules.
        _previous_volume: Tracks the volume of water dispensed during previous deliver_reward() calls.
        _previous_tone_duration: Tracks the auditory tone duration during previous deliver_reward() or simulate_reward()
            calls.
        _screen_state: Tracks the current VR screen state.
        _frame_monitoring: Tracks the current mesoscope frame monitoring state.
        _torque_monitoring: Tracks the current torque monitoring state.
        _lick_monitoring: Tracks the current lick monitoring state.
        _encoder_monitoring: Tracks the current encoder monitoring state.
        _break_state: Tracks the current break state.
        _delay_timer: Stores a millisecond-precise timer used by certain sequential command methods.
        wheel_break: The interface that controls the electromagnetic break attached to the running wheel.
        valve: The interface that controls the solenoid water valve that delivers water to the animal.
        screens: The interface that controls the power state of the VR display screens.
        _actor: The main interface for the 'Actor' Ataraxis Micro Controller (AMC) device.
        mesoscope_frame: The interface that monitors frame acquisition timestamp signals sent by the mesoscope.
        lick: The interface that monitors animal's interactions with the lick sensor (detects licks).
        torque: The interface that monitors the torque applied by the animal to the running wheel.
        _sensor: The main interface for the 'Sensor' Ataraxis Micro Controller (AMC) device.
        wheel_encoder: The interface that monitors the rotation of the running wheel and converts it into the distance
            traveled by the animal.
        _encoder: The main interface for the 'Encoder' Ataraxis Micro Controller (AMC) device.
    """

    def __init__(self, data_logger: DataLogger) -> None:
        # Initializes the start state tracker first
        self._started: bool = False

        # Retrieves the Mesoscope-VR system configuration parameters and saves them to class attribute to use them from
        # class methods.
        self._system_configuration = get_system_configuration()

        # Converts the general sensor polling delay and stores it in class attribute. Unless other duration / delay
        # parameters, this one is frequently queried by class methods, so it is beneficial to statically compute
        # it once.
        self._sensor_polling_delay: float = convert_time(  # type: ignore
            time=self._system_configuration.microcontrollers.sensor_polling_delay_ms, from_units="ms", to_units="us"
        )

        # Initializes internal tracker variables
        self._previous_volume: float = 0.0
        self._previous_tone_duration: int = 0
        self._screen_state: bool = False
        self._frame_monitoring: bool = False
        self._torque_monitoring: bool = False
        self._lick_monitoring: bool = False
        self._encoder_monitoring: bool = False
        self._break_state: bool = True  # The break is normally engaged, so it starts engaged by default

        self._delay_timer = PrecisionTimer("ms")

        # ACTOR. Actor AMC controls the hardware that needs to be triggered by PC at irregular intervals. Most of such
        # hardware is designed to produce some form of an output: deliver water reward, engage wheel breaks, issue a
        # TTL trigger, etc.

        # Module interfaces:
        self.wheel_break = BreakInterface(
            minimum_break_strength=self._system_configuration.microcontrollers.minimum_break_strength_g_cm,
            maximum_break_strength=self._system_configuration.microcontrollers.maximum_break_strength_g_cm,
            object_diameter=self._system_configuration.microcontrollers.wheel_diameter_cm,
            debug=self._system_configuration.microcontrollers.debug,
        )
        self.valve = ValveInterface(
            valve_calibration_data=self._system_configuration.microcontrollers.valve_calibration_data,  # type: ignore
            debug=self._system_configuration.microcontrollers.debug,
        )
        self.screens = ScreenInterface(
            initially_on=False,  # Initial Screen State is hardcoded
            debug=self._system_configuration.microcontrollers.debug,
        )

        # Main interface:
        self._actor: MicroControllerInterface = MicroControllerInterface(
            controller_id=np.uint8(101),  # Hardcoded
            microcontroller_serial_buffer_size=8192,  # Hardcoded
            microcontroller_usb_port=self._system_configuration.microcontrollers.actor_port,
            data_logger=data_logger,
            module_interfaces=(self.wheel_break, self.valve, self.screens),
        )

        # SENSOR. Sensor AMC controls the hardware that collects data at regular intervals. This includes lick sensors,
        # torque sensors, and input TTL recorders. Critically, all managed hardware does not rely on hardware interrupt
        # logic to maintain the necessary precision.

        # Module interfaces:
        self.mesoscope_frame: TTLInterface = TTLInterface(
            module_id=np.uint8(1),  # Hardcoded
            report_pulses=True,  # Hardcoded
            debug=self._system_configuration.microcontrollers.debug,
        )
        self.lick: LickInterface = LickInterface(
            lick_threshold=self._system_configuration.microcontrollers.lick_threshold_adc,
            debug=self._system_configuration.microcontrollers.debug,
        )
        self.torque: TorqueInterface = TorqueInterface(
            baseline_voltage=self._system_configuration.microcontrollers.torque_baseline_voltage_adc,
            maximum_voltage=self._system_configuration.microcontrollers.torque_maximum_voltage_adc,
            sensor_capacity=self._system_configuration.microcontrollers.torque_sensor_capacity_g_cm,
            object_diameter=self._system_configuration.microcontrollers.wheel_diameter_cm,
            debug=self._system_configuration.microcontrollers.debug,
        )

        # Main interface:
        self._sensor: MicroControllerInterface = MicroControllerInterface(
            controller_id=np.uint8(152),  # Hardcoded
            microcontroller_serial_buffer_size=8192,  # Hardcoded
            microcontroller_usb_port=self._system_configuration.microcontrollers.sensor_port,
            data_logger=data_logger,
            module_interfaces=(self.mesoscope_frame, self.lick, self.torque),
        )

        # ENCODER. Encoder AMC is specifically designed to interface with a rotary encoder connected to the running
        # wheel. The encoder uses hardware interrupt logic to maintain high precision and, therefore, it is isolated
        # to a separate microcontroller to ensure adequate throughput.

        # Module interfaces:
        self.wheel_encoder: EncoderInterface = EncoderInterface(
            encoder_ppr=self._system_configuration.microcontrollers.wheel_encoder_ppr,
            object_diameter=self._system_configuration.microcontrollers.wheel_diameter_cm,
            cm_per_unity_unit=self._system_configuration.microcontrollers.cm_per_unity_unit,
            debug=self._system_configuration.microcontrollers.debug,
        )

        # Main interface:
        self._encoder: MicroControllerInterface = MicroControllerInterface(
            controller_id=np.uint8(203),  # Hardcoded
            microcontroller_serial_buffer_size=8192,  # Hardcoded
            microcontroller_usb_port=self._system_configuration.microcontrollers.encoder_port,
            data_logger=data_logger,
            module_interfaces=(self.wheel_encoder,),
        )

    def __del__(self) -> None:
        """Ensures that all hardware resources are released when the object is garbage-collected."""
        self.stop()

    def start(self) -> None:
        """Starts MicroController communication processes and configures all hardware modules to use the runtime
        parameters loaded from the acquisition system configuration file.

        This method sets up the necessary assets that enable MicroController-PC communication. Until this method is
        called, all other class methods will not function correctly.

        Notes:
            After calling this method, most hardware modules will be initialized to an idle state. The only exception to
            this rule is the wheel break, which initializes to the 'engaged' state. Use other class methods to
            switch individual hardware modules into the desired state.

            Since most modules initialize to an idle state, they will not be generating data. Therefore, it is safe
            to call this method before enabling the DataLogger class. However, it is strongly advised to enable the
            DataLogger as soon as possible to avoid data piling up in the buffer.
        """

        # Prevents executing this method if the MicroControllers are already running.
        if self._started:
            return

        message = "Initializing Ataraxis Micro Controller (AMC) Interfaces..."
        console.echo(message=message, level=LogLevel.INFO)

        # Starts all microcontroller interfaces
        self._actor.start()
        self._actor.unlock_controller()  # Only Actor outputs data, so no need to unlock other controllers.
        self._sensor.start()
        self._encoder.start()

        # Configures the encoder to only report forward motion (CW) if the motion exceeds ~ 1 mm of distance.
        self.wheel_encoder.set_parameters(
            report_cw=self._system_configuration.microcontrollers.wheel_encoder_report_cw,
            report_ccw=self._system_configuration.microcontrollers.wheel_encoder_report_ccw,
            delta_threshold=self._system_configuration.microcontrollers.wheel_encoder_delta_threshold_pulse,
        )

        # Configures screen trigger pulse duration
        screen_pulse_duration: float = convert_time(  # type: ignore
            time=self._system_configuration.microcontrollers.screen_trigger_pulse_duration_ms,
            from_units="ms",
            to_units="us",
        )
        self.screens.set_parameters(pulse_duration=np.uint32(screen_pulse_duration))

        # Configures the water valve to deliver ~ 5 uL of water by default.
        tone_duration: float = convert_time(  # type: ignore
            time=self._system_configuration.microcontrollers.auditory_tone_duration_ms, from_units="ms", to_units="us"
        )
        self.valve.set_parameters(
            pulse_duration=np.uint32(self.valve.get_duration_from_volume(5.0)),  # Hardcoded for calibration purposes
            calibration_delay=np.uint32(300000),  # Hardcoded! Do not decrease unless you know what you are doing!
            calibration_count=np.uint16(self._system_configuration.microcontrollers.valve_calibration_pulse_count),
            tone_duration=np.uint32(tone_duration),
        )

        # Configures the lick sensor to filter out dry touches and only report significant changes in detected voltage
        # (used as a proxy for detecting licks).
        self.lick.set_parameters(
            signal_threshold=np.uint16(self._system_configuration.microcontrollers.lick_signal_threshold_adc),
            delta_threshold=np.uint16(self._system_configuration.microcontrollers.lick_delta_threshold_adc),
            averaging_pool_size=np.uint8(self._system_configuration.microcontrollers.lick_averaging_pool_size),
        )

        # Configures the torque sensor to filter out noise and sub-threshold 'slack' torque signals.
        self.torque.set_parameters(
            report_ccw=np.bool(self._system_configuration.microcontrollers.torque_report_ccw),
            report_cw=np.bool(self._system_configuration.microcontrollers.torque_report_cw),
            signal_threshold=np.uint16(self._system_configuration.microcontrollers.torque_signal_threshold_adc),
            delta_threshold=np.uint16(self._system_configuration.microcontrollers.torque_delta_threshold_adc),
            averaging_pool_size=np.uint8(self._system_configuration.microcontrollers.torque_averaging_pool_size),
        )

        # The setup procedure is complete.
        self._started = True

        message = "Ataraxis Micro Controller (AMC) Interfaces: Initialized."
        console.echo(message=message, level=LogLevel.SUCCESS)

    def stop(self) -> None:
        """Stops all MicroController communication processes and releases all resources.

        This method needs to be called at the end of each runtime to release the resources reserved by the start()
        method. Until the stop() method is called, the DataLogger instance may receive data from running
        MicroControllers, so calling this method also guarantees no MicroController data will be lost if the DataLogger
        process is terminated.
        """

        # Prevents stopping an already stopped VR process.
        if not self._started:
            return

        message = "Terminating Ataraxis Micro Controller (AMC) Interfaces..."
        console.echo(message=message, level=LogLevel.INFO)

        # Resets the _started tracker
        self._started = False

        # Stops all microcontroller interfaces. This directly shuts down and resets all managed hardware modules.
        self._actor.stop()
        self._sensor.stop()
        self._encoder.stop()

        message = "Ataraxis Micro Controller (AMC) Interfaces: Terminated."
        console.echo(message=message, level=LogLevel.SUCCESS)

    def enable_encoder_monitoring(self) -> None:
        """Enables wheel encoder monitoring at a 2 kHz rate.

        This means that, at most, the Encoder will send the data to the PC at the 2 kHz rate. The Encoder collects data
        at the native rate supported by the microcontroller hardware, which likely exceeds the reporting rate.
        """
        if not self._encoder_monitoring:
            self.wheel_encoder.reset_pulse_count()
            self.wheel_encoder.check_state(
                repetition_delay=np.uint32(self._system_configuration.microcontrollers.wheel_encoder_polling_delay_us)
            )
            self._encoder_monitoring = True

    def disable_encoder_monitoring(self) -> None:
        """Stops monitoring the wheel encoder."""
        if self._encoder_monitoring:
            self.wheel_encoder.reset_command_queue()
            self._encoder_monitoring = False

    def enable_break(self) -> None:
        """Engages the wheel break at maximum strength, preventing the animal from running on the wheel."""
        if not self._break_state:
            self.wheel_break.toggle(state=True)
            self._break_state = True

    def disable_break(self) -> None:
        """Disengages the wheel break, enabling the animal to run on the wheel."""
        if self._break_state:
            self.wheel_break.toggle(state=False)
            self._break_state = False

    def enable_vr_screens(self) -> None:
        """Sets the VR screens to be ON."""
        if not self._screen_state:  # If screens are OFF
            self.screens.toggle()  # Sets them ON
            self._screen_state = True

    def disable_vr_screens(self) -> None:
        """Sets the VR screens to be OFF."""
        if self._screen_state:  # If screens are ON
            self.screens.toggle()  # Sets them OFF
            self._screen_state = False

    def enable_mesoscope_frame_monitoring(self) -> None:
        """Enables monitoring the TTL pulses sent by the mesoscope to communicate when it is scanning a frame at
        ~ 1 kHZ rate.

        The mesoscope sends the HIGH phase of the TTL pulse while it is scanning the frame, which produces a pulse of
        ~100ms. This is followed by ~5ms LOW phase during which the Galvos are executing the flyback procedure. This
        command checks the state of the TTL pin at the 1 kHZ rate, which is enough to accurately report both phases.
        """
        if not self._frame_monitoring:
            self.mesoscope_frame.check_state(repetition_delay=np.uint32(self._sensor_polling_delay))
            self._frame_monitoring = True

    def disable_mesoscope_frame_monitoring(self) -> None:
        """Stops monitoring the TTL pulses sent by the mesoscope to communicate when it is scanning a frame."""
        if self._frame_monitoring:
            self.mesoscope_frame.reset_command_queue()
            self._frame_monitoring = False

    def enable_lick_monitoring(self) -> None:
        """Enables monitoring the state of the conductive lick sensor at ~ 1 kHZ rate.

        The lick sensor measures the voltage across the lick sensor and reports surges in voltage to the PC as a
        reliable proxy for tongue-to-sensor contact. Most lick events span at least 100 ms of time and, therefore, the
        rate of 1 kHZ is adequate for resolving all expected single-lick events.
        """
        if not self._lick_monitoring:
            self.lick.check_state(repetition_delay=np.uint32(self._sensor_polling_delay))
            self._lick_monitoring = True

    def disable_lick_monitoring(self) -> None:
        """Stops monitoring the conductive lick sensor."""
        if self._lick_monitoring:
            self.lick.reset_command_queue()
            self._lick_monitoring = False

    def enable_torque_monitoring(self) -> None:
        """Enables monitoring the torque sensor at ~ 1 kHZ rate.

        The torque sensor detects CW and CCW torques applied by the animal to the wheel. Currently, we do not have a
        way of reliably calibrating the sensor, so detected torque magnitudes are only approximate. However, the sensor
        reliably distinguishes large torques from small torques and accurately tracks animal motion activity when the
        wheel break is engaged.
        """
        if not self._torque_monitoring:
            self.torque.check_state(repetition_delay=np.uint32(self._sensor_polling_delay))
            self._torque_monitoring = True

    def disable_torque_monitoring(self) -> None:
        """Stops monitoring the torque sensor."""
        if self._torque_monitoring:
            self.torque.reset_command_queue()
            self._torque_monitoring = False

    def open_valve(self) -> None:
        """Opens the water reward solenoid valve.

        This method is primarily used to prime the water line with water before the first experiment or training session
        of the day.
        """
        self.valve.toggle(state=True)

    def close_valve(self) -> None:
        """Closes the water reward solenoid valve."""
        self.valve.toggle(state=False)

    def deliver_reward(self, volume: float = 5.0, tone_duration: int = 300, ignore_parameters: bool = False) -> None:
        """Pulses the water reward solenoid valve for the duration of time necessary to deliver the provided volume of
        water.

        This method assumes that the valve has been calibrated before calling this method. It uses the calibration data
        provided at class instantiation to determine the period of time the valve should be kept open to deliver the
        requested volume of water.

        Args:
            volume: The volume of water to deliver, in microliters.
            tone_duration: The duration of the auditory tone, in milliseconds, to emit while delivering the water
                reward.
            ignore_parameters: Determines whether to ignore the volume and tone_duration arguments. Calling the method
                with this argument ensures that the delivered reward always uses the same volume and tone_duration as
                the previous reward command. Primarily, this argument is used when receiving reward commands from Unity.
        """

        # This ensures that the valve settings are only updated if volume, tone_duration, or both changed compared to
        # the previous command runtime. This ensures that the valve settings are only updated when this is necessary,
        # reducing communication overhead.
        if not ignore_parameters and (volume != self._previous_volume or tone_duration != self._previous_tone_duration):
            # Parameters are cached here to use the tone_duration before it is converted to microseconds.
            self._previous_volume = volume
            self._previous_tone_duration = tone_duration

            # Note, calibration parameters are not used by the command below, but we explicitly set them here for
            # consistency
            tone_duration: float = convert_time(time=tone_duration, from_units="ms", to_units="us")  # type: ignore
            self.valve.set_parameters(
                pulse_duration=self.valve.get_duration_from_volume(volume),
                calibration_delay=np.uint32(300000),  # Hardcoded for safety reasons!
                calibration_count=np.uint16(self._system_configuration.microcontrollers.valve_calibration_pulse_count),
                tone_duration=np.uint32(tone_duration),
            )

        self.valve.send_pulse(noblock=False)

    def simulate_reward(self, tone_duration: int = 300) -> None:
        """Simulates delivering water reward by emitting an audible 'reward' tone without triggering the valve.

        This method is used during training when the animal refuses to consume water rewards. In this case, the water
        rewards are not delivered, but the tones are still played to notify the animal it is performing the task as
        required.

        Args:
            tone_duration: The duration of the auditory tone, in milliseconds, to emit while simulating the water
                reward delivery.
        """

        # This ensures that the valve settings are only updated if tone_duration changed compared to the previous
        # command runtime. This ensures that the valve settings are only updated when this is necessary, reducing
        # communication overhead.
        if tone_duration != self._previous_tone_duration:
            # Parameters are cached here to use the tone_duration before it is converted to microseconds.
            self._previous_tone_duration = tone_duration

            # Note, calibration parameters are not used by the command below, but we explicitly set them here for
            # consistency
            tone_duration: float = convert_time(time=tone_duration, from_units="ms", to_units="us")  # type: ignore
            self.valve.set_parameters(
                pulse_duration=self.valve.get_duration_from_volume(self._previous_volume),
                calibration_delay=np.uint32(300000),  # Hardcoded for safety reasons!
                calibration_count=np.uint16(self._system_configuration.microcontrollers.valve_calibration_pulse_count),
                tone_duration=np.uint32(tone_duration),
            )

        self.valve.tone()

    def configure_reward_parameters(self, volume: float = 5.0, tone_duration: int = 300) -> None:
        """Configures all future water rewards to use the provided volume and tone duration parameters.

        Primarily, this function is used to reconfigure the system from GUI and trigger reward delivery from Unity.

        Args:
            volume: The volume of water to deliver, in microliters.
            tone_duration: The duration of the auditory tone, in milliseconds, to emit while delivering the water
                reward.
        """
        if volume != self._previous_volume or tone_duration != self._previous_tone_duration:
            # Parameters are cached here to use the tone_duration before it is converted to microseconds.
            self._previous_volume = volume
            self._previous_tone_duration = tone_duration

            # Note, calibration parameters are not used by the command below, but we explicitly set them here for
            # consistency
            tone_duration: float = convert_time(time=tone_duration, from_units="ms", to_units="us")  # type: ignore
            self.valve.set_parameters(
                pulse_duration=self.valve.get_duration_from_volume(volume),
                calibration_delay=np.uint32(300000),  # Hardcoded for safety reasons!
                calibration_count=np.uint16(self._system_configuration.microcontrollers.valve_calibration_pulse_count),
                tone_duration=np.uint32(tone_duration),
            )

    def reference_valve(self) -> None:
        """Runs the reference valve calibration procedure.

        Reference calibration is functionally similar to the calibrate_valve() method runtime. It is, however, optimized
        to deliver the overall volume of water recognizable for the human eye looking at the syringe holding the water
        (water 'tank' used in our system). Additionally, this uses the 5 uL volume as the reference volume, which
        matches the volume we use during experiments and training sessions.

        The reference calibration HAS to be run with the water line being primed, deaerated, and the holding ('tank')
        syringe filled exactly to the 5 mL mark. This procedure is designed to dispense 5 uL of water 200 times, which
        should overall dispense ~ 1 ml of water.
        """
        tone_duration: float = convert_time(  # type: ignore
            time=self._system_configuration.microcontrollers.auditory_tone_duration_ms, from_units="ms", to_units="us"
        )
        self.valve.set_parameters(
            pulse_duration=np.uint32(self.valve.get_duration_from_volume(target_volume=5.0)),  # Hardcoded!
            calibration_delay=np.uint32(300000),  # Hardcoded for safety reasons!
            calibration_count=np.uint16(200),  # Hardcoded to work with the 5.0 uL volume to dispense 1 ml of water.
            tone_duration=np.uint32(tone_duration),
        )  # 5 ul x 200 times

        self.valve.calibrate()

    def calibrate_valve(self, pulse_duration: int = 15) -> None:
        """Cycles solenoid valve opening and closing 500 times to determine the amount of water dispensed by the input
        pulse_duration.

        The valve is kept open for the specified number of milliseconds. Between pulses, the valve is kept closed for
        300 ms. Due to our valve design, keeping the valve closed for less than 200-300 ms generates a large pressure
        at the third (Normally Open) port, which puts unnecessary strain on the port plug and internal mechanism of the
        valve.

        Notes:
            The calibration should be run with the following durations: 15 ms, 30 ms, 45 ms, and 60 ms. During testing,
            we found that these values cover the water reward range from 2 uL to 10 uL, which is enough to cover most
            training and experiment runtimes.

            Make sure that the water line is primed, deaerated, and the holding ('tank') syringe filled exactly to the
            5 mL mark at the beginning of each calibration cycle. Depending on the calibrated pulse_duration, you may
            need to refill the syringe during the calibration runtime.

        Args:
            pulse_duration: The duration, in milliseconds, the valve is kept open at each calibration cycle
        """
        pulse_us = pulse_duration * 1000  # Converts milliseconds to microseconds
        tone_duration: float = convert_time(  # type: ignore
            time=self._system_configuration.microcontrollers.auditory_tone_duration_ms, from_units="ms", to_units="us"
        )
        self.valve.set_parameters(
            pulse_duration=np.uint32(pulse_us),
            calibration_delay=np.uint32(300000),
            calibration_count=np.uint16(self._system_configuration.microcontrollers.valve_calibration_pulse_count),
            tone_duration=np.uint32(tone_duration),
        )
        self.valve.calibrate()

    def reset_mesoscope_frame_count(self) -> None:
        """Resets the mesoscope frame counter to 0."""
        self.mesoscope_frame.reset_pulse_count()

    def reset_distance_tracker(self) -> None:
        """Resets the total distance traveled by the animal since runtime onset and the current position of the animal
        relative to runtime onset to 0.
        """
        self.wheel_encoder.reset_distance_tracker()

    @property
    def mesoscope_frame_count(self) -> np.uint64:
        """Returns the total number of mesoscope frame acquisition pulses recorded since runtime onset."""
        return self.mesoscope_frame.pulse_count

    @property
    def delivered_water_volume(self) -> np.float64:
        """Returns the total volume of water, in microliters, dispensed by the valve since runtime onset."""
        return self.valve.delivered_volume

    @property
    def lick_count(self) -> np.uint64:
        """Returns the total number of licks recorded since runtime onset."""
        return self.lick.lick_count

    @property
    def traveled_distance(self) -> np.float64:
        """Returns the total distance, in centimeters, traveled by the animal since runtime onset.

        This value does not account for the direction of travel and is a monotonically increasing count of traveled
        centimeters.
        """
        return self.wheel_encoder.traveled_distance

    @property
    def position(self) -> np.float64:
        """Returns the current absolute position of the animal, in Unity units, relative to runtime onset."""
        return self.wheel_encoder.absolute_position


class VideoSystems:
    """Interfaces with all cameras managed by Ataraxis Video System (AVS) classes that acquire and save camera frames
    as .mp4 video files.

    This class interfaces with the three AVS cameras used during various runtimes to record animal behavior: the face
    camera and the two body cameras (the left camera and the right camera). The face camera is a high-grade scientific
    camera that records the animal's face and pupil. The left and right cameras are lower-end security cameras recording
    the animal's body from the left and right sides.

    Notes:
        This class is primarily intended to be used internally by the _MesoscopeExperiment and _BehaviorTraining
        classes. Do not initialize this class directly unless you know what you are doing.

        Calling the initializer does not start the underlying processes. Call the appropriate start() method to start
        acquiring and displaying face and body camera frames (there is a separate method for these two groups). Call
        the appropriate save() method to start saving the acquired frames to video files. Note that there is a single
        'global' stop() method that works for all cameras at the same time.

        The class is designed to be 'lock-in'. Once a camera is enabled, the only way to disable frame acquisition is to
        call the main stop() method. Similarly, once frame saving is started, there is no way to disable it without
        stopping the whole class. This is an intentional design decision optimized to the specific class use-pattern in
        our lab.

    Args:
        data_logger: The initialized DataLogger instance used to log the data generated by the managed cameras. For most
            runtimes, this argument is resolved by the _MesoscopeExperiment or _BehaviorTraining classes that
            initialize this class.
        output_directory: The path to the directory where to output the generated .mp4 video files. Each managed camera
            generates a separate video file saved in the provided directory. For most runtimes, this argument is
            resolved by the _MesoscopeExperiment or _BehaviorTraining classes that initialize this class.

    Attributes:
        _face_camera_started: Tracks whether the face camera frame acquisition is running.
        _body_cameras_started: Tracks whether the body cameras frame acquisition is running.
        _system_configuration: Stores the configuration parameters used by the Mesoscope-VR system.
        _face-camera: The interface that captures and saves the frames acquired by the 9MP scientific camera aimed at
            the animal's face and eye from the left side (via a hot mirror).
        _left_camera: The interface that captures and saves the frames acquired by the 1080P security camera aimed on
            the left side of the animal and the right and center VR screens.
        _right_camera: The interface that captures and saves the frames acquired by the 1080P security camera aimed on
            the right side of the animal and the left VR screen.
    """

    # noinspection PyTypeChecker
    def __init__(
        self,
        data_logger: DataLogger,
        output_directory: Path,
    ) -> None:
        # Creates the _started flags first to avoid leaks if the initialization method fails.
        self._face_camera_started: bool = False
        self._body_cameras_started: bool = False

        # Retrieves the Mesoscope-VR system configuration parameters and saves them to class attribute to use them from
        # class methods.
        self._system_configuration = get_system_configuration()

        # FACE CAMERA. This is the high-grade scientific camera aimed at the animal's face using the hot-mirror. It is
        # a 10-gigabit 9MP camera with a red long-pass filter and has to be interfaced through the GeniCam API. Since
        # the VRPC has a 4090 with 2 hardware acceleration chips, we are using the GPU to save all of our frame data.
        self._face_camera: VideoSystem = VideoSystem(
            system_id=np.uint8(51),  # Hardcoded
            data_logger=data_logger,
            output_directory=output_directory,
            harvesters_cti_path=self._system_configuration.paths.harvesters_cti_path,
        )
        # The acquisition parameters (framerate, frame dimensions, crop offsets, etc.) are set via the SVCapture64
        # software and written to non-volatile device memory. Generally, all projects in the lab should be using the
        # same parameters.
        self._face_camera.add_camera(
            save_frames=True,  # Hardcoded
            camera_index=self._system_configuration.cameras.face_camera_index,
            camera_backend=CameraBackends.HARVESTERS,  # Hardcoded
            output_frames=False,  # Hardcoded, as using queue output requires library refactoring anyway.
            display_frames=self._system_configuration.cameras.display_face_camera_frames,
            display_frame_rate=25,  # Hardcoded
        )
        self._face_camera.add_video_saver(
            hardware_encoding=True,  # Hardcoded
            video_format=VideoFormats.MP4,  # Hardcoded
            video_codec=VideoCodecs.H265,  # Hardcoded
            preset=GPUEncoderPresets.SLOW,  # Hardcoded
            input_pixel_format=InputPixelFormats.MONOCHROME,  # Hardcoded
            output_pixel_format=OutputPixelFormats.YUV444,  # Hardcoded
            quantization_parameter=self._system_configuration.cameras.face_camera_quantization_parameter,
        )

        # LEFT CAMERA. A 1080P security camera that is mounted on the left side from the mouse's perspective
        # (viewing the left side of the mouse and the right screen). This camera is interfaced with through the OpenCV
        # backend.
        self._left_camera: VideoSystem = VideoSystem(
            system_id=np.uint8(62), data_logger=data_logger, output_directory=output_directory
        )

        # DO NOT try to force the acquisition rate. If it is not 30 (default), the video will not save.
        self._left_camera.add_camera(
            save_frames=True,  # Hardcoded
            # The only difference between left and right cameras.
            camera_index=self._system_configuration.cameras.left_camera_index,
            camera_backend=CameraBackends.OPENCV,  # Hardcoded
            output_frames=False,  # Hardcoded, as using queue output requires library refactoring anyway.
            display_frames=self._system_configuration.cameras.display_body_camera_frames,
            display_frame_rate=25,  # Hardcoded
            color=False,  # Hardcoded
        )
        self._left_camera.add_video_saver(
            hardware_encoding=True,  # Hardcoded
            video_format=VideoFormats.MP4,  # Hardcoded
            video_codec=VideoCodecs.H265,  # Hardcoded
            preset=GPUEncoderPresets.FAST,  # Hardcoded
            input_pixel_format=InputPixelFormats.MONOCHROME,  # Hardcoded
            output_pixel_format=OutputPixelFormats.YUV420,  # Hardcoded
            quantization_parameter=self._system_configuration.cameras.body_camera_quantization_parameter,
        )

        # RIGHT CAMERA. Same as the left camera, but mounted on the right side from the mouse's perspective.
        self._right_camera: VideoSystem = VideoSystem(
            system_id=np.uint8(73), data_logger=data_logger, output_directory=output_directory
        )
        # Same as above, DO NOT force acquisition rate
        self._right_camera.add_camera(
            save_frames=True,  # Hardcoded
            # The only difference between left and right cameras.
            camera_index=self._system_configuration.cameras.right_camera_index,
            camera_backend=CameraBackends.OPENCV,
            output_frames=False,  # Hardcoded, as using queue output requires library refactoring anyway.
            display_frames=self._system_configuration.cameras.display_body_camera_frames,
            display_frame_rate=25,  # Hardcoded
            color=False,  # Hardcoded
        )
        self._right_camera.add_video_saver(
            hardware_encoding=True,  # Hardcoded
            video_format=VideoFormats.MP4,  # Hardcoded
            video_codec=VideoCodecs.H265,  # Hardcoded
            preset=GPUEncoderPresets.FAST,  # Hardcoded
            input_pixel_format=InputPixelFormats.MONOCHROME,  # Hardcoded
            output_pixel_format=OutputPixelFormats.YUV420,  # Hardcoded
            quantization_parameter=self._system_configuration.cameras.body_camera_quantization_parameter,
        )

    def __del__(self) -> None:
        """Ensures all hardware resources are released when the class is garbage-collected."""
        self.stop()

    def start_face_camera(self) -> None:
        """Starts face camera frame acquisition.

        This method sets up both the frame acquisition (producer) process and the frame saver (consumer) process.
        However, the consumer process will not save any frames until the save_face_camera_frames () method is called.
        """

        # Prevents executing this method if the face camera is already running
        if self._face_camera_started:
            return

        message = "Initializing face camera frame acquisition..."
        console.echo(message=message, level=LogLevel.INFO)

        # Starts frame acquisition. Note, this does NOT start frame saving.
        self._face_camera.start()
        self._face_camera_started = True

        message = "Face camera frame acquisition: Started."
        console.echo(message=message, level=LogLevel.SUCCESS)

    def start_body_cameras(self) -> None:
        """Starts left and right (body) camera frame acquisition.

        This method sets up both the frame acquisition (producer) process and the frame saver (consumer) process for
        both cameras. However, the consumer processes will not save any frames until the save_body_camera_frames ()
        method is called.
        """

        # Prevents executing this method if the body cameras are already running
        if self._body_cameras_started:
            return

        message = "Initializing body cameras (left and right) frame acquisition..."
        console.echo(message=message, level=LogLevel.INFO)

        # Starts frame acquisition. Note, this does NOT start frame saving.
        self._left_camera.start()
        self._right_camera.start()
        self._body_cameras_started = True

        message = "Body cameras frame acquisition: Started."
        console.echo(message=message, level=LogLevel.SUCCESS)

    def save_face_camera_frames(self) -> None:
        """Starts saving the frames acquired by the face camera as a video file."""

        # Starts frame saving process
        self._face_camera.start_frame_saving()

        message = "Face camera frame saving: Started."
        console.echo(message=message, level=LogLevel.SUCCESS)

    def save_body_camera_frames(self) -> None:
        """Starts saving the frames acquired by the left and right body cameras as a video file."""

        # Starts frame saving process
        self._left_camera.start_frame_saving()
        self._right_camera.start_frame_saving()

        message = "Body cameras frame saving: Started."
        console.echo(message=message, level=LogLevel.SUCCESS)

    def stop(self) -> None:
        """Stops saving all camera frames and terminates the managed VideoSystems.

        This method needs to be called at the end of each runtime to release the resources reserved by the start()
        methods. Until the stop() method is called, the DataLogger instance may receive data from running
        VideoSystems, so calling this method also guarantees no VideoSystem data will be lost if the DataLogger
        process is terminated. Similarly, this guarantees the integrity of the generated video files.
        """

        # Prevents executing this method if no cameras are running.
        if not self._face_camera_started and not self._body_cameras_started:
            return

        message = "Terminating Ataraxis Video System (AVS) Interfaces..."
        console.echo(message=message, level=LogLevel.INFO)

        # Instructs all cameras to stop saving frames
        self._face_camera.stop_frame_saving()
        self._left_camera.stop_frame_saving()
        self._right_camera.stop_frame_saving()

        message = "Camera frame saving: Stopped."
        console.echo(message=message, level=LogLevel.SUCCESS)

        # Stops all cameras
        self._face_camera.stop()
        self._left_camera.stop()
        self._right_camera.stop()

        # Marks all cameras as stopped
        self._face_camera_started = False
        self._body_cameras_started = False

        message = "Video Systems: Terminated."
        console.echo(message=message, level=LogLevel.SUCCESS)

    @property
    def face_camera_log_path(self) -> Path:
        """Returns the path to the compressed .npz archive that stores the data logged by the face camera during
        runtime."""
        return self._face_camera.log_path

    @property
    def left_camera_log_path(self) -> Path:
        """Returns the path to the compressed .npz archive that stores the data logged by the left body camera during
        runtime."""
        return self._left_camera.log_path

    @property
    def right_camera_log_path(self) -> Path:
        """Returns the path to the compressed .npz archive that stores the data logged by the right body camera during
        runtime."""
        return self._right_camera.log_path
