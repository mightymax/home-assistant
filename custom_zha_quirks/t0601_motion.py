

"""TS0601_TZE204_yensya2c"""

import math
from typing import Dict, Tuple#, Union, Optional, 
from zigpy.profiles import zha#, zgp
from zigpy.quirks import CustomDevice
import zigpy.types as t
from zigpy.zcl.clusters.general import (
    AnalogInput,
    AnalogOutput,
    Basic,
    Groups,
    Ota,
    Scenes,
    Time,
)
from zigpy.zcl.clusters.measurement import (
    IlluminanceMeasurement,
    OccupancySensing,
    TemperatureMeasurement,
    PressureMeasurement,
)
from zhaquirks import Bus, LocalDataCluster, MotionOnEvent
from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.tuya import (
    NoManufacturerCluster,
    TuyaLocalCluster,
    TuyaNewManufCluster,
)
from zhaquirks.tuya.mcu import (
    DPToAttributeMapping,
    TuyaAttributesCluster,
    TuyaMCUCluster,
)
class TuyaOccupancySensing(OccupancySensing, TuyaLocalCluster):
    """Tuya local OccupancySensing cluster."""

class TuyaMmwRadarDetectionDelay(TuyaAttributesCluster, AnalogOutput):
    """AnalogOutput cluster for detection delay."""

    _CONSTANT_ATTRIBUTES = {
        AnalogOutput.AttributeDefs.description.id: "detection_delay",
        AnalogOutput.AttributeDefs.min_present_value.id: 1, # min allowed = 1
        AnalogOutput.AttributeDefs.max_present_value.id: 60, # max allowed = 3600
        AnalogOutput.AttributeDefs.resolution.id: 1,# Resolution = 1 second
        AnalogOutput.AttributeDefs.engineering_units.id: 73,  # Expects seconds.  73: seconds 159: milliseconds 
    }

class TuyaIlluminanceMeasurement(IlluminanceMeasurement, TuyaLocalCluster): # result in lux
    """Tuya local IlluminanceMeasurement cluster."""

class TuyaTemperatureMeasurement(TemperatureMeasurement, TuyaLocalCluster): # result in seconds
    """Remaining FadeTime."""

class TuyaPressureMeasurement(PressureMeasurement, TuyaLocalCluster): # result in centermeteres 
    """Target Distance."""

class TuyaMmwRadarSensitivity(TuyaAttributesCluster, AnalogOutput):
    """AnalogOutput cluster for sensitivity."""
    
    _CONSTANT_ATTRIBUTES = {
        AnalogOutput.AttributeDefs.description.id: "sensitivity",
        AnalogOutput.AttributeDefs.min_present_value.id: 0, # min allowed = 0
        AnalogOutput.AttributeDefs.max_present_value.id: 10, # max allowed = 10
        AnalogOutput.AttributeDefs.resolution.id: 1, #resolution = 1
    }
    
class TuyaMmwRadarFadingTime(TuyaAttributesCluster, AnalogOutput):
    """AnalogOutput cluster for fading time."""

    _CONSTANT_ATTRIBUTES = {
        AnalogOutput.AttributeDefs.description.id: "fading_time",
        AnalogOutput.AttributeDefs.min_present_value.id: 5, #min allowed is 5
        AnalogOutput.AttributeDefs.max_present_value.id: 600, #max allowed is 3600
        AnalogOutput.AttributeDefs.resolution.id: 5, # Resolution 5 seconds 
        AnalogOutput.AttributeDefs.engineering_units.id: 73,  #expects seconds, 73 defines seconds 159: milliseconds 
    }
    
class TuyaMmwRadarMinRange(TuyaAttributesCluster, AnalogOutput):
    """AnalogOutput cluster for min range."""

    _CONSTANT_ATTRIBUTES = {
        AnalogOutput.AttributeDefs.description.id: "min_range",
        AnalogOutput.AttributeDefs.min_present_value.id: 0, # min allowed = 0
        AnalogOutput.AttributeDefs.max_present_value.id: 1000, # max allowed  = 1000
        AnalogOutput.AttributeDefs.resolution.id: 50, # resolution = 50 centermeteres 
        AnalogOutput.AttributeDefs.engineering_units.id: 118,  #expects centermeteres.  31: defines meters 118: defines centermeteres 
    }
    
class TuyaMmwRadarMaxRange(TuyaAttributesCluster, AnalogOutput):
    """AnalogOutput cluster for max range."""

    _CONSTANT_ATTRIBUTES = {
        AnalogOutput.AttributeDefs.description.id: "max_range",
        AnalogOutput.AttributeDefs.min_present_value.id: 50, # min allowed  = 50
        AnalogOutput.AttributeDefs.max_present_value.id: 1000, # max allowed  = 1000
        AnalogOutput.AttributeDefs.resolution.id: 50, #resolution = 50 centermeters
        AnalogOutput.AttributeDefs.engineering_units.id: 118,  #expects centermeteres.  31: defines meters 118: defines centermeteres 
    }

