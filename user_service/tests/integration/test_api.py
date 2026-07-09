from httpx import AsyncClient


class TestHealthEndpoint:
    async def test_health(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "user-service"


class TestCreateUser:
    async def test_create_user_success(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/users",
            json={"username": "alice", "email": "alice@example.com"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["status"] == "active"
        assert "id" in data

    async def test_create_user_duplicate_username(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/users",
            json={"username": "bob", "email": "bob1@example.com"},
        )
        resp = await client.post(
            "/api/v1/users",
            json={"username": "bob", "email": "bob2@example.com"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["error"] == "USER_ALREADY_EXISTS"

    async def test_create_user_duplicate_email(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/users",
            json={"username": "charlie", "email": "charlie@example.com"},
        )
        resp = await client.post(
            "/api/v1/users",
            json={"username": "charlie2", "email": "charlie@example.com"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["error"] == "USER_ALREADY_EXISTS"

    async def test_create_user_validation_error(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/users",
            json={"username": "x", "email": "bad"},
        )
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "VALIDATION_ERROR"
        assert "status_code" in data
        assert "detail" in data


class TestGetUser:
    async def test_get_user_by_id(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/users",
            json={"username": "dave", "email": "dave@example.com"},
        )
        user_id = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/users/{user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user_id
        assert data["username"] == "dave"

    async def test_get_user_not_found(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        data = resp.json()
        assert data["error"] == "USER_NOT_FOUND"

    async def test_get_user_invalid_uuid(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/users/not-a-uuid")
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "VALIDATION_ERROR"


class TestListUsers:
    async def test_list_users_empty(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/users?skip=0&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["users"], list)
        assert "total" in data

    async def test_list_users_pagination(self, client: AsyncClient) -> None:
        for i in range(3):
            await client.post(
                "/api/v1/users",
                json={
                    "username": f"user{i}", "email": f"user{i}@example.com",

                },
            )
        resp = await client.get("/api/v1/users?skip=1&limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["users"]) == 2
        assert data["skip"] == 1
        assert data["limit"] == 2


class TestUpdateUser:
    async def test_update_user_success(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/users",
            json={"username": "eve", "email": "eve@example.com"},
        )
        user_id = create_resp.json()["id"]

        resp = await client.put(
            f"/api/v1/users/{user_id}",
            json={"username": "eve_updated", "status": "inactive"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "eve_updated"
        assert data["status"] == "inactive"

    async def test_update_user_not_found(self, client: AsyncClient) -> None:
        resp = await client.put(
            "/api/v1/users/00000000-0000-0000-0000-000000000000",
            json={"username": "ghost"},
        )
        assert resp.status_code == 404
        data = resp.json()
        assert data["error"] == "USER_NOT_FOUND"


class TestDeleteUser:
    async def test_delete_user_success(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/users",
            json={"username": "frank", "email": "frank@example.com"},
        )
        user_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/users/{user_id}")
        assert resp.status_code == 204

        get_resp = await client.get(f"/api/v1/users/{user_id}")
        assert get_resp.status_code == 404

    async def test_delete_user_not_found(self, client: AsyncClient) -> None:
        resp = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        data = resp.json()
        assert data["error"] == "USER_NOT_FOUND"


class TestFullCRUD:
    async def test_full_crud_chain(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/users",
            json={"username": "grace", "email": "grace@example.com"},
        )
        assert create_resp.status_code == 201
        user_id = create_resp.json()["id"]

        get_resp = await client.get(f"/api/v1/users/{user_id}")
        assert get_resp.status_code == 200

        put_resp = await client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "grace_new@example.com", "status": "banned"},
        )
        assert put_resp.status_code == 200
        assert put_resp.json()["email"] == "grace_new@example.com"

        del_resp = await client.delete(f"/api/v1/users/{user_id}")
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/api/v1/users/{user_id}")
        assert get_resp.status_code == 404
