# PublicFormKit

한국어 | [English](README.en.md) | [변경 기록 / Changelog](CHANGELOG.md)

PublicFormKit은 공공 PDF·HWPX·HTML·Markdown·텍스트 서식을 JSON Schema, 접근 가능한 HTML 양식, 필드별 검토 보고서로 변환합니다. 모델 없이 규칙으로 추론해 결과를 사람이 확인할 수 있게 합니다.

## 설치 및 사용

```bash
git clone https://github.com/Kwondh0321/publicformkit.git
cd publicformkit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install .
publicformkit examples/application.txt --output-dir converted-form
```

생성 파일:

- `form.schema.json`: JSON Schema draft 2020-12
- `form.html`: 레이블과 키보드 접근성을 갖춘 HTML 초안
- `review.json`: 원본 정보, 추론 필드, 신뢰도, 검토 안내

원본 양식에 이미 입력된 값은 개인정보일 수 있으므로 생성 파일에 복사하지 않고, 값의 존재 여부만 `source_value_redacted`로 표시합니다.

텍스트·Markdown·HTML, PDF 텍스트와 AcroForm 필드, HWPX Open Packaging XML을 지원합니다. 구형 바이너리 `.hwp`는 HWPX 변환을 안내하며, 이미지로만 된 PDF는 OCR이 선행돼야 합니다.

필드, 필수 여부, 자료형, 수집 목적, 보존기간과 법적 근거는 공개 전에 반드시 사람이 검토해야 합니다. 이 프로젝트는 제출 서버를 제공하지 않습니다.

## 개발

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## 라이선스

MIT
