# 1. 베이스 이미지 선택 (공식 Python 이미지 사용)
FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. 작업 디렉토리 설정
WORKDIR /code

# 3. 종속성 설치용 파일 복사 (캐시 최적화 위해 requirements 먼저 복사)
COPY requirements.txt .

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 전체 복사
COPY . .

RUN python manage.py collectstatic --noinput

# 6. 환경 변수 설정 (예시)
ENV DJANGO_SETTINGS_MODULE=visa_la_vista.settings

# # 7. 포트 노출 (선택)
# EXPOSE 8000

### above is build setting ###

# 8. 서버 실행 명령 (CMD or ENTRYPOINT 중 택)
CMD ["gunicorn", "visa_la_vista.wsgi:application", "--config", "gunicorn.conf.py"]

