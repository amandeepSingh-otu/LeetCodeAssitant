from .models.hint_request import HintRequest

MAX_INPUT_LENGTH = 20_000


def check_request(req: HintRequest):
    # light validation and guardrails
    if not req.problem_title and not req.problem_description:
        raise ValueError('Provide a problem title or description')
    total_len = 0
    for attr in ('problem_title', 'problem_description', 'user_code'):
        v = getattr(req, attr, '') or ''
        total_len += len(v)
    if total_len > MAX_INPUT_LENGTH:
        raise ValueError('Input too large')
    return True
