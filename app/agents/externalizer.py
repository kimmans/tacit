"""
Externalizer Agent - Dialoguing Ba (대화의 장)

Phase 2 of SECI: Externalization (암묵지 → 형식지)

Uses Socratic dialogue to extract tacit knowledge and convert it
into explicit knowledge. Creates Tacit Knowledge Specification as output.
"""

import json
from typing import List, Optional, Tuple
from anthropic import Anthropic

from prompts.seci_prompts import (
    EXTERNALIZER_SYSTEM_PROMPT,
    EXTERNALIZER_KNOWLEDGE_SPEC_PROMPT
)
from models.knowledge import ExperienceMap, TacitKnowledgeSpec


class Externalizer:
    """
    표출자 Agent - 표출화 단계를 담당

    역할:
    - 소크라테스식 대화로 암묵지 언어화
    - 폴라니의 역설 돌파: "말할 수 없는 것"을 말하게
    - 암묵지 명세서(Tacit Knowledge Specification) 생성
    """

    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-20250514"):
        self.client = client
        self.model = model
        self.conversation_history: List[dict] = []
        self.is_complete = False
        self.knowledge_spec: Optional[TacitKnowledgeSpec] = None
        self.experience_map: Optional[ExperienceMap] = None
        self.current_focus_area: Optional[str] = None

    def reset(self):
        """대화 초기화"""
        self.conversation_history = []
        self.is_complete = False
        self.knowledge_spec = None
        self.current_focus_area = None

    def set_experience_map(self, experience_map: ExperienceMap):
        """경험 지도 설정"""
        self.experience_map = experience_map

        # 추천된 포커스 영역 설정
        if experience_map.tacit_knowledge_candidates:
            # 감정적 무게가 높은 것 우선
            high_weight = [
                c for c in experience_map.tacit_knowledge_candidates
                if c.emotional_weight.value == "높음"
            ]
            if high_weight:
                self.current_focus_area = high_weight[0].area
            else:
                self.current_focus_area = experience_map.tacit_knowledge_candidates[0].area

    def get_initial_message(self) -> str:
        """초기 메시지 생성"""
        if not self.experience_map:
            return "안녕하세요! 경험 지도를 먼저 설정해주세요."

        focus = self.current_focus_area or "암묵지"

        initial_prompt = f"""지금부터 '대화의 장(Dialoguing Ba)'을 시작합니다.

경험 지도를 바탕으로, '{focus}' 영역을 깊이 탐색하겠습니다.

경험 지도 정보:
- 사용자: {self.experience_map.user_profile.role} ({self.experience_map.user_profile.experience_years} 경력)
- 분야: {self.experience_map.user_profile.domain}
- 탐색 영역: {focus}
- 추천 이유: {self.experience_map.recommended_focus}

이 영역에서 사용자의 암묵지를 끌어내기 위한 첫 질문을 해주세요.
소크라테스식 대화법을 사용하고, 구체적인 상황을 물어보세요."""

        # 시스템 프롬프트와 함께 초기 대화 생성
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=EXTERNALIZER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": initial_prompt}]
        )

        assistant_message = response.content[0].text

        # 대화 히스토리 시작
        self.conversation_history = [
            {"role": "user", "content": initial_prompt},
            {"role": "assistant", "content": assistant_message}
        ]

        return assistant_message

    def chat(self, user_message: str) -> Tuple[str, bool]:
        """
        사용자와 대화

        Args:
            user_message: 사용자 메시지

        Returns:
            Tuple[str, bool]: (AI 응답, 단계 완료 여부)
        """
        # 대화 히스토리에 사용자 메시지 추가
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Claude API 호출
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=EXTERNALIZER_SYSTEM_PROMPT,
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text

        # 대화 히스토리에 AI 응답 추가
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # 충분한 정보가 모였는지 확인
        # 최소 6턴 이상 대화하고, 규칙/패턴이 발견되면 완료 가능
        if len(self.conversation_history) >= 12:  # 6턴 = 12개 메시지
            if self._has_enough_information():
                self.is_complete = True

        return assistant_message, self.is_complete

    def _has_enough_information(self) -> bool:
        """충분한 정보가 수집되었는지 확인"""
        full_conversation = " ".join([
            msg["content"] for msg in self.conversation_history
        ])

        # 표출화에서 찾아야 할 키워드들
        keywords = [
            "규칙", "패턴", "판단", "기준", "신호", "느낌",
            "비유", "은유", "예외", "실수", "초보", "경험"
        ]
        found_keywords = sum(1 for kw in keywords if kw in full_conversation)

        return found_keywords >= 5

    def generate_knowledge_spec(self) -> TacitKnowledgeSpec:
        """
        암묵지 명세서 생성

        Returns:
            TacitKnowledgeSpec: 생성된 암묵지 명세서
        """
        # 암묵지 명세서 생성 프롬프트 추가
        messages = self.conversation_history + [{
            "role": "user",
            "content": EXTERNALIZER_KNOWLEDGE_SPEC_PROMPT
        }]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            system=EXTERNALIZER_SYSTEM_PROMPT,
            messages=messages
        )

        # JSON 파싱
        response_text = response.content[0].text
        json_str = self._extract_json(response_text)

        try:
            data = json.loads(json_str)
            self.knowledge_spec = TacitKnowledgeSpec(**data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"JSON 파싱 오류: {e}")
            self.knowledge_spec = self._create_fallback_spec(response_text)

        return self.knowledge_spec

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

    def _create_fallback_spec(self, text: str) -> TacitKnowledgeSpec:
        """파싱 실패 시 기본 암묵지 명세서 생성"""
        from models.knowledge import TransferDifficulty

        return TacitKnowledgeSpec(
            knowledge_name="추가 분석 필요",
            summary="암묵지 명세서 생성을 위해 추가 분석이 필요합니다",
            detailed_description="대화 내용을 바탕으로 암묵지 명세서를 생성하는 데 실패했습니다. "
                                "추가 대화나 수동 분석이 필요합니다.",
            trigger_signals=["미확인"],
            decision_rules=["미확인"],
            exceptions=["미확인"],
            metaphor="미확인",
            sensory_cues=[],
            common_mistakes=[],
            transfer_difficulty=TransferDifficulty.MEDIUM,
            transfer_method="추가 분석 필요",
            evidence_quotes=[]
        )

    def get_conversation_summary(self) -> str:
        """대화 요약 반환"""
        if not self.conversation_history:
            return "아직 대화가 시작되지 않았습니다."

        # 첫 번째 시스템 설정 메시지는 제외
        display_history = self.conversation_history[2:] if len(self.conversation_history) > 2 else self.conversation_history

        summary_parts = []
        for msg in display_history:
            role = "사용자" if msg["role"] == "user" else "표출자"
            content = msg["content"][:150] + "..." if len(msg["content"]) > 150 else msg["content"]
            summary_parts.append(f"{role}: {content}")

        return "\n".join(summary_parts)

    def force_complete(self):
        """강제로 단계 완료 처리"""
        self.is_complete = True
