# knowledge/facts.py

class Fact:
    """
    Cấu trúc đại diện cho một Fact (Sự thật/Mệnh đề) trong Knowledge Base.
    Lưu trữ dạng Key-Value (Ví dụ: key="chest_pain", value=True)
    """
    def __init__(self, key: str, value: any):
        self.key = key
        self.value = value

    def __eq__(self, other):
        # Đè toán tử == để so sánh 2 Fact có giống hệt nhau về Key và Value không
        if isinstance(other, Fact):
            return self.key == other.key and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.key, self.value))

    def __repr__(self):
        return f"Fact({self.key} = {self.value})"


def extract_facts_from_patient(patient) -> list[Fact]:
    """
    Hàm tự động trích xuất các Facts ban đầu từ đối tượng Patient.
    Chuyển dữ liệu thô của bệnh nhân thành tri thức đầu vào cho AI.
    """
    facts = []

    # 1. Trích xuất các triệu chứng (symptoms)
    # Giả sử patient.symptoms là danh sách các chuỗi triệu chứng
    symptoms = getattr(patient, 'symptoms', [])
    if isinstance(symptoms, list):
        for symptom in symptoms:
            facts.append(Fact(key=symptom, value=True))
    elif isinstance(symptoms, str) and symptoms:
        # Trường hợp triệu chứng nhập dạng chuỗi phân tách bằng dấu phẩy
        for symptom in symptoms.split(','):
            facts.append(Fact(key=symptom.strip(), value=True))

    # 2. Trích xuất chỉ số cấp cứu ban đầu (nếu có)
    emergency = getattr(patient, 'emergency', None) or getattr(patient, 'emergency_level', None)
    if emergency:
        facts.append(Fact(key="emergency", value=str(emergency).upper()))

    # 3. Trích xuất tiền sử / chỉ số sinh hiệu đặc biệt
    if getattr(patient, 'high_blood_pressure', False):
        facts.append(Fact(key="high_blood_pressure", value=True))

    # 4. Trích xuất độ tuổi
    age = getattr(patient, 'age', None)
    if age is not None:
        facts.append(Fact(key="age", value=int(age)))
        if int(age) >= 65:
            facts.append(Fact(key="is_elderly", value=True))

    return facts