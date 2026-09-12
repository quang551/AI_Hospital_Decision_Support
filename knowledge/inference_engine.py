# knowledge/inference_engine.py

from knowledge.facts import Fact
from knowledge.rules import Rule


class InferenceEngine:


    def __init__(self, rules: list[Rule]):
        # Tập luật của Knowledge Base
        self.rules = rules

    def run(self, initial_facts: list[Fact]) -> dict:


        # ======================================================
        # 1. KHỞI TẠO TẬP FACTS
        # ======================================================

        known_facts = list(initial_facts)

        # Danh sách Rule đã được kích hoạt
        fired_rules = []

        # Các bước suy luận để hiển thị trên GUI
        reasoning_steps = []

        # ======================================================
        # 2. FORWARD CHAINING
        # ======================================================

        while True:

            rule_fired_in_this_loop = False

            # Duyệt toàn bộ Knowledge Base
            for rule in self.rules:

                # Rule chỉ được kích hoạt một lần
                if rule.rule_id in fired_rules:
                    continue

                # Kiểm tra tất cả điều kiện của Rule
                if rule.matches(known_facts):

                    # ------------------------------------------
                    # Rule được kích hoạt
                    # ------------------------------------------

                    fired_rules.append(rule.rule_id)
                    rule_fired_in_this_loop = True

                    # Nếu Fact mới chưa tồn tại thì thêm vào
                    if rule.consequence not in known_facts:
                        known_facts.append(rule.consequence)

                    # ------------------------------------------
                    # Ghi lại quá trình suy luận
                    # ------------------------------------------

                    step_msg = (
                        f"Kích hoạt [{rule.rule_id}]: "
                        f"{rule.description} "
                        f"==> Sinh ra Fact mới: "
                        f"{rule.consequence}"
                    )

                    reasoning_steps.append(step_msg)

                    # Dừng vòng lặp hiện tại.
                    # Sau đó quét lại Knowledge Base từ đầu
                    # vì có thể Fact mới vừa được sinh ra.
                    break

            # Không còn Rule nào được kích hoạt
            if not rule_fired_in_this_loop:
                break

        # ======================================================
        # 3. XÁC ĐỊNH RISK
        # ======================================================

        final_risk = "LOW"

        # Thứ tự mức độ Risk
        risk_levels = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }

        highest_risk = 0

        for fact in known_facts:

            if fact.key == "risk":

                risk_value = str(
                    fact.value
                ).upper()

                risk_score = risk_levels.get(
                    risk_value,
                    0
                )

                # Chỉ lấy Risk cao nhất
                if risk_score > highest_risk:

                    highest_risk = risk_score
                    final_risk = risk_value

        # ======================================================
        # 4. XÁC ĐỊNH PRIORITY
        # ======================================================

        final_priority = "LOW"

        # Thứ tự ưu tiên:
        #
        # CRITICAL > HIGH > MEDIUM > LOW
        #
        priority_levels = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }

        highest_priority = 0

        for fact in known_facts:

            if fact.key == "priority":

                priority_value = str(
                    fact.value
                ).upper()

                priority_score = priority_levels.get(
                    priority_value,
                    0
                )

                # Chỉ lấy Priority cao nhất
                if priority_score > highest_priority:

                    highest_priority = priority_score
                    final_priority = priority_value

        # ======================================================
        # 5. TRẢ KẾT QUẢ
        # ======================================================

        return {
            "priority": final_priority,
            "risk": final_risk,
            "all_facts": known_facts,
            "activated_rules": fired_rules,
            "reasoning_steps": reasoning_steps
        }