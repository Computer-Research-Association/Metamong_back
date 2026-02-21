from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    nickname: str

class SymmetricKeyResponse(BaseModel): # 이 class대로 json을 만들고 리턴함
    key: str # 대칭키
    algorithm: str = "HS256" #  jwt 서명 알고리즘