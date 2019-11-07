import '@percy/cypress'

/**
 * Generates a random number to be assigned to each individual test run.
 * This is useful for randomly generated names for resources used in tests.
 */
Cypress.Commands.add('generateTestID', () => cy.wrap(`${Cypress._.random(0, 1e10)}`).as('testID'))

/**
 * Shell built around cy.request(). Cypress attempts to handle CSRF token verification to an extent,
 * but AWX uses headers that Cypress doesn't handle out of the box. This utility function allows
 * cy.request() to interact with the AWX server correctly.
 *
 * @param {string} method - REST call. Can be GET, POST, PUT, DELETE...
 * @param {string} url - API endpoint to access. Base URL is configured,
 *                       so you may type '/api/v2/organizations', for example.
 * @param {Object} body - Body of the request made.
 * @param {boolean} form - False by default. This is set to true for login functions, mostly,
 *                         but its behavior can be viewed in the documentation for cy.request().
 */
Cypress.Commands.add('apiRequest', (method, url, body, form = false) => {
  cy.request(url).then(() =>
    cy.getCookie('csrftoken').then(cookie => {
      body.csrfmiddlewaretoken = cookie.value
      cy.request({
        method,
        url,
        form,
        headers: {
          referer: `${Cypress.config().baseUrl}/api/login/`,
          'x-csrftoken': `${cookie.value}`,
        },
        body: body,
      })
    })
  )
})

/**
 * Logs into the AWX server. CSRF tokens are cleared on every test in Cypress for complete
 * test isolation. As such, this is called in the beforeEach() function of all tests
 * (see cypress/support/index.js).
 * */
Cypress.Commands.add('login', () => {
  const body = {
    username: Cypress.env('AWX_E2E_USERNAME'),
    password: Cypress.env('AWX_E2E_PASSWORD'),
    next: '/api/',
  }
  cy.apiRequest('POST', `/api/login/`, body, true)
})

/**
 * Interacts with awxkit to run create_or_replace(),
 * which creates an arbitrary resource (and its dependencies).
 * For more information on setting up awxkit to work with Cypress,
 * please refer to the README in the cypress.json directory.
 *
 * Example usage:
 * cy.createOrReplace('job_templates', 'foo')
 * cy.createOrReplace('inventory', 'bar')
 * Note that inventory in the above example isn't plural to match awxkit.v2.
 *
 * @param {string} resource - Any resource type available under awxkit.v2
 * @param {string} name - The name of the resource. For user objects, this
 *                        value should be set to the username.
 * */
Cypress.Commands.add('createOrReplace', (resource, name) => {
  const options = `--resource="${resource}" --name="${name}"`
  const command = `python akit_client.py create_or_replace ${options} "${Cypress.config().baseUrl}"`
  console.log(`Calling awxkit create_or_replace(): ${options}`)
  cy.exec(command).then(ret => {
    expect(ret.stderr).to.be.empty
    return JSON.parse(ret.stdout)
  })
})

/**
 * Interacts with awxkit to run arbitrary v2 commands.
 * For more information on setting up awxkit to work with Cypress,
 * please refer to the README in the cypress.json directory.
 *
 * Example usage:
 * cy.akit('job_templates.create_or_replace(name="foo")')
 * This is equivalent to v2.job_templates.create_or_replace(name="foo") in awxkit.
 *
 * @param {string} akitcommand - Any awxkit v2 object expression.
 * */
Cypress.Commands.add('akit', akitcommand => {
  const options = `--akitcommand='${akitcommand}'`
  const command = `python akit_client.py akit ${options} '${Cypress.config().baseUrl}'`
  console.log(`Calling awxkit command: ${command}`)
  cy.exec(command).then(ret => {
    expect(ret.stderr).to.be.empty
    return JSON.parse(ret.stdout)
  })
})
