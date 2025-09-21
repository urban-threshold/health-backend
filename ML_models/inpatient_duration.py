import random

class InpatientDurationPredictor:
    def __init__(self, inpatient_duration_min, inpatient_duration_max):
        self.inpatient_duration_min = inpatient_duration_min
        self.inpatient_duration_max = inpatient_duration_max

    def predict_inpatient_duration_in_minutes(self, patient):
        return random.randint(self.inpatient_duration_min, self.inpatient_duration_max)