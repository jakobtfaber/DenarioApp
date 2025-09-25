import json
from denario.paper_agents.prompts import abstract_prompt, abstract_reflection
from denario.paper_agents.tools import extract_latex_block


def main() -> None:
    state = {
        'writer': 'scientific writer',
        'idea': {
            'Idea': 'Test idea',
            'Methods': 'Test methods',
            'Results': 'Test results',
        },
        'paper': {
            'Abstract': 'Previous abstract',
            'Title': 'Prev Title',
            'Introduction': '',
        },
    }

    # 1) Render prompts without exceptions
    msgs = abstract_prompt(state, attempt=1)
    msgs2 = abstract_reflection(state)
    assert isinstance(msgs, list) and len(msgs) >= 1
    assert isinstance(msgs2, list) and len(msgs2) >= 1

    # 2) Ensure Abstract block markers appear literally in the reflection
    # prompt
    text2 = msgs2[1].content if len(msgs2) > 1 else msgs2[0].content
    assert "\\begin{Abstract}" in text2 and "\\end{Abstract}" in text2, "Abstract markers missing"

    # 3) Test LaTeX extraction on a minimal Abstract sample
    sample = "\\begin{Abstract}\nHello world\n\\end{Abstract}"
    ex = extract_latex_block(
        {'files': {'Error': '/tmp/error.txt'}}, sample, 'Abstract')
    assert ex == 'Hello world'

    print(json.dumps({
        'prompts_ok': True,
        'markers_ok': True,
        'extract_ok': True,
    }))


if __name__ == '__main__':
    main()
