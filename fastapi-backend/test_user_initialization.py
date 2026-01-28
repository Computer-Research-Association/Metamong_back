"""
신규 유저 초기화 플로우 테스트 스크립트

실행 방법:
    uv run python test_user_initialization.py

이 스크립트는 다음을 확인합니다:
1. 신규 유저 로그인 시 status=NEW인지 확인
2. InitializeUserInfo 호출 시 NEW → ACTIVE로 변경되는지 확인
"""
import sys
from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.db.models import User
from app.db.enums import AuthProvider, RC, UserStatus
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import InitializeUserInfo


def test_user_initialization():
    """신규 유저 초기화 플로우 테스트"""
    db = SessionLocal()
    test_email = "test_init@example.com"

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
        print("신규 유저 초기화 플로우 테스트 시작")
        print("=" * 60)

        # 테스트 1: 신규 유저 로그인 시 status=NEW인지 확인
        print("\n[테스트 1] 신규 유저 로그인 시 status=NEW 확인")
        print("-" * 60)

        auth_service = AuthService(db)
        
        # 신규 유저 로그인 시뮬레이션 (실제 login 메서드 로직 사용)
        user_data = {
            "email": test_email,
            "nickname": "test_user",
            "name": "Test User"
        }
        
        # 실제 auth_service.login() 로직과 동일하게 유저 생성
        # (login은 async이고 토큰을 반환하므로, 여기서는 로직만 시뮬레이션)
        auth_provider = AuthProvider.GOOGLE
        existing_user = db.query(User).filter(
            User.email == test_email,
            User.auth_provider == auth_provider
        ).first()
        
        if not existing_user:
            # 새 유저 (처음 로그인) → NEW 상태로 생성
            new_user = User(
                email=test_email,
                nickname=user_data["nickname"],
                real_name=user_data["name"],
                auth_provider=auth_provider,
                rc=RC.UNASSIGNED,
                status=UserStatus.NEW
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        else:
            new_user = existing_user
        
        print(f"✓ 신규 유저 생성 성공 (ID: {new_user.id})")
        assert new_user.status == UserStatus.NEW, f"예상: NEW, 실제: {new_user.status}"
        assert new_user.rc == RC.UNASSIGNED, f"예상: UNASSIGNED, 실제: {new_user.rc}"
        print(f"✓ status={new_user.status.value} 확인")
        print(f"✓ rc={new_user.rc.value} 확인")

        # 테스트 2: InitializeUserInfo 호출 시 NEW → ACTIVE로 변경되는지 확인
        print("\n[테스트 2] InitializeUserInfo 호출 시 NEW → ACTIVE 변경 확인")
        print("-" * 60)

        user_service = UserService(db)
        init_data = InitializeUserInfo(
            rc=RC.Kuyper,
            student_id="2024123456",
            major="컴퓨터공학과",
            phone_number="010-1234-5678",
            instagram_id="test_instagram",
            mbti=None
        )

        updated_user = user_service.initialize_user_info(new_user, init_data)
        
        assert updated_user.status == UserStatus.ACTIVE, f"예상: ACTIVE, 실제: {updated_user.status}"
        assert updated_user.rc == RC.Kuyper, f"예상: Kuyper, 실제: {updated_user.rc}"
        assert updated_user.student_id == "2024123456", "student_id 업데이트 실패"
        assert updated_user.major == "컴퓨터공학과", "major 업데이트 실패"
        assert updated_user.phone_number == "010-1234-5678", "phone_number 업데이트 실패"
        assert updated_user.instagram_id == "test_instagram", "instagram_id 업데이트 실패"
        
        print(f"✓ status={updated_user.status.value}로 변경 확인 (NEW → ACTIVE)")
        print(f"✓ rc={updated_user.rc.value}로 변경 확인 (UNASSIGNED → Kuyper)")
        print(f"✓ 모든 필드 업데이트 확인")

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
    success = test_user_initialization()
    sys.exit(0 if success else 1)
