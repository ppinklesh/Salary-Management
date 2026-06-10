class TestSalarySummary:
    def test_summary_empty_database(self, client):
        response = client.get("/api/v1/insights/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 0
        assert data["min_salary"] == 0
        assert data["max_salary"] == 0

    def test_summary_with_data(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/summary")

        data = response.json()
        assert data["total_employees"] == 5
        assert data["min_salary"] == 65000.00
        assert data["max_salary"] == 1200000.00
        assert data["avg_salary"] > 0
        assert data["median_salary"] > 0

    def test_summary_median_odd_count(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/summary")

        data = response.json()
        assert data["median_salary"] == 95000.00


class TestStatsByCountry:
    def test_by_country_empty(self, client):
        response = client.get("/api/v1/insights/by-country")

        assert response.status_code == 200
        assert response.json() == []

    def test_by_country_with_data(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-country")

        data = response.json()
        assert len(data) == 3

        countries = {item["country"] for item in data}
        assert countries == {"United States", "Germany", "India"}

    def test_by_country_correct_stats(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-country")

        data = response.json()
        germany = next(item for item in data if item["country"] == "Germany")
        assert germany["employee_count"] == 2
        assert germany["min_salary"] == 65000.00
        assert germany["max_salary"] == 75000.00
        assert germany["avg_salary"] == 70000.00


class TestStatsByJobTitle:
    def test_by_job_title(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-job-title")

        data = response.json()
        assert len(data) == 4

        titles = {item["job_title"] for item in data}
        assert "Software Engineer" in titles
        assert "Product Manager" in titles

    def test_by_job_title_filtered_by_country(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-job-title?country=United States")

        data = response.json()
        assert len(data) == 2

        titles = {item["job_title"] for item in data}
        assert titles == {"Software Engineer", "Product Manager"}

    def test_by_job_title_correct_avg(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-job-title")

        data = response.json()
        sw_eng = next(item for item in data if item["job_title"] == "Software Engineer")
        assert sw_eng["employee_count"] == 2
        assert sw_eng["avg_salary"] == 85000.00


class TestStatsByDepartment:
    def test_by_department(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-department")

        data = response.json()
        assert len(data) == 4

        departments = {item["department"] for item in data}
        assert "Engineering" in departments
        assert "Product" in departments

    def test_by_department_correct_stats(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/by-department")

        data = response.json()
        eng = next(item for item in data if item["department"] == "Engineering")
        assert eng["employee_count"] == 2
        assert eng["min_salary"] == 75000.00
        assert eng["max_salary"] == 95000.00
