# knowledge/inference_engine.py
from facts import Fact
from rules import Rule

class InferenceEngine:
    """
    Động cơ suy luận Forward Chaining cho hệ thống AI y tế.
    """
    def __init__(self, rules: list[Rule]):
        self.rules = rules  # Tập luật (Knowledge Base)

    def run(self, initial_facts: list[Fact]) -> dict:
        """
        Thực hiện thuật toán Forward Chaining dựa trên tập Facts ban đầu.
        """
        known_facts = list(initial_facts)  # Tập tri thức hiện tại
        fired_rules = []                   # Danh sách mã Rule đã kích hoạt
        reasoning_steps = []               # Các bước suy luận dùng để giải thích trên GUI

        while True:
            rule_fired_in_this_loop = False

            for rule in self.rules:
                # Điều kiện kích hoạt Rule:
                # 1. Rule này chưa từng kích hoạt trước đó
                # 2. TẤT CẢ các điều kiện (conditions) của Rule đều có trong known_facts
                if rule.rule_id not in fired_rules and rule.matches(known_facts):
                    # Kích hoạt (Fire) Rule!
                    fired_rules.append(rule.rule_id)
                    rule_fired_in_this_loop = True

                    # Nếu kết luận (consequence) chưa có trong tập tri thức -> thêm vào
                    if rule.consequence not in known_facts:
                        known_facts.append(rule.consequence)

                    # Ghi nhận bước suy luận để giải thích (Explainable AI)
                    step_msg = (
                        f"Kích hoạt [{rule.rule_id}]: {rule.description} "
                        f"==> Sinh ra Fact mới: {rule.consequence}"
                    )
                    reasoning_steps.append(step_msg)

                    # Ngắt vòng lặp nhỏ để quét lại tập luật từ đầu với tập Facts mới
                    break

            # Nếu chạy hết danh sách Luật mà không có Luật nào thỏa mãn thêm -> Dừng thuật toán
            if not rule_fired_in_this_loop:
                break

        # Bóc tách kết quả Độ ưu tiên (Priority) và Mức độ nguy cơ (Risk) cuối cùng
        final_priority = "NORMAL"  # Mặc định nếu không kích hoạt Rule ưu tiên nào
        final_risk = "LOW"

        for fact in known_facts:
            if fact.key == "priority":
                final_priority = fact.value
            elif fact.key == "risk":
                final_risk = fact.value

        return {
            "priority": final_priority,
            "risk": final_risk,
            "all_facts": known_facts,
            "activated_rules": fired_rules,
            "reasoning_steps": reasoning_steps
        }