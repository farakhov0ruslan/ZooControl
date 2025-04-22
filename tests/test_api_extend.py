import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app

client = TestClient(app)


def test_invalid_birth_date_future():
    """POST /animals/ с датой рождения в будущем → 422"""
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    payload = {
        "name": "Future",
        "birth_date": future_date,
        "gender": "male",
        "animal_type": "predator",
        "favorite_food": "meat"
    }
    r = client.post("/animals/", json=payload)
    assert r.status_code == 422


def test_invalid_animal_type_and_food():
    """POST /animals/ с некорректным animal_type или favorite_food → 422"""
    base = {
        "name": "X",
        "birth_date": "2020-01-01T00:00:00Z",
        "gender": "male",
    }
    # Неверный animal_type
    r1 = client.post("/animals/", json={**base, "animal_type": "unknown", "favorite_food": "meat"})
    assert r1.status_code == 422
    # Неверный favorite_food
    r2 = client.post("/animals/", json={**base, "animal_type": "predator", "favorite_food": "grass"})
    assert r2.status_code == 422


def test_enclosure_capacity_limit_and_type_mismatch():
    """Граничные условия: capacity=1 и type mismatch."""
    # создаём одного травоядного
    herb = {"name": "Herb", "birth_date": "2021-01-01T00:00:00Z", "gender": "female",
            "animal_type": "herbivore", "favorite_food": "vegetables"}
    rh = client.post("/animals/", json=herb).json()["id"]
    # создаём одного хищника
    pred = {"name": "Pred", "birth_date": "2021-02-02T00:00:00Z", "gender": "male",
            "animal_type": "predator", "favorite_food": "meat"}
    rp = client.post("/animals/", json=pred).json()["id"]

    # capacity=1, сначала добавляем одного — должно быть ОК
    e1 = client.post("/enclosures/", json={
        "type": "herbivore", "size": 10.0, "capacity": 1, "is_clean": True, "animal_ids": [rh]
    })
    assert e1.status_code == 201
    eid = e1.json()["id"]

    # пытаемся создать вольер сразу с двумя — capacity overflow
    e2 = client.post("/enclosures/", json={
        "type": "herbivore", "size": 10.0, "capacity": 1, "is_clean": True, "animal_ids": [rh, rh]
    })
    assert e2.status_code == 400

    # пытаемся вложить неправильный тип животного
    e3 = client.post("/enclosures/", json={
        "type": "herbivore", "size": 10.0, "capacity": 2, "is_clean": True, "animal_ids": [rp]
    })
    assert e3.status_code == 400


def test_delete_animal_and_enclosure():
    """DELETE /animals/{id} и DELETE /enclosures/{id} edge cases."""
    # создаём животное и удаляем его
    a = client.post("/animals/", json={
        "name": "Del", "birth_date": "2020-05-05T00:00:00Z", "gender": "male",
        "animal_type": "predator", "favorite_food": "meat"
    }).json()
    aid = a["id"]
    r1 = client.delete(f"/animals/{aid}")
    assert r1.status_code == 204
    # повторное удаление → 404
    r2 = client.delete(f"/animals/{aid}")
    assert r2.status_code == 404

    # создаём вольер и удаляем его
    e = client.post("/enclosures/", json={
        "type": "predator", "size": 20.0, "capacity": 2, "is_clean": True, "animal_ids": []
    }).json()
    eid = e["id"]
    r3 = client.delete(f"/enclosures/{eid}")
    assert r3.status_code == 204
    # после удаления GET → список больше не содержит этого id
    all_enc = client.get("/enclosures/").json()
    assert eid not in [enc["id"] for enc in all_enc]


def test_create_and_complete_feeding_schedule():
    """POST /feedings/, PUT change, POST complete, GET checks, 404 on missing."""
    # создаём животное
    a = client.post("/animals/", json={
        "name": "Feed", "birth_date": "2021-03-03T00:00:00Z", "gender": "female",
        "animal_type": "predator", "favorite_food": "meat"
    }).json()
    aid = a["id"]

    # корректное создание расписания
    sched = client.post("/feedings/", json={
        "animal_id": aid,
        "feeding_time": "2025-04-23T10:00:00Z",
        "food_type": "meat"
    })
    assert sched.status_code == 201
    sid = sched.json()["id"]
    assert sched.json()["is_completed"] is False

    # попытка создать с несуществующим animal_id → 404
    bad = client.post("/feedings/", json={
        "animal_id": 99999, "feeding_time": "2025-04-23T10:00:00Z", "food_type": "meat"
    })
    assert bad.status_code == 404

    # изменяем только время и проверяем сброс флага completed
    # сперва пометим как выполненное
    client.post(f"/feedings/{sid}/complete")
    r_done = client.get("/feedings/").json()
    assert next(f["id"]==sid for f in r_done)
    # теперь меняем время
    old = client.get("/feedings/").json()
    r_put = client.put(f"/feedings/{sid}", json={"new_time": "2025-04-25T12:00:00Z"})
    assert r_put.status_code == 200
    assert r_put.json()["is_completed"] is False

    # меняем только тип пищи
    r_put2 = client.put(f"/feedings/{sid}", json={"new_food": "vegetables"})
    assert r_put2.status_code == 200
    assert r_put2.json()["is_completed"] is False

    # помечаем как выполненное и проверяем
    r_comp = client.post(f"/feedings/{sid}/complete")
    assert r_comp.status_code == 200
    assert r_comp.json()["is_completed"] is True

    # 404 при изменении/завершении несуществующего
    assert client.put("/feedings/99999", json={"new_time": "2025-04-25T12:00:00Z"}).status_code == 404
    assert client.post("/feedings/99999/complete").status_code == 404


def test_stats_endpoints_reflect_state():
    """Проверяем /stats/* после создания и перемещения."""
    # чистим зоопарк через новый инстанс приложения, либо доверимся что сессия чистая
    # создаём 2 животных и 2 вольера, один пустой, один с одним животным
    a1 = client.post("/animals/", json={
        "name": "Stat1", "birth_date": "2021-08-08T00:00:00Z", "gender": "male",
        "animal_type": "bird", "favorite_food": "fruits"
    }).json()["id"]
    a2 = client.post("/animals/", json={
        "name": "Stat2", "birth_date": "2021-09-09T00:00:00Z", "gender": "female",
        "animal_type": "bird", "favorite_food": "fruits"
    }).json()["id"]

    e1 = client.post("/enclosures/", json={
        "type": "bird", "size": 15.0, "capacity": 2, "is_clean": True, "animal_ids": [a1]
    }).json()["id"]
    e2 = client.post("/enclosures/", json={
        "type": "bird", "size": 15.0, "capacity": 2, "is_clean": True, "animal_ids": []
    }).json()["id"]

    # stats
    assert client.get("/stats/total_animals").json() >= 2
    assert client.get("/stats/free_enclosures").json() >= 1
    assert client.get("/stats/occupied_enclosures").json() >= 1
    by_type = client.get("/stats/animals_by_type").json()
    assert "bird" in by_type
    assert by_type["bird"] >= 2
