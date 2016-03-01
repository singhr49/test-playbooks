import httplib
import pytest
import common.api
import common.tower
from common.api.pages import *  # NOQA


def navigate(api, url, field):
    '''
    Return a json attribute from the given url.  While one can simply
    concatenate strings to form a URL, this method is preferred to ensure the
    API is capable of self-referencing.

    Examples:
     * navigate(api, '/api/', 'current_version') returns '/api/v1'
     * navigate(api, '/api/v1/, 'config') returns '/api/v1/config'
    '''
    if not url.endswith('/'):
        url += '/'
    data = api.get(url).json()
    return data.get(field)


@pytest.fixture(scope="module")
def api_default_page_size(testsetup):
    '''
    The tower default pagination size
    '''
    return 25


@pytest.fixture(scope="module")
def api(testsetup):
    '''
    Convenience fixture that returns api object
    '''
    return testsetup.api


@pytest.fixture(scope="module")
def api_v1_url(request, api):
    '''
    Navigate the API and return a link to the base api for the requested version.
    For example, if --api-version=v1, returns string '/api/v1/'
    '''
    api_version = request.config.getvalue('api_version')
    available_versions = navigate(api, '/api', 'available_versions')

    if api_version in [None, 'current_version']:
        current_version = navigate(api, '/api', 'current_version')
        # Update the stored api.version
        for version, link in available_versions.items():
            if current_version == link:
                api.version = version
                request.config.option.api_version = version
                break
        return current_version
    else:
        assert api_version in available_versions, "Requested tower version (%s) not available.  Choices include: %s" % (api_version, available_versions)
        return available_versions.get(api_version)


@pytest.fixture(scope="module")
def api_v1_pg(testsetup, api_v1_url):
    return Base(testsetup, base_url=api_v1_url).get()


#
# /api/v1/authtoken
#
@pytest.fixture(scope="module")
def api_authtoken_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'authtoken')


@pytest.fixture(scope="module")
def api_authtoken_pg(testsetup, api_authtoken_url):
    return AuthToken_Page(testsetup, base_url=api_authtoken_url)


@pytest.fixture(scope="module")
def authtoken(api, testsetup, api_authtoken_url):
    '''
    Logs in to the application with default credentials and returns the
    home page
    '''

    payload = dict(username=testsetup.credentials['default']['username'],
                   password=testsetup.credentials['default']['password'])

    r = api.post(api_authtoken_url, payload)
    assert r.status_code == httplib.OK
    # FIXME - build and return a Authtoken_Page() object
    json = r.json()
    testsetup.api.login(token=json['token'])
    return json


#
# /api/v1/settings
#
@pytest.fixture(scope="module")
def api_settings_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'settings')


@pytest.fixture(scope="module")
def api_settings_pg(testsetup, api_settings_url):
    return Settings_Page(testsetup, base_url=api_settings_url)


#
# /api/v1/dashboard
#
@pytest.fixture(scope="module")
def api_dashboard_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'dashboard')


@pytest.fixture(scope="module")
def api_dashboard_pg(testsetup, api_dashboard_url):
    return Dashboard_Page(testsetup, base_url=api_dashboard_url)


#
# /api/v1/ping
#
@pytest.fixture(scope="module")
def api_ping_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'ping')


@pytest.fixture(scope="module")
def api_ping_pg(testsetup, api_ping_url):
    return Ping_Page(testsetup, base_url=api_ping_url)


#
# /api/v1/config
#
@pytest.fixture(scope="module")
def api_config_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'config')


@pytest.fixture(scope="module")
def api_config_pg(testsetup, api_config_url):
    return Config_Page(testsetup, base_url=api_config_url)


@pytest.fixture(scope="module")
def tower_version(api_config_pg):
    return api_config_pg.get().version


@pytest.fixture(scope="module")
def tower_version_cmp(request, tower_version):
    return lambda x: common.tower.version_cmp(tower_version, x)


