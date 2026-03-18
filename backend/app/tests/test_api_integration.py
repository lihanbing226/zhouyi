"""API 集成测试

端到端测试所有 API 端点，使用内存 SQLite 数据库。
"""

import pytest
from httpx import AsyncClient

from backend.app.models.user import User


# ============================================================
# 认证 API 集成测试
# ============================================================

class TestAuthAPI:
    """认证 API 测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """注册新用户"""
        r = await client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "password": "pass123456",
            "email": "new@example.com",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user: User):
        """注册重复用户名返回 409"""
        r = await client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "password": "pass123456",
        })
        assert r.status_code == 409

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """密码太短返回 422"""
        r = await client.post("/api/v1/auth/register", json={
            "username": "user2",
            "password": "123",
        })
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """登录成功返回 token"""
        r = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """密码错误返回 401"""
        r = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpass",
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """不存在的用户返回 401"""
        r = await client.post("/api/v1/auth/login", json={
            "username": "nobody",
            "password": "pass123456",
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient, auth_headers: dict):
        """获取当前用户信息"""
        r = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_me_no_auth(self, client: AsyncClient):
        """未认证访问 /me 返回 401/403"""
        r = await client.get("/api/v1/auth/me")
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, auth_headers: dict):
        """刷新 token"""
        r = await client.post("/api/v1/auth/refresh", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data


# ============================================================
# 卜卦 API 集成测试
# ============================================================

class TestDivinationAPI:
    """卜卦 API 测试"""

    @pytest.mark.asyncio
    async def test_list_hexagrams(self, client: AsyncClient):
        """查询所有卦象（无需认证）"""
        r = await client.get("/api/v1/divination/hexagrams")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 64
        assert len(data["hexagrams"]) == 64

    @pytest.mark.asyncio
    async def test_list_hexagrams_pagination(self, client: AsyncClient):
        """卦象分页"""
        r = await client.get("/api/v1/divination/hexagrams?page=1&page_size=10")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 64
        assert len(data["hexagrams"]) == 10

    @pytest.mark.asyncio
    async def test_get_hexagram_detail(self, client: AsyncClient):
        """查询单个卦象"""
        r = await client.get("/api/v1/divination/hexagrams/1")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "乾"
        assert len(data["yao_texts"]) == 6

    @pytest.mark.asyncio
    async def test_get_hexagram_invalid(self, client: AsyncClient):
        """无效卦号返回 400"""
        r = await client.get("/api/v1/divination/hexagrams/0")
        assert r.status_code == 400
        r = await client.get("/api/v1/divination/hexagrams/65")
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_cast_divination(self, client: AsyncClient, auth_headers: dict):
        """执行卜卦"""
        r = await client.post("/api/v1/divination/cast", json={
            "question": "今天运势如何？",
            "method": "coins",
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert 1 <= data["hexagram_num"] <= 64
        assert len(data["yao_sequence"]) == 6
        assert 1 <= data["luck_score"] <= 100
        assert len(data["interpretation"]) > 0

    @pytest.mark.asyncio
    async def test_cast_divination_with_client_yao_sequence(
        self, client: AsyncClient, auth_headers: dict
    ):
        """前端上传爻序列时，后端应按该序列解卦。"""
        r = await client.post("/api/v1/divination/cast", json={
            "question": "我上传一个固定卦象",
            "method": "coins",
            "yao_sequence": "777777",
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["yao_sequence"] == "777777"
        assert data["hexagram_num"] == 1
        assert data["hexagram_name"] == "乾"

    @pytest.mark.asyncio
    async def test_cast_divination_invalid_yao_sequence(
        self, client: AsyncClient, auth_headers: dict
    ):
        """无效爻序列返回 422。"""
        r = await client.post("/api/v1/divination/cast", json={
            "question": "测试",
            "method": "coins",
            "yao_sequence": "123456",
        }, headers=auth_headers)
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_cast_divination_no_auth(self, client: AsyncClient):
        """未认证卜卦返回 403"""
        r = await client.post("/api/v1/divination/cast", json={
            "question": "测试",
        })
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_cast_divination_invalid_method(self, client: AsyncClient, auth_headers: dict):
        """无效卜卦方法返回 400"""
        r = await client.post("/api/v1/divination/cast", json={
            "question": "测试",
            "method": "invalid",
        }, headers=auth_headers)
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_divination_history(self, client: AsyncClient, auth_headers: dict):
        """卜卦历史记录"""
        # 先卜卦
        await client.post("/api/v1/divination/cast", json={
            "question": "测试问题",
        }, headers=auth_headers)

        # 查看历史
        r = await client.get("/api/v1/divination/history", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert data[0]["question"] == "测试问题"

    @pytest.mark.asyncio
    async def test_divination_history_no_auth(self, client: AsyncClient):
        """未认证查看历史返回 403"""
        r = await client.get("/api/v1/divination/history")
        assert r.status_code in (401, 403)


# ============================================================
# 八字 API 集成测试
# ============================================================

class TestBaziAPI:
    """八字 API 测试"""

    @pytest.mark.asyncio
    async def test_calculate_bazi(self, client: AsyncClient, auth_headers: dict):
        """计算八字命盘"""
        r = await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "2000-06-15T14:00:00",
            "gender": "M",
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert data["day_master"] in list("甲乙丙丁戊己庚辛壬癸")
        assert data["strength"] in ("身强", "身弱")
        assert len(data["analysis"]) > 0

    @pytest.mark.asyncio
    async def test_calculate_bazi_no_auth(self, client: AsyncClient):
        """未认证计算八字返回 403"""
        r = await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "2000-06-15T14:00:00",
        })
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_get_bazi_record(self, client: AsyncClient, auth_headers: dict):
        """查询八字记录"""
        # 先计算
        r = await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "1990-03-15T08:00:00",
        }, headers=auth_headers)
        record_id = r.json()["id"]

        # 查询
        r = await client.get(f"/api/v1/bazi/records/{record_id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["id"] == record_id

    @pytest.mark.asyncio
    async def test_get_bazi_record_not_found(self, client: AsyncClient, auth_headers: dict):
        """查询不存在的记录返回 404"""
        r = await client.get("/api/v1/bazi/records/nonexistent-id", headers=auth_headers)
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_bazi_history(self, client: AsyncClient, auth_headers: dict):
        """八字历史记录"""
        # 先计算
        await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "1985-12-25T10:00:00",
        }, headers=auth_headers)

        # 查看历史
        r = await client.get("/api/v1/bazi/history", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1


# ============================================================
# 历史记录 API 集成测试
# ============================================================

class TestHistoryAPI:
    """统一历史记录 API 测试"""

    @pytest.mark.asyncio
    async def test_list_history_all(self, client: AsyncClient, auth_headers: dict):
        """统一历史记录列表返回卜卦和八字数据。"""
        await client.post("/api/v1/divination/cast", json={
            "question": "统一历史测试",
            "method": "coins",
            "yao_sequence": "777777",
        }, headers=auth_headers)
        await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "2000-06-15T14:00:00",
            "gender": "M",
        }, headers=auth_headers)

        r = await client.get("/api/v1/history?page=1&page_size=10&type=all&sort=newest", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 2
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] >= 1
        item_types = {item["type"] for item in data["items"]}
        assert "divination" in item_types
        assert "bazi" in item_types

    @pytest.mark.asyncio
    async def test_list_history_filter_divination(self, client: AsyncClient, auth_headers: dict):
        """按类型筛选历史记录。"""
        await client.post("/api/v1/divination/cast", json={
            "question": "只看卜卦",
            "method": "coins",
            "yao_sequence": "777777",
        }, headers=auth_headers)

        r = await client.get("/api/v1/history?type=divination", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert all(item["type"] == "divination" for item in data["items"])

    @pytest.mark.asyncio
    async def test_list_history_invalid_type(self, client: AsyncClient, auth_headers: dict):
        """非法历史类型返回 400。"""
        r = await client.get("/api/v1/history?type=invalid", headers=auth_headers)
        assert r.status_code == 400


# ============================================================
# 看板 API 集成测试
# ============================================================

class TestDashboardAPI:
    """看板 API 测试"""

    @pytest.mark.asyncio
    async def test_overview_empty(self, client: AsyncClient):
        """空数据库的概览"""
        r = await client.get("/api/v1/dashboard/overview")
        assert r.status_code == 200
        data = r.json()
        assert data["today_count"] == 0
        assert data["active_users"] == 0
        assert data["total_count"] == 0

    @pytest.mark.asyncio
    async def test_overview_with_data(self, client: AsyncClient, auth_headers: dict):
        """有数据时的概览"""
        # 卜卦一次
        await client.post("/api/v1/divination/cast", json={
            "question": "测试",
        }, headers=auth_headers)

        r = await client.get("/api/v1/dashboard/overview")
        assert r.status_code == 200
        data = r.json()
        assert data["total_count"] >= 1

    @pytest.mark.asyncio
    async def test_hexagram_stats(self, client: AsyncClient):
        """卦象频率统计"""
        r = await client.get("/api/v1/dashboard/hexagram-stats")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_user_trend(self, client: AsyncClient):
        """用户活跃趋势"""
        r = await client.get("/api/v1/dashboard/user-trend?days=7")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 7
        for item in data:
            assert "date" in item
            assert "count" in item

    @pytest.mark.asyncio
    async def test_user_trend_with_data(self, client: AsyncClient, auth_headers: dict):
        """有卜卦数据时趋势接口仍应正常返回。"""
        await client.post("/api/v1/divination/cast", json={
            "question": "趋势测试",
            "method": "coins",
            "yao_sequence": "777777",
        }, headers=auth_headers)

        r = await client.get("/api/v1/dashboard/user-trend?days=3")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 3
        assert any(item["count"] >= 1 for item in data)

    @pytest.mark.asyncio
    async def test_luck_distribution(self, client: AsyncClient):
        """运势评分分布"""
        r = await client.get("/api/v1/dashboard/luck-distribution")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 5


# ============================================================
# 历史记录删除 API 集成测试
# ============================================================

class TestHistoryAPI:
    """历史记录管理测试"""

    @pytest.mark.asyncio
    async def test_delete_divination_record(self, client: AsyncClient, auth_headers: dict):
        """删除卜卦记录"""
        # 创建记录
        r = await client.post("/api/v1/divination/cast", json={
            "question": "删除测试",
        }, headers=auth_headers)
        record_id = r.json()["id"]

        # 删除
        r = await client.delete(
            f"/api/v1/history/divination/{record_id}",
            headers=auth_headers,
        )
        assert r.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_bazi_record(self, client: AsyncClient, auth_headers: dict):
        """删除八字记录"""
        # 创建记录
        r = await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "2000-01-01T00:00:00",
        }, headers=auth_headers)
        record_id = r.json()["id"]

        # 删除
        r = await client.delete(
            f"/api/v1/history/bazi/{record_id}",
            headers=auth_headers,
        )
        assert r.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_record(self, client: AsyncClient, auth_headers: dict):
        """删除不存在的记录返回 404"""
        r = await client.delete(
            "/api/v1/history/divination/nonexistent-id",
            headers=auth_headers,
        )
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_invalid_type(self, client: AsyncClient, auth_headers: dict):
        """无效记录类型返回 400"""
        r = await client.delete(
            "/api/v1/history/invalid/some-id",
            headers=auth_headers,
        )
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_no_auth(self, client: AsyncClient):
        """未认证删除返回 403"""
        r = await client.delete("/api/v1/history/divination/some-id")
        assert r.status_code in (401, 403)


# ============================================================
# 端到端流程测试
# ============================================================

class TestEndToEnd:
    """端到端流程测试"""

    @pytest.mark.asyncio
    async def test_full_divination_flow(self, client: AsyncClient):
        """完整卜卦流程：注册 -> 登录 -> 卜卦 -> 查看历史 -> 删除"""
        # 1. 注册
        r = await client.post("/api/v1/auth/register", json={
            "username": "e2e_user",
            "password": "e2epass123",
        })
        assert r.status_code == 201

        # 2. 登录
        r = await client.post("/api/v1/auth/login", json={
            "username": "e2e_user",
            "password": "e2epass123",
        })
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. 卜卦
        r = await client.post("/api/v1/divination/cast", json={
            "question": "端到端测试",
        }, headers=headers)
        assert r.status_code == 200
        record_id = r.json()["id"]
        assert 1 <= r.json()["hexagram_num"] <= 64

        # 4. 查看历史
        r = await client.get("/api/v1/divination/history", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) == 1

        # 5. 删除记录
        r = await client.delete(
            f"/api/v1/history/divination/{record_id}",
            headers=headers,
        )
        assert r.status_code == 204

        # 6. 确认已删除
        r = await client.get("/api/v1/divination/history", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) == 0

    @pytest.mark.asyncio
    async def test_full_bazi_flow(self, client: AsyncClient):
        """完整八字流程：注册 -> 登录 -> 计算 -> 查询 -> 删除"""
        # 1. 注册 + 登录
        await client.post("/api/v1/auth/register", json={
            "username": "bazi_user",
            "password": "bazipass123",
        })
        r = await client.post("/api/v1/auth/login", json={
            "username": "bazi_user",
            "password": "bazipass123",
        })
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 计算八字
        r = await client.post("/api/v1/bazi/calculate", json={
            "birth_datetime": "1995-08-20T15:30:00",
            "gender": "F",
        }, headers=headers)
        assert r.status_code == 200
        data = r.json()
        record_id = data["id"]
        assert data["strength"] in ("身强", "身弱")

        # 3. 查询记录
        r = await client.get(f"/api/v1/bazi/records/{record_id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["id"] == record_id

        # 4. 查看历史
        r = await client.get("/api/v1/bazi/history", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) == 1

        # 5. 删除
        r = await client.delete(
            f"/api/v1/history/bazi/{record_id}",
            headers=headers,
        )
        assert r.status_code == 204
