from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
import re

app = FastAPI(title='Jev JudgeOps', version='0.1.0')

class EvaluationRequest(BaseModel):
    question: str = Field(min_length=1, max_length=50000)
    answer: str = Field(min_length=1, max_length=50000)
    context: str = Field(min_length=1, max_length=50000)

class EvaluationResult(BaseModel):
    verdict: Literal['pass', 'fail', 'review']
    score: float
    evidence: list[str]
    evaluator: str = 'deterministic-grounding-v1'

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/v1/evaluate', response_model=EvaluationResult)
def evaluate(request: EvaluationRequest):
    """Conservative deterministic baseline, NOT an LLM judge."""
    tokens = lambda s: set(re.findall(r'[a-z0-9]+', s.lower()))
    answer_tokens = tokens(request.answer) - {'the','a','an','is','are','of','to','and','in','on','for'}
    context_tokens = tokens(request.context)
    score = len(answer_tokens & context_tokens) / len(answer_tokens) if answer_tokens else 0.0
    verdict = 'review' if score >= 0.6 else 'fail'
    return EvaluationResult(verdict=verdict, score=round(score, 3), evidence=['Lexical overlap only; semantic faithfulness requires an LLM judge and human calibration.'])

from fastapi import HTTPException
from app.judge import judge, JudgeOutput, JudgeUnavailable, RUBRICS

class LLMJudgeRequest(EvaluationRequest):
    rubric: Literal['groundedness', 'relevance', 'safety', 'trajectory'] = 'groundedness'

@app.get('/v1/rubrics')
def list_rubrics():
    return RUBRICS

@app.post('/v1/judge', response_model=JudgeOutput)
def llm_judge(request: LLMJudgeRequest):
    try:
        return judge(request.question, request.answer, request.context, request.rubric)
    except JudgeUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
