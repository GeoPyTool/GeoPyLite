import chaquopy
# chaquopy

def get_available_sensors():
    sensors = chaquopy.getModule("android.hardware").getAvailableSensors()
    return sensors

available_sensors = get_available_sensors()
print(available_sensors)
