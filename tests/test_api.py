async def test_create_post(client, create_user):
    post = {"text": "test"}
    resp = await client.post("api/v1/post", json=post)
    assert resp.status_code == 200


async def test_register(client):
    # XXX хоть в клиенте и передается валидный токен, ручка регистрации на него не смотрит
    # так что все ок
    data = {
        "name":"test",
        "login":"test1",
        "password":"123aaa"
    }
    # 1 проверяем, что дает зарегаться
    resp = await client.post("api/v1/register", json=data)
    assert resp.status_code == 200

    # 2 проверяем, что после регистрации можно получить токен
    resp = await client.post("api/v1/token", json=data)
    assert resp.status_code == 200


async def test_tree_of_comments(client):
    params = {
        "parent_id": 1,
    }
    post = {"text": "test"}
    resp = await client.post("api/v1/post", json=post)
    post_id = 1
    resp = await client.post(f"api/v1/comment", json={"text": "some", "post_id": 1})
    resp = await client.post(f"api/v1/comment", json={"text": "some", "post_id": 1})
    print()
    for i in range(5):
        resp = await client.post(f"api/v1/comment", json={"text": "some", "post_id": 1}, params={"parent_id": 1})
    for i in range(5):
        resp = await client.post(
            f"api/v1/comment/{post_id}", json={"text": "some", "post_id": 1}, params={"parent_id": 2}
        )
    print()
    resp = await client.get(f"api/v1/comment/{1}", params=params)
    print()