@pytest.fixture(scope='module')
def ansible_version(api_config_pg):
    '''Returns the ansible version of the system under test.'''
    return api_config_pg.get().ansible_version


@pytest.fixture(scope="module")
def ansible_version_cmp(request, ansible_version):
    return lambda x: common.tower.version_cmp(ansible_version, x)


@pytest.fixture(scope="module")
def awx_config(api, api_v1_url):
    url = navigate(api, api_v1_url, 'config')
    r = api.get(url)
    assert r.status_code == httplib.OK
    return r.json()


#
# /api/v1/me
#
@pytest.fixture(scope="module")
def api_me_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'me')


@pytest.fixture(scope="module")
def api_me_pg(testsetup, api_me_url):
    return Me_Page(testsetup, base_url=api_me_url)


#
# /api/v1/organizations
#
@pytest.fixture(scope="module")
def api_organizations_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'organizations')


@pytest.fixture(scope="module")
def api_organizations_pg(testsetup, api_organizations_url):
    return Organizations_Page(testsetup, base_url=api_organizations_url)


#
# /api/v1/users
#
@pytest.fixture(scope="module")
def api_users_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'users')


@pytest.fixture(scope="module")
def api_users_pg(testsetup, api_users_url):
    return Users_Page(testsetup, base_url=api_users_url)


#
# /api/v1/teams
#
@pytest.fixture(scope="module")
def api_teams_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'teams')


@pytest.fixture(scope="module")
def api_teams_pg(testsetup, api_teams_url):
    return Teams_Page(testsetup, base_url=api_teams_url)


#
# /api/v1/projects
#
@pytest.fixture(scope="module")
def api_projects_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'projects')


@pytest.fixture(scope="module")
def api_projects_pg(testsetup, api_projects_url):
    return Projects_Page(testsetup, base_url=api_projects_url)


#
# /api/v1/activity_stream
#
@pytest.fixture(scope="module")
def api_activity_stream_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'activity_stream')


@pytest.fixture(scope="module")
def api_activity_stream_pg(testsetup, api_activity_stream_url):
    return Activity_Stream_Page(testsetup, base_url=api_activity_stream_url)


#
# /api/v1/credentials
#
@pytest.fixture(scope="module")
def api_credentials_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'credentials')


@pytest.fixture(scope="module")
def api_credentials_pg(testsetup, api_credentials_url):
    return Credentials_Page(testsetup, base_url=api_credentials_url)


#
# /api/v1/inventory
#
@pytest.fixture(scope="module")
def api_inventories_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'inventory')


@pytest.fixture(scope="module")
def api_inventories_pg(testsetup, api_inventories_url):
    return Inventories_Page(testsetup, base_url=api_inventories_url)


#
# /api/v1/inventory_sources
#
@pytest.fixture(scope="module")
def api_inventory_sources_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'inventory_sources')


@pytest.fixture(scope="module")
def api_inventory_sources_pg(testsetup, api_inventory_sources_url):
    return Inventory_Sources_Page(testsetup, base_url=api_inventory_sources_url)


#
# /api/v1/inventory_scripts
#
@pytest.fixture(scope="module")
def api_inventory_scripts_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'inventory_scripts')


@pytest.fixture(scope="module")
def api_inventory_scripts_pg(testsetup, api_inventory_scripts_url):
    return Inventory_Scripts_Page(testsetup, base_url=api_inventory_scripts_url)


#
# /api/v1/groups
#
@pytest.fixture(scope="module")
def api_groups_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'groups')


@pytest.fixture(scope="module")
def api_groups_pg(testsetup, api_groups_url):
    return Groups_Page(testsetup, base_url=api_groups_url)


#
# /api/v1/hosts
#
@pytest.fixture(scope="module")
def api_hosts_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'hosts')


@pytest.fixture(scope="module")
def api_hosts_pg(testsetup, api_hosts_url):
    return Hosts_Page(testsetup, base_url=api_hosts_url)


#
# /api/v1/job_templates
#
@pytest.fixture(scope="module")
def api_job_templates_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'job_templates')