class TuyaMmwRadarClusterBase(NoManufacturerCluster, TuyaMCUCluster):
    """Mmw radar cluster, base class."""

    attributes = TuyaMCUCluster.attributes.copy()
    attributes.update(
        {
            # ramdom attribute IDs
            0xEF01: ("occupancy", t.uint32_t, True),
            0xEF02: ("detection_delay", t.uint32_t, True),
            0xEF03: ("illuminance", t.uint32_t, True),
            0xEF04: ("sensitivity", t.uint32_t, True),
            0xEF05: ("fading_time", t.uint32_t, True),
            0xEF65: ("min_range", t.uint32_t, True),
            0xEF66: ("max_range", t.uint32_t, True),
            0xEF67: ("pressure_measurement", t.uint32_t, True),# = Target Distance 
            0xEF68: ("temperature_measurement", t.uint32_t, True), # = Remaining Fade Time 
        }
    )

class TuyaMmwRadarCluster(TuyaMmwRadarClusterBase):
    """Mmw radar cluster."""

    dp_to_attribute: Dict[int, DPToAttributeMapping] = {
        1: DPToAttributeMapping(
            TuyaOccupancySensing.ep_attribute,
            "occupancy",
        ),
        12: DPToAttributeMapping(
            TuyaMmwRadarDetectionDelay.ep_attribute,
            "present_value",
            endpoint_id=4,
        ),
        19: DPToAttributeMapping(
            TuyaPressureMeasurement.ep_attribute, # = Target Distance 
            "measured_value",
            endpoint_id=7,
        ),
        20: DPToAttributeMapping(
            TuyaIlluminanceMeasurement.ep_attribute,
            "measured_value",
            #converter=lambda x: int(math.log10(max(x, 1)) * 10000) + 10000 if x > 0 else int(0),
            converter=lambda x: int(math.log10(x) * 10000 + 1) + 10000 if x > 0 else int(0),
        ),
        101: DPToAttributeMapping(
            TuyaMmwRadarSensitivity.ep_attribute,
            "present_value",
        ),
        102: DPToAttributeMapping(
            TuyaMmwRadarFadingTime.ep_attribute,
            "present_value",
            endpoint_id=5,
        ),
        111: DPToAttributeMapping(
            TuyaMmwRadarMinRange.ep_attribute,
            "present_value",
            endpoint_id=2,
        ),
        112: DPToAttributeMapping(
            TuyaMmwRadarMaxRange.ep_attribute,
            "present_value",
            endpoint_id=3,
        ),
        116: DPToAttributeMapping(
            TuyaTemperatureMeasurement.ep_attribute, # = Remaining Fade Time 
            "measured_value",
            converter=lambda x: x * 100, #Corrects displayed value to fit available sensor
            endpoint_id=6,
        ),
    }

    data_point_handlers = {
          1: "_dp_2_attr_update",
         12: "_dp_2_attr_update",
         19: "_dp_2_attr_update", 
         20: "_dp_2_attr_update", 
        101: "_dp_2_attr_update",
        102: "_dp_2_attr_update",
        111: "_dp_2_attr_update",
        112: "_dp_2_attr_update",
        116: "_dp_2_attr_update",
    }

class TuyaMmwRadarOccupancy(CustomDevice):
    """Millimeter wave occupancy sensor."""
    signature = {
        MODELS_INFO: [("_TZE204_qasjif9e", "TS0601")],
        
        ENDPOINTS: {
            # <SimpleDescriptor endpoint=1 profile=260 device_type=81
            # device_version=1
            # input_clusters=[4, 5, 61184, 0000]
            # output_clusters=[25, 10]>       

            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaNewManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.OCCUPANCY_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaMmwRadarCluster,
                    TuyaIlluminanceMeasurement,
                    TuyaOccupancySensing,
                    TuyaMmwRadarSensitivity,
                ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.COMBINED_INTERFACE,
                INPUT_CLUSTERS: [
                    TuyaMmwRadarMinRange,
                ],
                OUTPUT_CLUSTERS: [],
            },
            3: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.COMBINED_INTERFACE,
                INPUT_CLUSTERS: [
                    TuyaMmwRadarMaxRange,
                ],
                OUTPUT_CLUSTERS: [],
            },
            4: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.COMBINED_INTERFACE,
                INPUT_CLUSTERS: [
                    TuyaMmwRadarDetectionDelay,
                ],
                OUTPUT_CLUSTERS: [],
            },
            5: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.COMBINED_INTERFACE,
                INPUT_CLUSTERS: [
                    TuyaMmwRadarFadingTime,
                ],
                OUTPUT_CLUSTERS: [],
            },
            6: {       # could be icluded in endpoint 1 if wanted
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.OCCUPANCY_SENSOR,
                INPUT_CLUSTERS: [
                    TuyaTemperatureMeasurement,
                ],
                OUTPUT_CLUSTERS: [],
            },
            7: {         # could be included in endpoint 1 if wanted
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.OCCUPANCY_SENSOR,
                INPUT_CLUSTERS: [
                    TuyaPressureMeasurement
                ],
                OUTPUT_CLUSTERS: [],
            },


            
        }
    }
