class TestCreateEmployee:
    def test_create_employee_success(self, client, sample_employee_data):
        response = client.post("/api/v1/employees", json=sample_employee_data)

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["salary"] == 95000.00
        assert data["id"] is not None

    def test_create_employee_duplicate_email(self, client, sample_employee_data):
        client.post("/api/v1/employees", json=sample_employee_data)
        response = client.post("/api/v1/employees", json=sample_employee_data)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_employee_invalid_email(self, client, sample_employee_data):
        sample_employee_data["email"] = "invalid-email"
        response = client.post("/api/v1/employees", json=sample_employee_data)

        assert response.status_code == 422

    def test_create_employee_negative_salary(self, client, sample_employee_data):
        sample_employee_data["salary"] = -5000
        response = client.post("/api/v1/employees", json=sample_employee_data)

        assert response.status_code == 422

    def test_create_employee_invalid_employment_type(self, client, sample_employee_data):
        sample_employee_data["employment_type"] = "intern"
        response = client.post("/api/v1/employees", json=sample_employee_data)

        assert response.status_code == 422


class TestGetEmployee:
    def test_get_employee_success(self, client, sample_employee_data):
        create_resp = client.post("/api/v1/employees", json=sample_employee_data)
        employee_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/employees/{employee_id}")

        assert response.status_code == 200
        assert response.json()["full_name"] == "John Doe"

    def test_get_employee_not_found(self, client):
        response = client.get("/api/v1/employees/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestListEmployees:
    def test_list_employees_empty(self, client):
        response = client.get("/api/v1/employees")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_employees_with_data(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/employees")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["data"]) == 5

    def test_list_employees_pagination(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/employees?page=1&page_size=2")

        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3

    def test_list_employees_search(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/employees?search=alice")

        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["full_name"] == "Alice Johnson"

    def test_list_employees_filter_by_country(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/employees?country=Germany")

        data = response.json()
        assert data["total"] == 2
        for emp in data["data"]:
            assert emp["country"] == "Germany"

    def test_list_employees_filter_by_department(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/employees?department=Engineering")

        data = response.json()
        assert data["total"] == 2

    def test_list_employees_sort_by_salary_desc(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/employees?sort_by=salary&sort_order=desc")

        data = response.json()
        salaries = [emp["salary"] for emp in data["data"]]
        assert salaries == sorted(salaries, reverse=True)


class TestUpdateEmployee:
    def test_update_employee_success(self, client, sample_employee_data):
        create_resp = client.post("/api/v1/employees", json=sample_employee_data)
        employee_id = create_resp.json()["id"]

        response = client.put(
            f"/api/v1/employees/{employee_id}",
            json={"salary": 105000.00, "job_title": "Senior Software Engineer"},
        )

        assert response.status_code == 200
        assert response.json()["salary"] == 105000.00
        assert response.json()["job_title"] == "Senior Software Engineer"

    def test_update_employee_not_found(self, client):
        response = client.put(
            "/api/v1/employees/99999",
            json={"salary": 105000.00},
        )

        assert response.status_code == 404

    def test_update_employee_duplicate_email(self, client, sample_employees_data):
        for emp in sample_employees_data[:2]:
            client.post("/api/v1/employees", json=emp)

        response = client.put(
            "/api/v1/employees/1",
            json={"email": "bob@example.com"},
        )

        assert response.status_code == 409

    def test_update_employee_no_fields(self, client, sample_employee_data):
        create_resp = client.post("/api/v1/employees", json=sample_employee_data)
        employee_id = create_resp.json()["id"]

        response = client.put(f"/api/v1/employees/{employee_id}", json={})

        assert response.status_code == 400


class TestDeleteEmployee:
    def test_delete_employee_success(self, client, sample_employee_data):
        create_resp = client.post("/api/v1/employees", json=sample_employee_data)
        employee_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/employees/{employee_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/employees/{employee_id}")
        assert get_response.status_code == 404

    def test_delete_employee_not_found(self, client):
        response = client.delete("/api/v1/employees/99999")
        assert response.status_code == 404
