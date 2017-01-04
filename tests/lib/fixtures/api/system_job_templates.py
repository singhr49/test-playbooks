import pytest


@pytest.fixture(scope="function", params=['cleanup_jobs', 'cleanup_activitystream', 'cleanup_facts'])
def system_job_template(request, api_system_job_templates_pg):
    # Selectively xfail test for cases known to fail due to
    # https://github.com/ansible/ansible-tower/issues/2655
    if request.param == 'cleanup_facts' and request.node.function.func_name == 'test_system_job_notifications':
        pytest.xfail('https://github.com/ansible/ansible-tower/issues/2655')

    return request.getfuncargvalue(request.param + '_template')


@pytest.fixture(scope="function")
def cleanup_jobs_template(request, api_system_job_templates_pg):
    """Return a System_Job_Template object representing the 'cleanup_jobs' system
    job template.
    """
    matches = api_system_job_templates_pg.get(job_type='cleanup_jobs')
    assert matches.count == 1, "Unexpected number of results (%s) when querying " \
        "for system_job_template job_type:cleanup_jobs" % matches.count
    return matches.results[0]


@pytest.fixture(scope="function")
def cleanup_activitystream_template(request, api_system_job_templates_pg):
    """Return a System_Job_Template object representing the 'cleanup_activitystream'
    system job template.
    """
    matches = api_system_job_templates_pg.get(job_type='cleanup_activitystream')
    assert matches.count == 1, "Unexpected number of results (%s) when querying " \
        "for system_job_template job_type:cleanup_activitystream" % matches.count
    return matches.results[0]


@pytest.fixture(scope="function")
def cleanup_facts_template(request, api_system_job_templates_pg):
    """Return a System_Job_Template object representing the 'cleanup facts'
    system job template.
    """
    matches = api_system_job_templates_pg.get(job_type='cleanup_facts')
    assert matches.count == 1, "Unexpected number of results (%s) when querying " \
        "for system_job_template job_type:cleanup_activitystream" % matches.count
    return matches.results[0]
