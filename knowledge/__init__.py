# tests/test_reasoning.py
import sys
import os
import unittest

#đường dẫn để Python nhận diện thư mục knowledge/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facts import Fact, extract_facts_from_patient
from rules import get_default_knowledge_base
from inference_engine import InferenceEngine


class MockPatient:
    """Lớp bệnh nhân giả lập để test"""
    def __init__(self, symptoms=None, high_blood_pressure=False, emergency=None, age=30):
        self.symptoms = symptoms or []
        self.high_blood_pressure = high_blood_pressure
        self.emergency = emergency
        self.age = age


class TestAIReasoning(unittest.TestCase):

    def test_critical_patient(self):
        """Test Bệnh nhân nguy cấp -> Phải suy ra CRITICAL"""
        rules = get_default_knowledge_base()
        engine = InferenceEngine(rules)

        patient = MockPatient(
            symptoms=["chest_pain"],
            high_blood_pressure=True,
            emergency="HIGH"
        )
        facts = extract_facts_from_patient(patient)
        result = engine.run(facts)

        self.assertEqual(result["risk"], "HIGH")
        self.assertEqual(result["priority"], "CRITICAL")
        self.assertIn("R1", result["activated_rules"])
        self.assertIn("R2", result["activated_rules"])

    def test_normal_patient(self):
        """Test Bệnh nhân nhẹ -> Mặc định là NORMAL"""
        rules = get_default_knowledge_base()
        engine = InferenceEngine(rules)

        patient = MockPatient(symptoms=["headache"])
        facts = extract_facts_from_patient(patient)
        result = engine.run(facts)

        self.assertEqual(result["risk"], "LOW")
        self.assertEqual(result["priority"], "NORMAL")
        self.assertEqual(len(result["activated_rules"]), 0)


if __name__ == "__main__":
    # Cho phép bấm nút Run trực tiếp file này
    unittest.main()