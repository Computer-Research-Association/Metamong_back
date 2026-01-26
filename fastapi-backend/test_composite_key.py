"""
복합 키 (email + auth_provider) 테스트 스크립트

실행 방법:
    # .env의 DATABASE_URL 사용 (로컬 개발 DB)
    uv run python test_composite_key.py

    # 또는 테스트용 DB URL 직접 지정
    TEST_DB_URL=postgresql://user:pass@localhost/dbname uv run python test_composite_key.py

이 스크립트는 다음을 확인합니다:
1. 같은 이메일 + 다른 provider → 별도 유저 생성 가능
2. 같은 이메일 + 같은 provider → 중복 방지 (IntegrityError)

⚠️ 주의사항:
- 기본적으로 .env 파일의 DATABASE_URL을 사용합니다 (로컬 개발 DB)
- 테스트 후 자동으로 테스트 데이터를 삭제합니다
- 로컬 개발 DB가 실행 중이어야 합니다 (docker compose up -d db 등)
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.db.database import Base, SessionLocal
from app.db.models import User
from app.db.enums import AuthProvider, RC, UserStatus


def get_test_db_session():
    """테스트용 DB 세션 생성 (트랜잭션 롤백 사용)"""
    # 환경변수로 테스트 DB URL 지정 가능
    test_db_url = os.getenv("TEST_DB_URL")

    if test_db_url:
        # 환경변수로 지정된 DB 사용
        print(f"ℹ️  환경변수 TEST_DB_URL 사용: {test_db_url}")
        engine = create_engine(test_db_url)
        Base.metadata.create_all(bind=engine)
        TestSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine)
        return TestSessionLocal()
    else:
        # 기본값: .env의 DATABASE_URL 사용 (로컬 개발 DB)
        from app.core.config import settings

        if not settings.DATABASE_URL:
            print("❌ 오류: DATABASE_URL이 설정되지 않았습니다.")
            print("   .env 파일에 DATABASE_URL을 설정하거나,")
            print("   환경변수 TEST_DB_URL을 지정해주세요.")
            print(
                "   예: TEST_DB_URL=postgresql://... uv run python test_composite_key.py")
            sys.exit(1)

        print(f"ℹ️  .env의 DATABASE_URL 사용 (로컬 개발 DB)")
        print(
            f"   DB: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else '로컬 DB'}")
        print("ℹ️  테스트 후 자동으로 테스트 데이터를 삭제합니다.")
        # 파일 상단에서 import한 SessionLocal 사용
        return SessionLocal()


def test_composite_key():
    """복합 키 테스트"""
    db = get_test_db_session()
    test_email = "test_composite@example.com"

    # 기존 테스트 데이터 정리
    try:
        db.query(User).filter(User.email == test_email).delete()
        db.commit()
        print("✓ 기존 테스트 데이터 정리 완료")
    except Exception as e:
        db.rollback()
        print(f"⚠️  기존 데이터 정리 중 오류 (무시): {e}")

    try:
        print("=" * 60)
        print("복합 키 (email + auth_provider) 테스트 시작")
        print("=" * 60)

        # 테스트 1: 같은 이메일 + 다른 provider → 별도 유저 생성 가능
        print("\n[테스트 1] 같은 이메일 + 다른 provider로 유저 생성")
        print("-" * 60)

        # 구글 유저 생성
        google_user = User(
            email=test_email,
            nickname="google_user",
            real_name="Google User",
            auth_provider=AuthProvider.GOOGLE,
            rc=RC.Torrey,
            status=UserStatus.ACTIVE
        )
        db.add(google_user)
        db.commit()
        db.refresh(google_user)
        print(f"✓ 구글 유저 생성 성공 (ID: {google_user.id})")

        # 카카오 유저 생성 (같은 이메일, 다른 provider)
        kakao_user = User(
            email=test_email,
            nickname="kakao_user",
            real_name="Kakao User",
            auth_provider=AuthProvider.KAKAO,
            rc=RC.Torrey,
            status=UserStatus.ACTIVE
        )
        db.add(kakao_user)
        db.commit()
        db.refresh(kakao_user)
        print(f"✓ 카카오 유저 생성 성공 (ID: {kakao_user.id})")

        # 두 유저가 별도로 생성되었는지 확인
        users = db.query(User).filter(User.email == test_email).all()
        assert len(users) == 2, f"예상: 2명, 실제: {len(users)}명"
        assert google_user.id != kakao_user.id, "두 유저의 ID가 같습니다!"
        print(f"✓ 같은 이메일로 2명의 유저가 별도로 생성됨 확인")
        print(
            f"  - 구글 유저 ID: {google_user.id}, Provider: {google_user.auth_provider.value}")
        print(
            f"  - 카카오 유저 ID: {kakao_user.id}, Provider: {kakao_user.auth_provider.value}")

        # 테스트 2: 같은 이메일 + 같은 provider → 중복 방지
        print("\n[테스트 2] 같은 이메일 + 같은 provider로 중복 생성 시도")
        print("-" * 60)

        duplicate_user = User(
            email=test_email,
            nickname="duplicate_user",
            real_name="Duplicate User",
            auth_provider=AuthProvider.GOOGLE,  # 같은 provider
            rc=RC.Torrey,
            status=UserStatus.ACTIVE
        )
        db.add(duplicate_user)

        try:
            db.commit()
            print("✗ 중복 생성이 허용되었습니다! (예상과 다름)")
            db.delete(duplicate_user)
            db.commit()
            return False
        except IntegrityError as e:
            db.rollback()
            print(f"✓ 중복 생성 방지 확인 (IntegrityError 발생)")
            print(f"  에러 메시지: {str(e)[:100]}...")

        # 테스트 3: AuthService의 조회 로직 테스트
        print("\n[테스트 3] 복합 키로 유저 조회")
        print("-" * 60)

        # 구글 유저 조회
        found_google = db.query(User).filter(
            User.email == test_email,
            User.auth_provider == AuthProvider.GOOGLE
        ).first()

        assert found_google is not None, "구글 유저를 찾을 수 없습니다!"
        assert found_google.id == google_user.id, "잘못된 유저가 조회되었습니다!"
        print(f"✓ 구글 유저 조회 성공 (ID: {found_google.id})")

        # 카카오 유저 조회
        found_kakao = db.query(User).filter(
            User.email == test_email,
            User.auth_provider == AuthProvider.KAKAO
        ).first()

        assert found_kakao is not None, "카카오 유저를 찾을 수 없습니다!"
        assert found_kakao.id == kakao_user.id, "잘못된 유저가 조회되었습니다!"
        print(f"✓ 카카오 유저 조회 성공 (ID: {found_kakao.id})")

        # 네이버로 조회 (존재하지 않아야 함)
        found_naver = db.query(User).filter(
            User.email == test_email,
            User.auth_provider == AuthProvider.NAVER
        ).first()

        assert found_naver is None, "네이버 유저가 존재합니다! (예상과 다름)"
        print(f"✓ 네이버 유저 조회 결과: None (정상)")

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 테스트 데이터 정리 (성공/실패 관계없이 항상 실행)
        try:
            db.query(User).filter(User.email == test_email).delete()
            db.commit()
            print("✓ 테스트 데이터 정리 완료")
        except Exception as cleanup_error:
            print(f"⚠️ 테스트 데이터 정리 중 오류: {cleanup_error}")
            db.rollback()
        finally:
            db.close()


if __name__ == "__main__":
    success = test_composite_key()
    sys.exit(0 if success else 1)