@pytest.fixture(scope="module")
def api_job_templates_pg(testsetup, api_job_templates_url):
    return Job_Templates_Page(testsetup, base_url=api_job_templates_url)


#
# /api/v1/schedules
#
@pytest.fixture(scope="module")
def api_schedules_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'schedules')


@pytest.fixture(scope="module")
def api_schedules_pg(testsetup, api_schedules_url):
    return Schedules_Page(testsetup, base_url=api_schedules_url)


#
# /api/v1/jobs
#
@pytest.fixture(scope="module")
def api_jobs_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'jobs')


@pytest.fixture(scope="module")
def api_jobs_pg(testsetup, api_jobs_url):
    return Jobs_Page(testsetup, base_url=api_jobs_url)


#
# /api/v1/unified_jobs
#
@pytest.fixture(scope="module")
def api_unified_jobs_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'unified_jobs')


@pytest.fixture(scope="module")
def api_unified_jobs_pg(testsetup, api_unified_jobs_url):
    return Jobs_Page(testsetup, base_url=api_unified_jobs_url)


#
# /api/v1/unified_job_templates
#
@pytest.fixture(scope="module")
def api_unified_job_templates_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'unified_job_templates')


@pytest.fixture(scope="module")
def api_unified_job_templates_pg(testsetup, api_unified_job_templates_url):
    return Unified_Job_Templates_Page(testsetup, base_url=api_unified_job_templates_url)


#
# /api/v1/system_jobs
#
@pytest.fixture(scope="module")
def api_system_jobs_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'system_jobs')


@pytest.fixture(scope="module")
def api_system_jobs_pg(testsetup, api_system_jobs_url):
    # FIXME - this should be System_Jobs_Page
    return Jobs_Page(testsetup, base_url=api_system_jobs_url)


#
# /api/v1/system_job_templates
#
@pytest.fixture(scope="module")
def api_system_job_templates_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'system_job_templates')


@pytest.fixture(scope="module")
def api_system_job_templates_pg(testsetup, api_system_job_templates_url):
    return System_Job_Templates_Page(testsetup, base_url=api_system_job_templates_url)


#
# /api/v1/ad_hoc_commands
#
@pytest.fixture(scope="module")
def api_ad_hoc_commands_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'ad_hoc_commands')


@pytest.fixture(scope="module")
def api_ad_hoc_commands_pg(testsetup, api_ad_hoc_commands_url):
    return Ad_Hoc_Commands_Page(testsetup, base_url=api_ad_hoc_commands_url)


@pytest.fixture(scope="module")
def region_choices(api_inventory_sources_pg):
    options = api_inventory_sources_pg.options()

    # The format is a list of lists in the format: [['<internal-string>', '<human-readable-string>'], ...]
    return dict(ec2=[r[0] for r in options.json.get('actions', {}).get('GET', {}).get('source_regions', {}).get('ec2_region_choices', [])],
                rax=[r[0] for r in options.json.get('actions', {}).get('GET', {}).get('source_regions', {}).get('rax_region_choices', [])],
                azure=[r[0] for r in options.json.get('actions', {}).get('GET', {}).get('source_regions', {}).get('azure_region_choices', [])],
                gce=[r[0] for r in options.json.get('actions', {}).get('GET', {}).get('source_regions', {}).get('gce_region_choices', [])])


#
# /api/v1/notifications
#
@pytest.fixture(scope="module")
def api_notifications_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'notifications')


@pytest.fixture(scope="module")
def api_notifications_pg(testsetup, api_notifications_url):
    return Notifications_Page(testsetup, base_url=api_notifications_url)


#
# /api/v1/notifiers
#
@pytest.fixture(scope="module")
def api_notifiers_url(api, api_v1_url):
    return navigate(api, api_v1_url, 'notifiers')


@pytest.fixture(scope="module")
def api_notifiers_pg(testsetup, api_notifiers_url):
    return Notifiers_Page(testsetup, base_url=api_notifiers_url)
