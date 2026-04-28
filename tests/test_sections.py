# Sections
import pytest

@pytest.mark.parametrize("route, expected_status", [
    ("/general/Welcome", 200),
    ("/general/Training", 200),
    ("/general/Authentication", 200),
    ("/general/Equipment", 200),
    ("/general/Information sources", 200),
    ("/general/Organisation structure", 200),
    ("/general/myHR", 200),
    ("/general/Employee benefits", 200),

    ("/access/Jira", 200),
    ("/access/Confluence", 200),
    ("/access/Figma", 200),
    ("/access/ServiceNow", 200),
    ("/access/Service accounts", 200),
    ("/access/Developer folders", 200),
    ("/access/Developer tools", 200),
])
def test_sidebar_routes(client, route, expected_status):
    # login first (required for all pages)
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get(route, follow_redirects=True)

    assert response.status_code == expected_status