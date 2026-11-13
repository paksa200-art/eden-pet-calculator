# 에덴 페트 계산기 — toinfo.work 전용 화이트 버전

- 기본 데이터: 사용자가 제공한 `toinfo.work/pet` 첫 페이지 HTML에서 추출한 20마리. **전체 목록이 아님**.
- 관리자 `/admin.html` 버튼 → Vercel API → GitHub Actions → `scripts/sync_pets.py` → 목록에 표시된 마지막 페이지까지 전체 조회 → `data/pets.json` **전체 교체** → Vercel 재배포.
- 이전 487마리 데이터, 브라우저 로컬 저장 페트, 수동 추가 페트는 **사용하지 않음**.
- 페이지 수는 목록의 페이지 링크에서 자동 탐지. 수집이 불완전하거나 100마리 미만이면 파일을 덮어쓰지 않음.
- 사이트 제공 초기치는 정수뿐입니다. 계산에 필요한 소수점 S랭크 기준 초기치가 없으므로 환각 계산 버튼은 비활성화됩니다. 수치를 추측하지 않습니다.
- 실제 사이트의 전체 페이지 수집 성공 및 자동 접근 허용 여부는 배포 환경에서 확인 필요.

## 설치
1. ZIP 압축을 풀고 파일/숨김 `.github` 폴더를 GitHub 저장소 루트에 업로드합니다.
2. GitHub Settings → Actions → General → Workflow permissions → Read and write permissions.
3. Vercel에서 GitHub 저장소 Import, Framework Preset Other.
4. Vercel 환경변수 `ADMIN_UPDATE_KEY`, `GITHUB_TOKEN`, `GITHUB_REPOSITORY` 설정 (`GITHUB_BRANCH` 선택). `GITHUB_TOKEN`은 저장소 Actions: Read and write 권한이 필요합니다.
5. `/admin.html`에서 비밀번호 입력 후 업데이트 실행. 버튼은 작업 시작을 요청하며 완료를 기다리지 않습니다. GitHub Actions 실행 결과와 재배포 확인이 필요합니다.

**주의:** 원본 사이트 데이터/이미지 자동 수집 및 재사용 허용 여부를 확인하세요.

## 실제 등록 수 표시
- 첫 페이지 HTML에서 확인된 페트는 **20마리**입니다. 이는 전체 등록 수가 아닙니다.
- 원본 페이지에는 **27페이지**로 이동하는 링크가 있습니다. 각 페이지를 실제로 수집해야 총 등록 수를 확정할 수 있습니다.
- 업데이트 성공 시 `data/pets.json`의 `total`은 수집한 **고유 페트 ID 수**이고, `updatedAt`에 갱신 시각을 기록합니다. 화면은 실제 `pets.length`를 표시합니다.
- 현재 실행 환경에서는 원본 사이트에 직접 연결되지 않아 전체 등록 수를 확인하지 못했습니다.
