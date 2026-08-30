# knowledge/rules.py
from facts import Fact

class Rule:
    def __init__(self, rule_id: str, conditions: list[Fact], consequence: Fact, description: str = ""):
        self.rule_id = rule_id          # Mã luật (vd: 'R1', 'R2')
        self.conditions = conditions    # Danh sách các Fact cần thỏa mãn (phép AND)
        self.consequence = consequence  # Fact mới sẽ sinh ra khi Rule kích hoạt
        self.description = description  # Mô tả đọc được để hiển thị lên GUI

    def matches(self, current_facts: list[Fact]) -> bool:
        """Kiểm tra xem TẤT CẢ conditions của Rule có nằm trong current_facts hay không."""
        for cond in self.conditions:
            if cond not in current_facts:
                return False
        return True

    def __repr__(self):
        return f"Rule({self.rule_id}: IF {self.conditions} THEN {self.consequence})"


def get_default_knowledge_base() -> list[Rule]:
    """Khai báo tập Knowledge Base cố định cho bệnh viện."""
    return [
        # R1: Nguy cơ cao do đau ngực & huyết áp cao
        Rule(
            rule_id="R1",
            conditions=[Fact("chest_pain", True), Fact("high_blood_pressure", True)],
            consequence=Fact("risk", "HIGH"),
            description="Bệnh nhân bị đau ngực kèm huyết áp cao có nguy cơ cao."
        ),
        
        # R2: Đưa vào cấp cứu CRITICAL nếu nguy cơ cao + emergency HIGH
        Rule(
            rule_id="R2",
            conditions=[Fact("risk", "HIGH"), Fact("emergency", "HIGH")],
            consequence=Fact("priority", "CRITICAL"),
            description="Bệnh nhân nguy cơ cao và tình trạng khẩn cấp xếp loại CRITICAL."
        ),

        # R3: Nguy cơ trung bình do sốt & khó thở
        Rule(
            rule_id="R3",
            conditions=[Fact("fever", True), Fact("shortness_of_breath", True)],
            consequence=Fact("risk", "MEDIUM"),
            description="Bệnh nhân sốt kèm khó thở xếp nguy cơ trung bình."
        ),

        # R4: Xếp độ ưu tiên HIGH cho người nguy cơ trung bình
        Rule(
            rule_id="R4",
            conditions=[Fact("risk", "MEDIUM")],
            consequence=Fact("priority", "HIGH"),
            description="Bệnh nhân nguy cơ trung bình xếp độ ưu tiên HIGH."
        ),

        # R5: Ưu tiên cho người cao tuổi có triệu chứng
        Rule(
            rule_id="R5",
            conditions=[Fact("is_elderly", True), Fact("fever", True)],
            consequence=Fact("priority", "HIGH"),
            description="Người cao tuổi bị sốt cần được ưu tiên khám sớm."
        )
    ]