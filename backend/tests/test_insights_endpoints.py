import pytest

SALARY_REL = 1e-2

class TestSalarySummary:
    def test_summary_empty_database(self, client):
        response = client.get("/api/v1/insights/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 0
        assert data["min_salary"] == pytest.approx(0, abs=1e-9)
        assert data["max_salary"] == pytest.approx(0, abs=1e-9)

    def test_summary_with_data(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/summary")

        data = response.json()
        assert data["total_employees"] == 5
        assert data["min_salary"] == pytest.approx(14371.26, rel=SALARY_REL)
        assert data["max_salary"] == pytest.approx(110000, rel=SALARY_REL)
        assert data["avg_salary"] == pytest.approx(74309.03, rel=SALARY_REL)
        assert data["median_salary"] == pytest.approx(81521.74, rel=SALARY_REL)

    def test_summary_median_odd_count(self, client, sample_employees_data):
        for emp in sample_employees_data:
            client.post("/api/v1/employees", json=emp)

        response = client.get("/api/v1/insights/summary")

        data = response.json()
        assert data["median_salary"] == pytest.approx(81521.74, rel=SALARY_REL)


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
        assert germany["min_salary"] == pytest.approx(65000, rel=SALARY_REL)
        assert germany["max_salary"] == pytest.approx(75000, rel=SALARY_REL)
        assert germany["avg_salary"] == pytest.approx(70000, rel=SALARY_REL)


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
        assert sw_eng["avg_salary"] == pytest.approx(88260.87, rel=SALARY_REL)


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
        assert eng["min_salary"] == pytest.approx(81521.74, rel=SALARY_REL)
        assert eng["max_salary"] == pytest.approx(95000, rel=SALARY_REL)
        assert eng["avg_salary"] == pytest.approx(88260.87, rel=SALARY_REL)
