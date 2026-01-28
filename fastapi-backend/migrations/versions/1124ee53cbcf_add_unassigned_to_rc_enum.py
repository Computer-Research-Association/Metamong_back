"""add_unassigned_to_rc_enum

Revision ID: 1124ee53cbcf
Revises: ae06d63ee130
Create Date: 2026-01-28 14:49:48.730062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1124ee53cbcf'
down_revision: Union[str, Sequence[str], None] = 'ae06d63ee130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL enum에 값을 추가하려면 타입을 재생성해야 함
    
    # 1. 임시 enum 타입 생성 (UNASSIGNED 포함)
    op.execute("CREATE TYPE rc_new AS ENUM ('UNASSIGNED', 'Torrey', 'JangGiRyeo', 'Kuyper', 'SonYangWon', 'Philadelphos', 'Carmichael')")
    
    # 2. 기존 컬럼을 새 enum 타입으로 변경
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN rc TYPE rc_new 
        USING rc::text::rc_new
    """)
    
    # 3. 기존 enum 타입 삭제
    op.execute("DROP TYPE rc")
    
    # 4. 새 enum 타입 이름을 기존 이름으로 변경
    op.execute("ALTER TYPE rc_new RENAME TO rc")


def downgrade() -> None:
    """Downgrade schema."""
    # UNASSIGNED를 제거하고 원래 enum으로 복원
    
    # 1. UNASSIGNED 값을 가진 유저를 Torrey로 변경
    op.execute("UPDATE users SET rc = 'Torrey' WHERE rc = 'UNASSIGNED'")
    
    # 2. 임시 enum 타입 생성 (UNASSIGNED 제외)
    op.execute("CREATE TYPE rc_old AS ENUM ('Torrey', 'JangGiRyeo', 'Kuyper', 'SonYangWon', 'Philadelphos', 'Carmichael')")
    
    # 3. 기존 컬럼을 원래 enum 타입으로 변경
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN rc TYPE rc_old 
        USING rc::text::rc_old
    """)
    
    # 4. 새 enum 타입 삭제
    op.execute("DROP TYPE rc")
    
    # 5. 원래 enum 타입 이름으로 변경
    op.execute("ALTER TYPE rc_old RENAME TO rc")
