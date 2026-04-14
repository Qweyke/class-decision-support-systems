import json
from typing import Dict, List, Optional


class NeylorEngine:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Initial prior probabilities P(H)
        self.hypotheses: Dict[str, float] = data["hypotheses"]
        self.questions: List[Dict] = data["questions"]
        self.asked_questions: List[str] = []

    def update_probabilities(self, question_id: str, answer: bool):
        """
        Update hypothesis probabilities using Bayes' Theorem.
        P(H|E) = (P(E|H) * P(H)) / P(E)
        """
        question = next(q for q in self.questions if q["id"] == question_id)

        # 1. Calculate Total Probability P(E)
        # P(E) = sum( P(E|Hi) * P(Hi) )
        p_e = 0.0
        for h_name, p_h in self.hypotheses.items():
            p_e_h = question["p_e_h"].get(h_name, 0.5)

            # If user said 'No', we use inverse probability 1 - P(E|H)
            likelihood = p_e_h if answer else (1.0 - p_e_h)
            p_e += likelihood * p_h

        # 2. Update each P(H)
        if p_e > 0:
            for h_name in self.hypotheses:
                p_e_h = question["p_e_h"].get(h_name, 0.5)
                likelihood = p_e_h if answer else (1.0 - p_e_h)
                self.hypotheses[h_name] = (likelihood * self.hypotheses[h_name]) / p_e

        self.asked_questions.append(question_id)

    def skip_question(self, question_id: str):
        """
        Mark the question as asked without updating probabilities.
        """
        # We find the question and add it to the 'asked' list
        # so get_best_question() won't pick it again.
        if question_id not in self.asked_questions:
            self.asked_questions.append(question_id)

    def get_best_question(self) -> Optional[Dict]:
        """
        Find the question with the highest Information Gain.
        Naylor's approach: find a question that causes the maximum shift in probabilities.
        """
        _, prob = self.get_top_hypothesis()

        # If we are 80% sure, stop and show the result
        if prob >= 0.8:
            return None

        best_q = None
        max_gain = -1.0

        for q in self.questions:
            if q["id"] in self.asked_questions:
                continue

            # Simplified cost calculation: Sum of absolute differences
            gain = 0.0
            for h_name, p_h in self.hypotheses.items():
                p_e_h = q["p_e_h"].get(h_name, 0.5)
                # How much would P(H) change if answer is Yes vs No
                gain += abs(p_e_h - (1.0 - p_e_h)) * p_h

            if gain > max_gain:
                max_gain = gain
                best_q = q

        if max_gain < 0.01:
            return None

        return best_q

    def get_top_hypothesis(self) -> tuple:
        best_h = max(self.hypotheses.items(), key=lambda x: x[1])
        return best_h
