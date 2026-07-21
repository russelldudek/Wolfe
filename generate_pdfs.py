"""Generate the campaign PDFs from the authoritative HTML print layouts."""
from pathlib import Path
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
JOBS = {
    'resume.html': 'docs/Russell-Dudek-Wolfe-Resume.pdf',
    'cover-letter.html': 'docs/Russell-Dudek-Wolfe-Cover-Letter.pdf',
    'interview-brief.html': 'docs/Russell-Dudek-Wolfe-Interview-Thesis-Brief.pdf',
    '120-day-plan.html': 'docs/Russell-Dudek-Wolfe-120-Day-Entry-Plan.pdf',
    'data-use-card.html': 'docs/Russell-Dudek-Wolfe-Data-Use-Card-Standard.pdf',
}

for source, target in JOBS.items():
    source_path = ROOT / source
    target_path = ROOT / target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(filename=str(source_path), base_url=str(ROOT)).write_pdf(str(target_path))
    print(f'{source} -> {target}')
