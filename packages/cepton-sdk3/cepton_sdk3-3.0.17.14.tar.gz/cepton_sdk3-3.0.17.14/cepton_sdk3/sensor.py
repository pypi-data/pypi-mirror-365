import queue

class Sensor:
    sensors = {}

    def __init__(self):
        self.info = {}


    @classmethod
    def find_or_create_by_handle(cls, handle):
        if (handle not in cls.sensors): 
            cls.sensors[handle] = Sensor()
        return cls.sensors[handle]

    @staticmethod
    def get_count():
        return len(Sensor.sensors)

    @staticmethod
    def get_all_handles():
        return list(Sensor.sensors.keys())

    def update_info(self, info):
        self.info.update(info)

    def get_information(self):
        return self.info

