# knowledge/rules.py

from knowledge.facts import Fact


class Rule:
    """
    Đại diện cho một luật trong Knowledge Base.

    Cấu trúc:
        IF conditions
        THEN consequence
    """

    def __init__(
        self,
        rule_id: str,
        conditions: list[Fact],
        consequence: Fact,
        description: str = ""
    ):
        self.rule_id = rule_id
        self.conditions = conditions
        self.consequence = consequence
        self.description = description

    def matches(self, current_facts: list[Fact]) -> bool:
        """
        Kiểm tra tất cả điều kiện của Rule có nằm trong
        danh sách Facts hiện tại hay không.
        """

        for condition in self.conditions:
            if condition not in current_facts:
                return False

        return True

    def __repr__(self):
        return (
            f"Rule({self.rule_id}: "
            f"IF {self.conditions} "
            f"THEN {self.consequence})"
        )


def get_default_knowledge_base() -> list[Rule]:


    return [

        # ======================================================
        # NHÓM 1 - SUY LUẬN RISK TỪ TRIỆU CHỨNG
        # ======================================================

        # R1:
        # Đau ngực + huyết áp cao
        # -> nguy cơ HIGH
        Rule(
            rule_id="R1",
            conditions=[
                Fact("chest_pain", True),
                Fact("high_blood_pressure", True)
            ],
            consequence=Fact("risk", "HIGH"),
            description=(
                "Bệnh nhân bị đau ngực kèm huyết áp cao "
                "có nguy cơ cao."
            )
        ),

        # R2:
        # Sốt + khó thở
        # -> nguy cơ MEDIUM
        Rule(
            rule_id="R2",
            conditions=[
                Fact("fever", True),
                Fact("shortness_of_breath", True)
            ],
            consequence=Fact("risk", "MEDIUM"),
            description=(
                "Bệnh nhân sốt kèm khó thở "
                "xếp nguy cơ trung bình."
            )
        ),

        # ======================================================
        # NHÓM 2 - SUY LUẬN PRIORITY TỪ RISK + EMERGENCY
        # ======================================================

        # R3:
        # Risk HIGH + Emergency HIGH
        # -> CRITICAL
        Rule(
            rule_id="R3",
            conditions=[
                Fact("risk", "HIGH"),
                Fact("emergency", "HIGH")
            ],
            consequence=Fact("priority", "CRITICAL"),
            description=(
                "Bệnh nhân nguy cơ cao và tình trạng "
                "khẩn cấp xếp loại CRITICAL."
            )
        ),

        # R4:
        # Risk HIGH
        # -> HIGH
        Rule(
            rule_id="R4",
            conditions=[
                Fact("risk", "HIGH")
            ],
            consequence=Fact("priority", "HIGH"),
            description=(
                "Bệnh nhân có nguy cơ cao "
                "được xếp độ ưu tiên HIGH."
            )
        ),

        # R5:
        # Risk MEDIUM
        # -> HIGH
        Rule(
            rule_id="R5",
            conditions=[
                Fact("risk", "MEDIUM")
            ],
            consequence=Fact("priority", "HIGH"),
            description=(
                "Bệnh nhân có nguy cơ trung bình "
                "được ưu tiên khám sớm ở mức HIGH."
            )
        ),

        # ======================================================
        # NHÓM 3 - SUY LUẬN TỪ SEVERITY
        # ======================================================

        # R6:
        # Severity CRITICAL
        # -> CRITICAL
        Rule(
            rule_id="R6",
            conditions=[
                Fact("severity", "CRITICAL")
            ],
            consequence=Fact("priority", "CRITICAL"),
            description=(
                "Bệnh nhân có mức độ nghiêm trọng CRITICAL "
                "được ưu tiên CRITICAL."
            )
        ),

        # R7:
        # Severity HIGH
        # -> HIGH
        Rule(
            rule_id="R7",
            conditions=[
                Fact("severity", "HIGH")
            ],
            consequence=Fact("priority", "HIGH"),
            description=(
                "Bệnh nhân có mức độ nghiêm trọng HIGH "
                "được ưu tiên HIGH."
            )
        ),

        # R8:
        # Severity MEDIUM
        # -> MEDIUM
        Rule(
            rule_id="R8",
            conditions=[
                Fact("severity", "MEDIUM")
            ],
            consequence=Fact("priority", "MEDIUM"),
            description=(
                "Bệnh nhân có mức độ nghiêm trọng MEDIUM "
                "được ưu tiên MEDIUM."
            )
        ),

        # R9:
        # Severity LOW
        # -> LOW
        Rule(
            rule_id="R9",
            conditions=[
                Fact("severity", "LOW")
            ],
            consequence=Fact("priority", "LOW"),
            description=(
                "Bệnh nhân có mức độ nghiêm trọng LOW "
                "được ưu tiên LOW."
            )
        ),

        # ======================================================
        # NHÓM 4 - TÌNH TRẠNG CẤP CỨU
        # ======================================================

        # R10:
        # Emergency CRITICAL
        # -> CRITICAL
        Rule(
            rule_id="R10",
            conditions=[
                Fact("emergency", "CRITICAL")
            ],
            consequence=Fact("priority", "CRITICAL"),
            description=(
                "Bệnh nhân có tình trạng cấp cứu CRITICAL "
                "được ưu tiên CRITICAL."
            )
        ),

        # R11:
        # Emergency HIGH
        # -> HIGH
        Rule(
            rule_id="R11",
            conditions=[
                Fact("emergency", "HIGH")
            ],
            consequence=Fact("priority", "HIGH"),
            description=(
                "Bệnh nhân có tình trạng cấp cứu HIGH "
                "được ưu tiên HIGH."
            )
        ),

        # ======================================================
        # NHÓM 5 - NGƯỜI CAO TUỔI
        # ======================================================

        # R12:
        # Người cao tuổi + sốt
        # -> HIGH
        Rule(
            rule_id="R12",
            conditions=[
                Fact("is_elderly", True),
                Fact("fever", True)
            ],
            consequence=Fact("priority", "HIGH"),
            description=(
                "Người cao tuổi bị sốt "
                "cần được ưu tiên khám sớm."
            )
        )
    ]