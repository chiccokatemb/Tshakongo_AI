
class SimpleAvoid:
    def __init__(self, lidar, drive, stop_dist=0.35, cruise=0.25):
        self.lidar, self.drive = lidar, drive
        self.stop_dist, self.cruise = stop_dist, cruise
    def tick(self):
        d = self.lidar.min_distance()
        if d is None:
            self.drive.stop(); return "Lidar?"
        if d < self.stop_dist:
            self.drive.stop(); return f"Stop {d:.2f}m"
        else:
            self.drive.forward(self.cruise); return f"Go {self.cruise}"
