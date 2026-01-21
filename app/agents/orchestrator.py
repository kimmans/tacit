"""
SECI Orchestrator - Knowledge Creation Spiral Manager

Manages the flow through SECI phases:
1. Socialization (S) - 사회화
2. Externalization (E) - 표출화
3. Combination (C) - 연결화
4. Internalization (I) - 내면화

Each phase corresponds to a Ba (場):
- Originating Ba (S)
- Dialoguing Ba (E)
- Systemising Ba (C)
- Exercising Ba (I)
"""

from enum import Enum
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from anthropic import Anthropic

from agents.socializer import Socializer
from agents.externalizer import Externalizer
from agents.combiner import Combiner
from agents.internalizer import Internalizer
from models.knowledge import (
    ExperienceMap,
    TacitKnowledgeSpec,
    BusinessOpportunityCard,
    ActionPlan
)


class SECIPhase(str, Enum):
    """SECI 모델의 4단계"""
    SOCIALIZATION = "socialization"      # S: 사회화 (암묵지→암묵지)
    EXTERNALIZATION = "externalization"  # E: 표출화 (암묵지→형식지)
    COMBINATION = "combination"          # C: 연결화 (형식지→형식지)
    INTERNALIZATION = "internalization"  # I: 내면화 (형식지→암묵지)
    COMPLETE = "complete"                # 나선 완료


class Ba(str, Enum):
    """Ba(場) - 지식창조의 장"""
    ORIGINATING = "originating"    # 창발의 장 (S)
    DIALOGUING = "dialoguing"      # 대화의 장 (E)
    SYSTEMISING = "systemising"    # 시스템화의 장 (C)
    EXERCISING = "exercising"      # 실천의 장 (I)


# Phase와 Ba 매핑
PHASE_TO_BA = {
    SECIPhase.SOCIALIZATION: Ba.ORIGINATING,
    SECIPhase.EXTERNALIZATION: Ba.DIALOGUING,
    SECIPhase.COMBINATION: Ba.SYSTEMISING,
    SECIPhase.INTERNALIZATION: Ba.EXERCISING,
}

BA_DESCRIPTIONS = {
    Ba.ORIGINATING: "창발의 장 (Originating Ba) - 공감과 경험 공유의 공간",
    Ba.DIALOGUING: "대화의 장 (Dialoguing Ba) - 대화를 통한 개념화의 공간",
    Ba.SYSTEMISING: "시스템화의 장 (Systemising Ba) - 지식 조합과 문서화의 공간",
    Ba.EXERCISING: "실천의 장 (Exercising Ba) - 실행과 체화의 공간",
}


@dataclass
class SECIState:
    """SECI 나선의 현재 상태"""
    phase: SECIPhase = SECIPhase.SOCIALIZATION
    spiral_count: int = 1  # 몇 번째 나선인지

    # Phase별 산출물
    experience_map: Optional[ExperienceMap] = None
    knowledge_spec: Optional[TacitKnowledgeSpec] = None
    business_card: Optional[BusinessOpportunityCard] = None
    action_plan: Optional[ActionPlan] = None

    # 대화 기록
    conversation_history: Dict[SECIPhase, list] = field(default_factory=dict)


