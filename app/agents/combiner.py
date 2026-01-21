"""
Combiner Agent - Systemising Ba (시스템화의 장)

Phase 3 of SECI: Combination (형식지 → 형식지)

Analyzes externalized knowledge and connects it to business opportunities.
Creates Business Opportunity Cards as output.
"""

import json
from typing import Optional
from anthropic import Anthropic

from prompts.seci_prompts import (
    COMBINER_SYSTEM_PROMPT,
    COMBINER_BUSINESS_CARD_PROMPT
)
from models.knowledge import (
    TacitKnowledgeSpec,
    BusinessOpportunityCard,
    KnowledgeAssetScore,
    BusinessOpportunity,
    BusinessOpportunityType,
    TransferDifficulty
)


class Combiner:
    """
    연결자 Agent - 연결화 단계를 담당

    역할:
    - 암묵지 명세서를 분석하여 비즈니스 가치 평가
    - 시장 수요와 매칭
    - 상품화 방향 제안
    - 비즈니스 기회 카드 3개 생성
    """

    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-20250514"):
        self.client = client
        self.model = model
        self.knowledge_spec: Optional[TacitKnowledgeSpec] = None
        self.business_card: Optional[BusinessOpportunityCard] = None
        self.is_complete = False

    def reset(self):
        """초기화"""
        self.knowledge_spec = None
        self.business_card = None
        self.is_complete = False

    def set_knowledge_spec(self, knowledge_spec: TacitKnowledgeSpec):
        """암묵지 명세서 설정"""
        self.knowledge_spec = knowledge_spec

    def generate_business_card(self) -> BusinessOpportunityCard:
        """
        비즈니스 기회 카드 생성

        Returns:
            BusinessOpportunityCard: 생성된 비즈니스 기회 카드
        """
        if not self.knowledge_spec:
            raise ValueError("암묵지 명세서가 설정되지 않았습니다.")

        # 암묵지 명세서를 프롬프트에 포함
        knowledge_spec_json = self.knowledge_spec.model_dump_json(indent=2)

        prompt = f"""다음은 표출화 단계에서 생성된 암묵지 명세서입니다:

```json
{knowledge_spec_json}
```

{COMBINER_BUSINESS_CARD_PROMPT}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            system=COMBINER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        json_str = self._extract_json(response_text)

        try:
            data = json.loads(json_str)
            self.business_card = BusinessOpportunityCard(**data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"JSON 파싱 오류: {e}")
            self.business_card = self._create_fallback_card()

        self.is_complete = True
        return self.business_card

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

    def _create_fallback_card(self) -> BusinessOpportunityCard:
        """파싱 실패 시 기본 비즈니스 기회 카드 생성"""
        return BusinessOpportunityCard(
            knowledge_asset=KnowledgeAssetScore(
                name=self.knowledge_spec.knowledge_name if self.knowledge_spec else "미확인",
                scarcity_score=3,
                demand_score=3,
                transferability_score=3
            ),
            business_opportunities=[
                BusinessOpportunity(
                    opportunity_name="추가 분석 필요",
                    type=BusinessOpportunityType.KNOWLEDGE_TRANSFER,
                    target_customer="추가 분석 필요",
                    value_proposition="추가 분석 필요",
                    product_format="추가 분석 필요",
                    difficulty=TransferDifficulty.MEDIUM,
                    first_step="비즈니스 기회 분석을 다시 시도해주세요"
                )
            ],
            recommended_opportunity="추가 분석이 필요합니다"
        )

    def get_summary(self) -> str:
        """비즈니스 기회 카드 요약 반환"""
        if not self.business_card:
            return "비즈니스 기회 카드가 아직 생성되지 않았습니다."

        card = self.business_card
        asset = card.knowledge_asset

        summary_parts = [
            f"## 지식 자산: {asset.name}",
            f"- 희소성: {'★' * asset.scarcity_score}{'☆' * (5 - asset.scarcity_score)}",
            f"- 수요: {'★' * asset.demand_score}{'☆' * (5 - asset.demand_score)}",
            f"- 전달가능성: {'★' * asset.transferability_score}{'☆' * (5 - asset.transferability_score)}",
            "",
            "## 비즈니스 기회"
        ]

        for i, opp in enumerate(card.business_opportunities, 1):
            summary_parts.extend([
                f"\n### 기회 {i}: {opp.opportunity_name}",
                f"- 유형: {opp.type.value}",
                f"- 타겟: {opp.target_customer}",
                f"- 가치: {opp.value_proposition}",
                f"- 상품 형태: {opp.product_format}",
                f"- 난이도: {opp.difficulty.value}",
                f"- 첫 번째 행동: {opp.first_step}"
            ])

        summary_parts.extend([
            "",
            f"## 추천",
            card.recommended_opportunity
        ])

        return "\n".join(summary_parts)

    def force_complete(self):
        """강제로 단계 완료 처리"""
        self.is_complete = True
