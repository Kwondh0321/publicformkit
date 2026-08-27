# 변경 기록 / Changelog

이 프로젝트는 [Keep a Changelog](https://keepachangelog.com/)의 구조와 [Semantic Versioning](https://semver.org/) 원칙을 따릅니다.

## [Unreleased]

### 한국어

- 채워진 원본 서식 값을 생성 파일에 복사하지 않고 `source_value_redacted` 상태만 기록해 개인정보 재노출을 막았습니다.
- HWPX에서 읽는 XML의 전체 압축 해제 크기를 20 MiB로 제한합니다.
- 보고서에는 이식 가능한 원본 파일명만 남기고, 생성된 서식에 사람의 검토가 필요하다는 안내를 추가했습니다.
- OCR과 구형 바이너리 HWP가 지원 범위 밖임을 명확히 했습니다.

### English

- Stops copying filled source values into generated files and records only `source_value_redacted`, preventing PII re-exposure.
- Bounds the total expanded HWPX XML payload at 20 MiB.
- Retains only a portable source filename and adds a clear human-review notice to generated forms.
- Makes the lack of OCR and legacy binary HWP support explicit.

### 검증 / Validation

- 4 regression tests, Ruff checks, clean wheel build and install, installed conversion example, unsupported-input failure, and GitHub Actions.

[Unreleased]: https://github.com/Kwondh0321/publicformkit/compare/v0.1.0...HEAD