class SECIOrchestrator:
    """
    SECI 나선 관리자

    지식창조의 나선형 과정을 관리하고,
    각 단계의 Agent를 조율합니다.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

        # Agent 초기화
        self.socializer = Socializer(self.client, model)
        self.externalizer = Externalizer(self.client, model)
        self.combiner = Combiner(self.client, model)
        self.internalizer = Internalizer(self.client, model)

        # 상태 초기화
        self.state = SECIState()

    def reset(self):
        """전체 초기화"""
        self.state = SECIState()
        self.socializer.reset()
        self.externalizer.reset()
        self.combiner.reset()
        self.internalizer.reset()

    @property
    def current_phase(self) -> SECIPhase:
        """현재 단계"""
        return self.state.phase

    @property
    def current_ba(self) -> Ba:
        """현재 Ba(場)"""
        return PHASE_TO_BA.get(self.state.phase, Ba.ORIGINATING)

    @property
    def current_ba_description(self) -> str:
        """현재 Ba 설명"""
        return BA_DESCRIPTIONS.get(self.current_ba, "")

    def get_phase_info(self) -> Dict[str, Any]:
        """현재 단계 정보 반환"""
        phase_names = {
            SECIPhase.SOCIALIZATION: "사회화 (Socialization)",
            SECIPhase.EXTERNALIZATION: "표출화 (Externalization)",
            SECIPhase.COMBINATION: "연결화 (Combination)",
            SECIPhase.INTERNALIZATION: "내면화 (Internalization)",
            SECIPhase.COMPLETE: "완료",
        }

        phase_descriptions = {
            SECIPhase.SOCIALIZATION: "암묵지 → 암묵지: 경험과 감정을 공유하며 암묵지가 숨어있는 영역을 탐색합니다.",
            SECIPhase.EXTERNALIZATION: "암묵지 → 형식지: 소크라테스식 대화로 암묵지를 언어화합니다.",
            SECIPhase.COMBINATION: "형식지 → 형식지: 표출된 지식을 비즈니스 기회와 연결합니다.",
            SECIPhase.INTERNALIZATION: "형식지 → 암묵지: 지식을 실행 가능한 액션플랜으로 전환합니다.",
            SECIPhase.COMPLETE: "SECI 나선이 완료되었습니다.",
        }

        return {
            "phase": self.state.phase.value,
            "phase_name": phase_names[self.state.phase],
            "phase_description": phase_descriptions[self.state.phase],
            "ba": self.current_ba.value,
            "ba_description": self.current_ba_description,
            "spiral_count": self.state.spiral_count,
        }

    def chat(self, user_message: str) -> Tuple[str, Dict[str, Any]]:
        """
        사용자 메시지 처리

        Args:
            user_message: 사용자 메시지

        Returns:
            Tuple[str, Dict]: (AI 응답, 상태 정보)
        """
        response = ""
        phase_changed = False

        if self.state.phase == SECIPhase.SOCIALIZATION:
            response, is_complete = self.socializer.chat(user_message)

            if is_complete:
                # 경험 지도 생성 후 다음 단계로
                self.state.experience_map = self.socializer.generate_experience_map()
                self._advance_phase()
                phase_changed = True

        elif self.state.phase == SECIPhase.EXTERNALIZATION:
            # 첫 대화라면 초기 메시지 생성
            if not self.externalizer.conversation_history:
                self.externalizer.set_experience_map(self.state.experience_map)
                initial = self.externalizer.get_initial_message()
                return initial, self.get_phase_info()

            response, is_complete = self.externalizer.chat(user_message)

            if is_complete:
                # 암묵지 명세서 생성 후 다음 단계로
                self.state.knowledge_spec = self.externalizer.generate_knowledge_spec()
                self._advance_phase()
                phase_changed = True

        elif self.state.phase == SECIPhase.COMBINATION:
            # 연결화 단계: 비즈니스 기회 카드 생성
            if not self.combiner.business_card:
                self.combiner.set_knowledge_spec(self.state.knowledge_spec)
                self.state.business_card = self.combiner.generate_business_card()
                response = self._format_combination_result()
                self._advance_phase()
                phase_changed = True
            else:
                response = self._format_combination_result()

        elif self.state.phase == SECIPhase.INTERNALIZATION:
            # 내면화 단계: 액션플랜 생성
            if not self.internalizer.action_plan:
                self.internalizer.set_business_card(self.state.business_card)
                self.state.action_plan = self.internalizer.generate_action_plan()
                response = self._format_internalization_result()
                self._advance_phase()
                phase_changed = True
            else:
                response = self._format_internalization_result()

        info = self.get_phase_info()
        info["phase_changed"] = phase_changed

        return response, info

    def _advance_phase(self):
        """다음 단계로 진행"""
        phase_order = [
            SECIPhase.SOCIALIZATION,
            SECIPhase.EXTERNALIZATION,
            SECIPhase.COMBINATION,
            SECIPhase.INTERNALIZATION,
            SECIPhase.COMPLETE,
        ]

        current_idx = phase_order.index(self.state.phase)
        if current_idx < len(phase_order) - 1:
            self.state.phase = phase_order[current_idx + 1]

    def force_advance_phase(self):
        """강제로 다음 단계로 진행 (테스트/디버그용)"""
        if self.state.phase == SECIPhase.SOCIALIZATION:
            self.socializer.force_complete()
            self.state.experience_map = self.socializer.generate_experience_map()

        elif self.state.phase == SECIPhase.EXTERNALIZATION:
            self.externalizer.force_complete()
            self.state.knowledge_spec = self.externalizer.generate_knowledge_spec()

        elif self.state.phase == SECIPhase.COMBINATION:
            if self.state.knowledge_spec:
                self.combiner.set_knowledge_spec(self.state.knowledge_spec)
                self.state.business_card = self.combiner.generate_business_card()

        elif self.state.phase == SECIPhase.INTERNALIZATION:
            if self.state.business_card:
                self.internalizer.set_business_card(self.state.business_card)
                self.state.action_plan = self.internalizer.generate_action_plan()

        self._advance_phase()

    def _format_combination_result(self) -> str:
        """연결화 단계 결과 포맷팅"""
        if not self.state.business_card:
            return "비즈니스 기회 카드가 생성되지 않았습니다."

        return f"""## 🔗 연결화 단계 완료!

