"""
API 集成测试
覆盖核心业务流程：注册 → 登录 → 创建档案 → 筛查 → 报告 → 训练
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


@pytest.fixture(scope="module")
def auth_headers(client):
    """注册并登录，返回 Authorization 头（纯用户名注册，不需要验证码）"""
    client.post("/api/auth/register", json={
        "username": "test_parent",
        "password": "Test1234",
    })
    res = client.post("/api/auth/login", json={
        "username": "test_parent",
        "password": "Test1234",
    })
    assert res.status_code == 200, f"登录失败: {res.json()}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def child_id(client, auth_headers):
    """创建儿童档案，返回 child_id"""
    res = client.post("/api/children/", json={
        "name": "小明",
        "gender": "male",
        "birth_date": "2017-06-01",
        "grade": "一年级",
    }, headers=auth_headers)
    assert res.status_code == 200, f"创建档案失败: {res.json()}"
    return res.json()["id"]


# ── 认证模块 ──────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_duplicate(self, client, auth_headers):
        res = client.post("/api/auth/register", json={
            "username": "test_parent",
            "password": "Test1234",
        })
        assert res.status_code == 400

    def test_login_wrong_password(self, client):
        res = client.post("/api/auth/login", json={
            "username": "test_parent",
            "password": "wrong",
        })
        assert res.status_code == 401
    def test_get_me(self, client, auth_headers):
        res = client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["username"] == "test_parent"

    def test_unauthorized(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code in (401, 403)  # FastAPI OAuth2 返回 403，兼容两种


# ── 儿童档案模块 ──────────────────────────────────────────────────────────────

class TestChildren:
    def test_list_children(self, client, auth_headers, child_id):
        res = client.get("/api/children/", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

    def test_get_child(self, client, auth_headers, child_id):
        res = client.get(f"/api/children/{child_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "小明"

    def test_update_child(self, client, auth_headers, child_id):
        res = client.put(f"/api/children/{child_id}", json={"grade": "二年级"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["grade"] == "二年级"


# ── 筛查模块 ──────────────────────────────────────────────────────────────────

class TestScreenings:
    def test_get_questions(self, client, auth_headers):
        for game_type in ["visual", "spelling", "comprehension", "working_memory", "rapid_naming", "motor_coordination"]:
            res = client.get(f"/api/screenings/questions/{game_type}?difficulty=L1", headers=auth_headers)
            assert res.status_code == 200, f"{game_type} 题目获取失败"
            data = res.json()
            assert "questions" in data
            assert len(data["questions"]) > 0

    def test_get_questions_with_grade(self, client, auth_headers):
        res = client.get("/api/screenings/questions/visual?grade=一年级", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["difficulty"] == "L1"

    def test_full_screening_flow(self, client, auth_headers, child_id):
        """完整筛查流程：开始 → 提交 → 生成报告"""
        # 开始筛查
        start_res = client.post("/api/screenings/start", json={
            "child_id": child_id,
            "game_type": "visual",
        }, headers=auth_headers)
        assert start_res.status_code == 200
        screening_id = start_res.json()["id"]

        # 获取题目
        q_res = client.get("/api/screenings/questions/visual?difficulty=L1", headers=auth_headers)
        questions = q_res.json()["questions"]

        # 构造答案（全部选第0个选项）
        answers = [
            {
                "question_id": q["id"],
                "answer": 0,
                "time_spent": 4,
                "reaction_time": 1200,
                "change_count": 0,
                "is_timeout": False,
            }
            for q in questions[:5]
        ]

        # 提交答案
        submit_res = client.post("/api/screenings/submit", json={
            "screening_id": screening_id,
            "answers": answers,
            "behavior_data": {},
        }, headers=auth_headers)
        assert submit_res.status_code == 200
        data = submit_res.json()
        assert "report_id" in data
        assert "risk_level" in data
        assert data["risk_level"] in ("low", "medium", "high")
        return data["report_id"]

    def test_screening_history(self, client, auth_headers, child_id):
        res = client.get(f"/api/screenings/history?child_id={child_id}", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)


# ── 报告模块 ──────────────────────────────────────────────────────────────────

class TestReports:
    def test_list_reports(self, client, auth_headers, child_id):
        res = client.get(f"/api/reports/?child_id={child_id}", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_report_dimensions(self, client, auth_headers, child_id):
        reports = client.get(f"/api/reports/?child_id={child_id}", headers=auth_headers).json()
        if not reports:
            pytest.skip("无报告数据")
        report_id = reports[0]["id"]
        res = client.get(f"/api/reports/{report_id}/dimensions", headers=auth_headers)
        assert res.status_code == 200
        assert "dimensions" in res.json()

    def test_export_report_text(self, client, auth_headers, child_id):
        reports = client.get(f"/api/reports/?child_id={child_id}", headers=auth_headers).json()
        if not reports:
            pytest.skip("无报告数据")
        report_id = reports[0]["id"]
        res = client.get(f"/api/reports/{report_id}/export-text", headers=auth_headers)
        assert res.status_code == 200
        content = res.json()["content"]
        assert "悦读小灯塔" in content
        assert "综合得分" in content


# ── 训练模块 ──────────────────────────────────────────────────────────────────

class TestTraining:
    def test_create_and_complete_task(self, client, auth_headers, child_id):
        from datetime import date
        today = date.today().isoformat()
        # 创建任务
        create_res = client.post("/api/training/tasks", json={
            "child_id": child_id,
            "task_type": "visual",
            "task_name": "测试视觉训练",
            "scheduled_date": today,
        }, headers=auth_headers)
        assert create_res.status_code == 200
        task_id = create_res.json()["id"]

        # 完成任务
        complete_res = client.post(f"/api/training/tasks/{task_id}/complete", json={
            "correct_count": 8,
            "total_count": 10,
            "accuracy": 80,
        }, headers=auth_headers)
        assert complete_res.status_code == 200
        assert complete_res.json()["status"] == "completed"

    def test_get_stars(self, client, auth_headers, child_id):
        res = client.get(f"/api/training/stars?child_id={child_id}", headers=auth_headers)
        assert res.status_code == 200
        assert "total_stars" in res.json()

    def test_growth_records(self, client, auth_headers, child_id):
        # 创建备注
        create_res = client.post("/api/training/growth", json={
            "child_id": child_id,
            "record_type": "note",
            "title": "家长备注",
            "content": "今天表现很好",
        }, headers=auth_headers)
        assert create_res.status_code == 200

        # 查询
        list_res = client.get(f"/api/training/growth?child_id={child_id}", headers=auth_headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1


# ── 通知模块 ──────────────────────────────────────────────────────────────────

class TestNotifications:
    def test_get_notifications(self, client, auth_headers):
        res = client.get("/api/notifications", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_unread_count(self, client, auth_headers):
        res = client.get("/api/notifications/unread-count", headers=auth_headers)
        assert res.status_code == 200
        assert "unread_count" in res.json()

    def test_mark_all_read(self, client, auth_headers):
        res = client.put("/api/notifications/read-all", headers=auth_headers)
        assert res.status_code == 200


# ── 健康检查 ──────────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
