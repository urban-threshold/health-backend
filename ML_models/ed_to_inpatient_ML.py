import joblib
import pandas as pd
from typing import Dict, Union
import os

class EDToInpatientPredictor:
    def __init__(self, model_path: str = "ed_admit_model.joblib"):
        """
        Initialize the predictor with a trained model.
        
        Args:
            model_path: Path to the joblib file containing the trained model
        """
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, model_path)
        
        # Load the model artifacts
        artifact = joblib.load(full_path)
        self.pipeline = artifact["pipeline"]
        self.features = artifact["features"]

    def predict(self, patient_data: Dict[str, Union[int, float]]) -> float:
        """
        Predict the probability of a patient requiring inpatient care.
        
        Args:
            patient_data: Dictionary containing patient features:
                - triage_category: int (1-5)
                - age: int
                - primary_diagnosis_ICD10AM_chapter: int
                - affected_by_drugs_and_or_alcohol: int (0 or 1)
                - mental_health_admission: int (0 or 1)
                
        Returns:
            float: Probability (0-1) that the patient will require inpatient care
        
        Example:
            predictor = EDToInpatientPredictor()
            prob = predictor.predict({
                'triage_category': 5,
                'age': 50,
                'primary_diagnosis_ICD10AM_chapter': 11,
                'affected_by_drugs_and_or_alcohol': 0,
                'mental_health_admission': 0
            })
        """
        # Validate input features
        missing_features = set(self.features) - set(patient_data.keys())
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        # Create DataFrame with proper column order
        X_new = pd.DataFrame([patient_data], columns=self.features)
        
        # Get prediction probability
        probability = float(self.pipeline.predict_proba(X_new)[:, 1][0])
        
        
        return probability


if __name__ == "__main__":
    # Example usage
    predictor = EDToInpatientPredictor()
    
    test_patient = {
        'triage_category': 5,
        'age': 50,
        'primary_diagnosis_ICD10AM_chapter': 11,
        'affected_by_drugs_and_or_alcohol': 0,
        'mental_health_admission': 0
    }
    
    prob = predictor.predict(test_patient)
    print(f"\nPatient has {prob*100:.2f}% probability of requiring inpatient care.")