
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_various_animal_types():
    """Создание животных всех поддерживаемых типов."""
    payloads = [
        {"name": "Leo",    "birth_date": "2020-01-01T00:00:00Z", "gender": "male",   "animal_type": "predator",  "favorite_food": "meat"},
        {"name": "Ellie",  "birth_date": "2019-05-10T00:00:00Z", "gender": "female", "animal_type": "herbivore","favorite_food": "vegetables"},
        {"name": "Tweety", "birth_date": "2022-03-03T00:00:00Z", "gender": "female", "animal_type": "bird",      "favorite_food": "fruits"},
        {"name": "Nemo",   "birth_date": "2022-04-04T00:00:00Z", "gender": "male",   "animal_type": "fish",      "favorite_food": "fish_food"},
    ]
    created_ids = []
    for p in payloads:
        r = client.post("/animals/", json=p)
        assert r.status_code == 201, r.text
        body = r.json()
        # должен вернуться id и все поля совпадать
        assert "id" in body
        for field, val in p.items():
            assert body[field] == val
        assert body["is_healthy"] is True
        created_ids.append(body["id"])

    # Проверим, что они все есть в общем списке
    r = client.get("/animals/")
    assert r.status_code == 200
    all_animals = r.json()
    ids_in_list = {a["id"] for a in all_animals}
    assert set(created_ids).issubset(ids_in_list)


def test_create_enclosure_with_animals():
    """Создание вольера сразу с вложенными животными по ID."""
    # Сначала создадим пару хищников
    p1 = {"name": "Raider", "birth_date": "2021-06-06T00:00:00Z", "gender": "male", "animal_type": "predator", "favorite_food": "meat"}
    p2 = {"name": "Raven",  "birth_date": "2021-07-07T00:00:00Z", "gender": "female", "animal_type": "predator", "favorite_food": "meat"}
    r1 = client.post("/animals/", json=p1)
    r2 = client.post("/animals/", json=p2)
    assert r1.status_code == 201 and r2.status_code == 201
    id1, id2 = r1.json()["id"], r2.json()["id"]

    enc_payload = {
        "type": "predator",
        "size": 50.0,
        "capacity": 5,
        "is_clean": True,
        "animal_ids": [id1, id2]
    }
    r_enc = client.post("/enclosures/", json=enc_payload)
    assert r_enc.status_code == 201, r_enc.text
    enc = r_enc.json()
    # Должно быть присвоено id и список животных точно такой же
    assert "id" in enc
    assert enc["animal_ids"] == [id1, id2]

    # Проверим через GET /enclosures/
    r = client.get("/enclosures/")
    assert r.status_code == 200
    found = [e for e in r.json() if e["id"] == enc["id"]]
    assert len(found) == 1
    assert found[0]["animal_ids"] == [id1, id2]


def test_transfer_animal_between_enclosures():
    """Перемещение животного из одного вольера в другой."""
    # Создадим двух травоядных
    A = {"name": "Bunny", "birth_date": "2022-01-01T00:00:00Z", "gender": "female", "animal_type": "herbivore", "favorite_food": "vegetables"}
    B = {"name": "Cotton", "birth_date": "2022-02-02T00:00:00Z", "gender": "male", "animal_type": "herbivore", "favorite_food": "vegetables"}
    rA = client.post("/animals/", json=A)
    rB = client.post("/animals/", json=B)
    a_id, b_id = rA.json()["id"], rB.json()["id"]

    # Два вольера: первый с A, второй пустой
    enc1 = client.post("/enclosures/", json={
        "type": "herbivore", "size": 30.0, "capacity": 3, "is_clean": True, "animal_ids": [a_id]
    }).json()
    enc2 = client.post("/enclosures/", json={
        "type": "herbivore", "size": 30.0, "capacity": 3, "is_clean": True, "animal_ids": []
    }).json()

    # Переместим A из enc1 в enc2
    r_move = client.post(f"/animals/{a_id}/transfer/{enc2['id']}")
    assert r_move.status_code == 200, r_move.text

    # Проверим списки животных в обоих вольерах
    enclosures = client.get("/enclosures/").json()
    e1 = next(e for e in enclosures if e["id"] == enc1["id"])
    e2 = next(e for e in enclosures if e["id"] == enc2["id"])
    assert a_id not in e1["animal_ids"]
    assert a_id in e2["animal_ids"]
