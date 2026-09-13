# knowledge/facts.py

class Fact:

    def __init__(self, key: str, value):
        self.key = key
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Fact):
            return (
                self.key == other.key
                and self.value == other.value
            )
        return False

    def __hash__(self):

        return hash((self.key, self.value))

    def __repr__(self):
        return f"Fact({self.key} = {self.value})"


def normalize_symptom(symptom):

    if symptom is None:
        return None

    symptom = str(symptom).strip().lower()

    if not symptom:
        return None

    # Thay khoảng trắng bằng dấu _
    symptom = "_".join(symptom.split())

    return symptom


def extract_facts_from_patient(patient) -> list[Fact]:

    facts = []

    # ==========================================================
    # 1. TRÍCH XUẤT TRIỆU CHỨNG
    # ==========================================================

    symptoms = getattr(patient, "symptoms", [])

    # Trường hợp symptoms là list
    if isinstance(symptoms, list):

        for symptom in symptoms:

            normalized_symptom = normalize_symptom(symptom)

            if normalized_symptom:
                fact = Fact(
                    key=normalized_symptom,
                    value=True
                )

                if fact not in facts:
                    facts.append(fact)

    # Trường hợp symptoms là chuỗi:
    # "fever, chest_pain, headache"
    elif isinstance(symptoms, str) and symptoms.strip():

        for symptom in symptoms.split(","):

            normalized_symptom = normalize_symptom(symptom)

            if normalized_symptom:
                fact = Fact(
                    key=normalized_symptom,
                    value=True
                )

                if fact not in facts:
                    facts.append(fact)

    # ==========================================================
    # 2. TRÍCH XUẤT TÌNH TRẠNG CẤP CỨU
    # ==========================================================

    emergency = getattr(
        patient,
        "emergency",
        None
    )

    # Hỗ trợ thêm trường emergency_level nếu project
    # có sử dụng tên này ở nơi khác.
    if not emergency:
        emergency = getattr(
            patient,
            "emergency_level",
            None
        )

    if emergency:

        emergency_value = str(
            emergency
        ).strip().upper()

        facts.append(
            Fact(
                key="emergency",
                value=emergency_value
            )
        )

    # ==========================================================
    # 3. TRÍCH XUẤT MỨC ĐỘ NGHIÊM TRỌNG
    # ==========================================================

    severity = getattr(
        patient,
        "severity",
        None
    )

    if severity:

        severity_value = str(
            severity
        ).strip().upper()

        facts.append(
            Fact(
                key="severity",
                value=severity_value
            )
        )

    # ==========================================================
    # 4. TRÍCH XUẤT HUYẾT ÁP CAO
    # ==========================================================

    high_blood_pressure = getattr(
        patient,
        "high_blood_pressure",
        False
    )

    if high_blood_pressure:
        facts.append(
            Fact(
                key="high_blood_pressure",
                value=True
            )
        )

    # ==========================================================
    # 5. TRÍCH XUẤT TUỔI
    # ==========================================================

    age = getattr(
        patient,
        "age",
        None
    )

    if age is not None:

        try:
            age_value = int(age)

            facts.append(
                Fact(
                    key="age",
                    value=age_value
                )
            )

            # ==================================================
            # 6. XÁC ĐỊNH BỆNH NHÂN CAO TUỔI
            # ==================================================

            if age_value >= 65:

                facts.append(
                    Fact(
                        key="is_elderly",
                        value=True
                    )
                )

        except (ValueError, TypeError):
            # Nếu tuổi không hợp lệ thì bỏ qua,
            # không làm chương trình bị crash.
            pass

    return facts