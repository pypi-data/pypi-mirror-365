from fastmcp import FastMCP
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
import os

# 載入 .env 檔案
# load_dotenv()

# 初始化 SQLAlchemy
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

# 從 .env 載入 MYSQL_URL
# DB_URL = os.getenv("MYSQL_URL")
# if not DB_URL:
#     raise ValueError("請確認 .env 檔中有設定 MYSQL_URL")
DB_URL = "mysql+pymysql://root:11111111@127.0.0.1:3306/testdb"
engine = create_engine(DB_URL, echo=True, future=True)
Session = sessionmaker(bind=engine)
session = Session()

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users"))  # ⚠️ 要用 text() 包起來
        for row in result:
            print(row)
        print("✅ 連線成功")
except Exception as e:
    print("❌ 錯誤：", e)

# 建立表格（如果還沒建立）
Base.metadata.create_all(engine)

def main():
    mcp = FastMCP("unieai-mcp-mysql-server")

    @mcp.tool()
    def add_user(name: str, email: str) -> str:
        """新增使用者"""
        new_user = User(name=name, email=email)
        session.add(new_user)
        session.commit()
        return f"使用者 {name} 已成功新增，ID：{new_user.id}"

    @mcp.tool()
    def update_user(user_id: int, name: str = None, email: str = None) -> str:
        """更新使用者資訊"""
        user = session.query(User).get(user_id)
        if not user:
            return "查無此使用者"
        if name:
            user.name = name
        if email:
            user.email = email
        session.commit()
        return f"使用者 ID {user_id} 已更新"

    @mcp.tool()
    def delete_user(user_id: int) -> str:
        """刪除使用者"""
        user = session.query(User).get(user_id)
        if not user:
            return "查無此使用者"
        session.delete(user)
        session.commit()
        return f"使用者 ID {user_id} 已刪除"

    @mcp.tool()
    def get_user(user_id: int) -> dict:
        """查詢使用者"""
        user = session.query(User).get(user_id)
        if not user:
            return {"error": "查無此使用者"}
        return {"id": user.id, "name": user.name, "email": user.email}

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
