import pytest
import httplib
from unittestzero import Assert
from common.api.schema import validate
from plugins.pytest_restqa.rest_client import Connection
from plugins.pytest_restqa.pytest_restqa import load_credentials

# Generate fixture values for 'method' and 'resource'
def pytest_generate_tests(metafunc):

    for fixture in metafunc.fixturenames:
        test_set = list()
        id_list = list()

        if fixture == 'method':
            request_methods = ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'OPTIONS', ]
            test_set.extend(request_methods)
            id_list.extend(request_methods)

        if fixture == 'resource':
            # Discover available API resources
            api = Connection(pytest.config.option.base_url)
            r = api.get('/api/')
            data = r.json()
            current_version = data.get('current_version')
            r = api.get(current_version)
            api_resources = r.json().values()

            test_set.extend(api_resources)
            id_list.extend(api_resources)

        if test_set and id_list:
            metafunc.parametrize(fixture, test_set, ids=id_list)

def assert_response(api, resource, method, response_code=httplib.OK, response_schema='unauthorized', data={}):
    '''Issue the desired API method on the provided resource.  Assert that the
    http response and JSON schema are valid
    '''

    # Determine requested api method
    method = method.lower()

    # Call the desired API $method on the provided $resource (e.g.
    # api.get('/api/v1/me/')
    if method in ['get', 'head', 'options']:
        r = getattr(api, method)(resource)
    else:
        r = getattr(api, method)(resource, data)

    # Assert api response code matches expected
    assert r.code == response_code

    # Extract JSON response
    try:
        json = r.json()
    except ValueError:
        json = dict()

    # Validate API JSON response
    validate(json, resource, response_schema)

@pytest.fixture(scope="function")
def logout(api):
    '''Logout of the API on each function call'''
    api.logout()

@pytest.fixture(scope="function")
def login(api, testsetup):
    '''Login to the API on each function call'''
    api.login(*testsetup.credentials['default'].values())

@pytest.mark.api
@pytest.mark.skip_selenium
@pytest.mark.nondestructive
@pytest.mark.usefixtures("logout")
def test_unauthenticated(api, resource, method):

    expected_response = {
        'HEAD': (httplib.UNAUTHORIZED, 'head'),
        'GET': (httplib.UNAUTHORIZED, 'unauthorized'),
        'POST': (httplib.UNAUTHORIZED, 'unauthorized'),
        'PUT': (httplib.UNAUTHORIZED, 'unauthorized'),
        'PATCH': (httplib.UNAUTHORIZED, 'unauthorized'),
        'OPTIONS': (httplib.UNAUTHORIZED, 'unauthorized'),
    }

    exception_matrix = {
        '/api/v1/authtoken/': {
            'HEAD': (httplib.METHOD_NOT_ALLOWED, 'head'),
            'GET': (httplib.METHOD_NOT_ALLOWED, 'get'),
            'PUT': (httplib.METHOD_NOT_ALLOWED, 'put'),
            'PATCH': (httplib.METHOD_NOT_ALLOWED, 'patch'),
            'OPTIONS': (httplib.OK, 'options'),
            'POST': (httplib.BAD_REQUEST, 'bad_request'),
        },
    }

    # Generic response
    (expected_response_code, expected_response_schema) = expected_response[method]

    # Check if any api link requires special handling
    if resource in exception_matrix:
        if method in exception_matrix[resource]:
            (expected_response_code, expected_response_schema) = exception_matrix[resource][method]

    assert_response(api, resource, method, expected_response_code, expected_response_schema)

@pytest.mark.api
@pytest.mark.skip_selenium
@pytest.mark.nondestructive
# Either works ...
#  @pytest.mark.usefixtures("login")
# Or ...
#  @pytest.mark.usefixtures("authtoken")
@pytest.mark.usefixtures("authtoken")
def test_authenticated(api, resource, method):

    expected_response = {
        'HEAD': (httplib.OK, 'head'),
        'GET': (httplib.OK, 'get'),
        'POST': (httplib.BAD_REQUEST, 'bad_request'),
        'PUT': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        'PATCH': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        'OPTIONS': (httplib.OK, 'options'),
    }

    exception_matrix = {
        '/api/v1/activity_stream/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/authtoken/': {
            'HEAD': (httplib.METHOD_NOT_ALLOWED, 'head'),
            'GET': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
            'POST': (httplib.BAD_REQUEST, 'bad_request'),
        },
        '/api/v1/dashboard/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/config/': {
            'POST': (httplib.BAD_REQUEST, 'license_invalid'),
        },
        '/api/v1/me/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/inventory_sources/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/unified_jobs/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/unified_job_templates/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/system_job_templates/': {
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
        '/api/v1/schedules/': {  # Doesn't yet support POST
            'POST': (httplib.METHOD_NOT_ALLOWED, 'method_not_allowed'),
        },
    }

    # Generic response
    (expected_response_code, expected_response_schema) = expected_response[method]

    # Check if any api link requires special handling
    if resource in exception_matrix:
        if method in exception_matrix[resource]:
            (expected_response_code, expected_response_schema) = exception_matrix[resource][method]

    assert_response(api, resource, method, expected_response_code, expected_response_schema)
