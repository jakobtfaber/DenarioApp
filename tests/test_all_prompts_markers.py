import json
from denario.paper_agents.prompts import (
    abstract_reflection,
    introduction_prompt,
    introduction_reflection,
    methods_prompt,
    results_prompt,
    conclusions_prompt,
    LaTeX_prompt,
    clean_section_prompt,
    summary_prompt,
    references_prompt,
    keyword_prompt,
    fixer_prompt,
)


def contains_markers(text: str, name: str) -> bool:
    return (f"\\begin{{{name}}}" in text) and (f"\\end{{{name}}}" in text)


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
            'Introduction': 'Prev intro',
            'Methods': 'Prev methods',
            'Results': 'Prev results',
        },
        'files': {
            'Folder': 'proj',
            'AAS_keywords': '/data/cmbagents/Denario/denario/paper_agents/LaTeX/AAS_keywords.txt'},
        'latex': {
            'section_to_fix': 'Results'},
    }

    out = {}

    msgs = abstract_reflection(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Abstract'] = contains_markers(t, 'Abstract')

    msgs = introduction_prompt(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Introduction'] = contains_markers(t, 'Introduction')

    msgs = introduction_reflection(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Introduction_reflect'] = contains_markers(t, 'Introduction')

    msgs = methods_prompt(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Methods'] = contains_markers(t, 'Methods')

    msgs = results_prompt(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Results'] = contains_markers(t, 'Results')

    msgs = conclusions_prompt(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Conclusions'] = contains_markers(t, 'Conclusions')

    msgs = LaTeX_prompt('A = B_1 + C% test')
    t = msgs[0].content
    out['Text_from_LaTeX_prompt'] = contains_markers(t, 'Text')

    msgs = clean_section_prompt(state, 'Some text')
    t = msgs[0].content
    out['Text_from_clean'] = ('\\begin{Text}' in t and '\\end{Text}' in t)

    msgs = summary_prompt(state, 'Long text')
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Summary'] = contains_markers(t, 'Summary')

    msgs = references_prompt(state, 'Body with \\ref{fig:A.png}')
    t = msgs[0].content
    out['Text_from_refs'] = contains_markers(t, 'Text')

    msgs, _ = keyword_prompt(state)
    t = msgs[1].content if len(msgs) > 1 else msgs[0].content
    out['Keywords'] = contains_markers(t, 'Keywords')

    msgs = fixer_prompt('Foo', 'Results')
    t = msgs[0].content
    out['Fixer_dynamic'] = ('\\begin{Results}' in t and '\\end{Results}' in t)

    print(json.dumps(out))


if __name__ == '__main__':
    main()