시스템화의 장(Systemising Ba)에서 당신의 암묵지를 비즈니스 기회와 연결했습니다.

{self.combiner.get_summary()}

---

다음은 **내면화 단계**입니다.
실천의 장(Exercising Ba)에서 구체적인 액션플랜을 만들어 드리겠습니다.

**"계속"**이라고 입력하시면 내면화 단계로 진행합니다."""

    def _format_internalization_result(self) -> str:
        """내면화 단계 결과 포맷팅"""
        if not self.state.action_plan:
            return "액션플랜이 생성되지 않았습니다."

        return f"""## 🎯 내면화 단계 완료!

실천의 장(Exercising Ba)에서 실행 가능한 액션플랜을 만들었습니다.

{self.internalizer.get_summary()}

---

## 🎉 SECI 나선 1바퀴 완료!

당신의 암묵지가 다음과 같이 변환되었습니다:

1. **사회화** → 경험 지도 (암묵지가 숨어있는 영역 발견)
2. **표출화** → 암묵지 명세서 (말할 수 없던 것을 언어화)
3. **연결화** → 비즈니스 기회 카드 (지식의 시장 가치 발견)
4. **내면화** → 액션플랜 (실천으로 연결)

> *"We can know more than we can tell"* — Michael Polanyi
> 이제 당신은 말할 수 있게 되었습니다.

**"처음부터"**라고 입력하시면 새로운 SECI 나선을 시작합니다."""

    def get_current_output(self) -> Optional[Any]:
        """현재 단계의 산출물 반환"""
        if self.state.phase == SECIPhase.EXTERNALIZATION:
            return self.state.experience_map
        elif self.state.phase == SECIPhase.COMBINATION:
            return self.state.knowledge_spec
        elif self.state.phase == SECIPhase.INTERNALIZATION:
            return self.state.business_card
        elif self.state.phase == SECIPhase.COMPLETE:
            return self.state.action_plan
        return None

    def get_all_outputs(self) -> Dict[str, Any]:
        """모든 산출물 반환"""
        outputs = {}

        if self.state.experience_map:
            outputs["experience_map"] = self.state.experience_map.model_dump()

        if self.state.knowledge_spec:
            outputs["knowledge_spec"] = self.state.knowledge_spec.model_dump()

        if self.state.business_card:
            outputs["business_card"] = self.state.business_card.model_dump()

        if self.state.action_plan:
            outputs["action_plan"] = self.state.action_plan.model_dump()

        return outputs

    def get_welcome_message(self) -> str:
        """환영 메시지"""
        return """안녕하세요! **Tacit** 서비스에 오신 것을 환영합니다.

저는 당신의 **암묵지(Tacit Knowledge)**를 발견하고,
비즈니스 기회로 연결해드리는 AI 파트너입니다.

> *"We can know more than we can tell"*
> — Michael Polanyi

지금부터 **SECI 지식창조 나선**을 시작합니다.

**첫 번째 단계: 사회화 (Socialization)**
창발의 장(Originating Ba)에서 당신의 경험을 탐색합니다.

먼저 간단히 자기소개를 부탁드릴게요.
**어떤 일을 하시고, 얼마나 오래 하셨나요?**"""
