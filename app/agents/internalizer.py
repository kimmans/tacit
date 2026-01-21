"""
Internalizer Agent - Exercising Ba (실천의 장)

Phase 4 of SECI: Internalization (형식지 → 암묵지)

Converts business opportunities into actionable plans.
Creates Action Plan as output.
"""

import json
from typing import Optional
from anthropic import Anthropic

from prompts.seci_prompts import (
    INTERNALIZER_SYSTEM_PROMPT,
    INTERNALIZER_ACTION_PLAN_PROMPT
)
from models.knowledge import (
    BusinessOpportunityCard,
    ActionPlan,
    Experiment,
    ValidationMetric,
    FirstCustomer,
    Obstacle
)


class Internalizer:
    """
    내면화 촉진자 Agent - 내면화 단계를 담당

    역할:
    - 비즈니스 기회를 구체적 액션플랜으로 전환
    - 가장 작은 실험 설계
    - 검증 지표 설정
    - 피드백 루프 구축
    """

    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-20250514"):
        self.client = client
        self.model = model
        self.business_card: Optional[BusinessOpportunityCard] = None
        self.action_plan: Optional[ActionPlan] = None
        self.is_complete = False

    def reset(self):
        """초기화"""
        self.business_card = None
        self.action_plan = None
        self.is_complete = False

    def set_business_card(self, business_card: BusinessOpportunityCard):
        """비즈니스 기회 카드 설정"""
        self.business_card = business_card

    def generate_action_plan(self) -> ActionPlan:
        """
        주간 액션플랜 생성

        Returns:
            ActionPlan: 생성된 액션플랜
        """
        if not self.business_card:
            raise ValueError("비즈니스 기회 카드가 설정되지 않았습니다.")

        # 비즈니스 기회 카드를 프롬프트에 포함
        business_card_json = self.business_card.model_dump_json(indent=2)

        prompt = f"""다음은 연결화 단계에서 생성된 비즈니스 기회 카드입니다:

```json
{business_card_json}
```

{INTERNALIZER_ACTION_PLAN_PROMPT}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            system=INTERNALIZER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        json_str = self._extract_json(response_text)

        try:
            data = json.loads(json_str)
            self.action_plan = ActionPlan(**data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"JSON 파싱 오류: {e}")
            self.action_plan = self._create_fallback_plan()

        self.is_complete = True
        return self.action_plan

    def _extract_json(self, text: str) -> str:
        """텍스트에서 JSON 블록 추출"""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return text[start:end]

        return text

    def _create_fallback_plan(self) -> ActionPlan:
        """파싱 실패 시 기본 액션플랜 생성"""
        return ActionPlan(
            selected_opportunity="추가 분석 필요",
            this_week_experiments=[
                Experiment(
                    experiment_name="기본 실험",
                    description="액션플랜 생성을 위해 추가 분석이 필요합니다",
                    expected_outcome="미정",
                    success_criteria="미정",
                    time_required="미정",
                    resources_needed="미정"
                )
            ],
            validation_metrics=[
                ValidationMetric(
                    metric_name="기본 지표",
                    how_to_measure="추가 분석 필요",
                    target_value="미정"
                )
            ],
            first_customer=FirstCustomer(
                who="추가 분석 필요",
                why_them="추가 분석 필요",
                how_to_reach="추가 분석 필요"
            ),
            next_session_checklist=["액션플랜 재생성 시도"],
            potential_obstacles=[
                Obstacle(
                    obstacle="액션플랜 생성 실패",
                    mitigation="다시 시도해주세요"
                )
            ]
        )

    def get_summary(self) -> str:
        """액션플랜 요약 반환"""
        if not self.action_plan:
            return "액션플랜이 아직 생성되지 않았습니다."

        plan = self.action_plan

        summary_parts = [
            f"## 선택된 비즈니스 기회",
            f"{plan.selected_opportunity}",
            "",
            "## 이번 주 실험"
        ]

        for i, exp in enumerate(plan.this_week_experiments, 1):
            summary_parts.extend([
                f"\n### 실험 {i}: {exp.experiment_name}",
                f"- 설명: {exp.description}",
                f"- 기대 결과: {exp.expected_outcome}",
                f"- 성공 기준: {exp.success_criteria}",
                f"- 소요 시간: {exp.time_required}",
                f"- 필요 자원: {exp.resources_needed}"
            ])

        summary_parts.extend([
            "",
            "## 검증 지표"
        ])

        for metric in plan.validation_metrics:
            summary_parts.extend([
                f"- **{metric.metric_name}**",
                f"  - 측정 방법: {metric.how_to_measure}",
                f"  - 목표: {metric.target_value}"
            ])

        summary_parts.extend([
            "",
            "## 첫 번째 고객",
            f"- 누구: {plan.first_customer.who}",
            f"- 이유: {plan.first_customer.why_them}",
            f"- 접근 방법: {plan.first_customer.how_to_reach}",
            "",
            "## 다음 세션 체크리스트"
        ])

        for item in plan.next_session_checklist:
            summary_parts.append(f"- [ ] {item}")

        summary_parts.extend([
            "",
            "## 예상 장애물"
        ])

        for obs in plan.potential_obstacles:
            summary_parts.extend([
                f"- **{obs.obstacle}**",
                f"  - 대응: {obs.mitigation}"
            ])

        return "\n".join(summary_parts)

    def force_complete(self):
        """강제로 단계 완료 처리"""
        self.is_complete = True
