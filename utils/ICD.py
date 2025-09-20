from typing import Dict, Tuple, Union
from dataclasses import dataclass

@dataclass
class ICDCategory:
    id: int
    description: str
    code: str

    def to_dict(self) -> Dict[str, Union[int, str]]:
        return {
            "id": self.id,
            "description": self.description,
            "code": self.code
        }

# Main mapping of ICD categories
ICD_CATEGORIES = {
    1: ICDCategory(1, "Certain infectious and parasitic diseases", "A0"),
    2: ICDCategory(2, "Neoplasms", "C0"),
    3: ICDCategory(3, "Diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism", "D5"),
    4: ICDCategory(4, "Endocrine, nutritional and metabolic diseases", "E0"),
    5: ICDCategory(5, "Mental and behavioural disorders", "F0"),
    6: ICDCategory(6, "Diseases of the nervous system", "G0"),
    7: ICDCategory(7, "Diseases of the eye and adnexa", "H0"),
    8: ICDCategory(8, "Diseases of the ear and mastoid process", "H6"),
    9: ICDCategory(9, "Diseases of the circulatory system", "I0"),
    10: ICDCategory(10, "Diseases of the respiratory system", "J0"),
    11: ICDCategory(11, "Diseases of the digestive system", "K0"),
    12: ICDCategory(12, "Diseases of the skin and subcutaneous tissue", "L0"),
    13: ICDCategory(13, "Diseases of the musculoskeletal system and connective tissue", "M0"),
    14: ICDCategory(14, "Diseases of the genitourinary system", "N0"),
    15: ICDCategory(15, "Pregnancy, childbirth and the puerperium", "O0"),
    16: ICDCategory(16, "Certain conditions originating in the perinatal period", "P0"),
    17: ICDCategory(17, "Congenital malformations, deformations and chromosomal abnormalities", "Q0"),
    18: ICDCategory(18, "Symptoms, signs and abnormal clinical and laboratory findings, not elsewhere classified", "R0"),
    19: ICDCategory(19, "Injury, poisoning and certain other consequences of external causes", "S0"),
    20: ICDCategory(20, "External causes of morbidity and mortality", "U5"),
    21: ICDCategory(21, "Factors influencing health status and contact with health services", "Z0"),
    22: ICDCategory(22, "Codes for special purposes", "U0")
}

# Create reverse mappings
CODE_TO_ID = {cat.code: cat_id for cat_id, cat in ICD_CATEGORIES.items()}
DESCRIPTION_TO_ID = {cat.description: cat_id for cat_id, cat in ICD_CATEGORIES.items()}

def get_category_by_id(category_id: int) -> Dict[str, Union[str, int]]:

    if category_id not in ICD_CATEGORIES:
        raise ValueError(f"Invalid category ID: {category_id}. Must be between 1 and 22.")
    return ICD_CATEGORIES[category_id].to_dict()

def get_category_by_code(code: str) -> Dict[str, Union[str, int]]:

    if code not in CODE_TO_ID:
        raise ValueError(f"Invalid ICD code: {code}")
    return ICD_CATEGORIES[CODE_TO_ID[code]].to_dict()

def get_category_by_description(description: str) -> Dict[str, Union[str, int]]:

    if description not in DESCRIPTION_TO_ID:
        raise ValueError(f"Invalid ICD description: {description}")
    return ICD_CATEGORIES[DESCRIPTION_TO_ID[description]].to_dict()

# Example usage:
if __name__ == "__main__":
    # Get by ID
    print(get_category_by_id(2))  
    # Output: {'id': 2, 'description': 'Neoplasms', 'code': 'C0'}
    
    # Get by code
    print(get_category_by_code("C0"))  
    # Output: {'id': 2, 'description': 'Neoplasms', 'code': 'C0'}
    
    # Get by description
    print(get_category_by_description("Neoplasms"))  
    # Output: {'id': 2, 'description': 'Neoplasms', 'code': 'C0'}
