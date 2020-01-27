## AWX-PF E2E
### Introduction
This is an automated functional test suite for the AWX Patternfly UI. It uses Cypress as its base framework.

*See CONTRIBUTING.md for guidelines on what to do before opening a PR.*

### Framework Reference 
- [Cypress Github page](https://github.com/cypress-io/cypress)
- [Cypress Docs](https://docs.cypress.io)
- [Percy Docs](https://docs.percy.io/docs/cypress)
- [awxkit](https://github.com/ansible/awx/tree/devel/awxkit)

### Requirements and installation.

#### Short Version
Run this block and include the username and password for an admin account for your AWX instance. If you already have AWX cloned, remove that line and adjust the python install paths as needed.: 
```
export CYPRESS_AWX_E2E_USERNAME=username
export CYPRESS_AWX_E2E_PASSWORD=password
export CYPRESS_baseUrl=https://localhost:3001
python3 -m venv ~/.envs/awxkit
source ~/.envs/awxkit/bin/activate
pip install nodeenv
nodeenv -p
git clone https://github.com/ansible/awx
pip install -e awx/awxkit[crypto] -r awx/awxkit/requirements.txt
```

In *this* directory (the directory containing cypress.json), run:

```
npm install
```

This will install cypress, as well as a few dependencies for linting.

#### Long version:
Since this suite leverages `awxkit` to perform setup functions, you'll need to have a Python 3 virtual environment that has `awxkit` installed, as well as `nodeenv` so Node subprocesses can access installed modules:
```
python3 -m venv ~/some_directory
```

The path at the end can be any empty directory you like. Start the virtual environment with: 
```
source ~/some_directory/bin/activate
```

Now, link a Node virtual environment to the Python virtual environment:
```
# While python virtual environment is active
pip install nodeenv
nodeenv -p
```

To install awxkit for use in fixtures:
```
git clone https://github.com/ansible/awx
pip install -e awx/awxkit[crypto] -r awx/awxkit/requirements.txt -r awx/requirements/requirements_dev.txt

```

You should now have a functional environment to set up the test framework. 

See details for awx-pf setup in general [here](https://github.com/ansible/awx/tree/devel/awx/ui_next). Installation steps for awx-pf installs the dependencies needed to run Cypress. If you're not spinning up the awx-pf instance yourself, use the nodeJS and npm requirements listed in the aforementioned UI repo link, and then ensure Cypress is installed via npm:
```
npm install cypress  # --save-dev option will update dependencies in package.json
```

### Configuring Cypress settings
In `cypress.json`, set the baseUrl value to that of the target UI you are testing. Do NOT include a trailing slash. This will break awxkit functions. For example, "https://localhost:3001" is fine, but "https://localhost:3001/" is not. 

Inserting your credentials into cypress.json in plaintext isn't recommended, for standard security reasons. There are multiple ways to override the variables, listed [here](https://docs.cypress.io/guides/guides/environment-variables.html#Setting). The simplest way is to take an environment variable and prefix it with `CYPRESS_`. Cypress searches for this environment variable prefix and makes it available. Cypress can _only_ see environment variables with this prefix, or vars set in a cypress config file. 
```
export CYPRESS_AWX_E2E_USERNAME=foo 
export CYPRESS_AWX_E2E_PASSWORD=bar
export CYPRESS_baseUrl=https://localhost:3001
npm run cypress # etc, etc,
```

### Usage
To open the Cypress test inspection tools to assist with test development (assumes you are at the top level directory of `tower-qa`):
```
npm --prefix tower-qa/ui-tests-/awx-pf-tests run cypress
```

To run the test suite in headless mode (assuming you are in the same directory as `cypress.json`):
```
npm run cypress-headless
```

### Integrating Percy with your Cypress tests:

Before you can successfully run Percy, the PERCY_TOKEN environment variable must be set.
The token can be found in your project settings on percy dashboard

```
export PERCY_TOKEN=<your token here>
```
Now, insert the cypress command `cy.percySnapshot()` in the tests where you would like percy to take snapshots for visual diffing.

For more options to adjust attributes like snapshot name, width and height, follow the documentation [here](https://docs.percy.io/docs/cypress#section-configuration)

Finally, use the following command to run the tests:
```
npx percy exec -- cypress run
```

That's it! Now, whenever CI runs, a snapshot of the app in that state will be uploaded to Percy for visual regression testing!


### Directory Organization
At the top level, there is a `cypress.json` file and a `cypress/` directory; within this directory, there are four folders:
- `fixtures/`: Contains JSON payloads for usage in tests.
- `integration/`: Contains the tests themselves.
- `plugins/`: Contains the loader for Cypress plugins and any plugins you might like to add.
- `support/`: Contains custom commands and setup functions for global use in the test suite.

For more information regarding these folders, please see the Cypress documentation.

### Tips and Tricks
- `support/commands.js` contains plenty of helper functions. Of note are `akit` and `createOrReplace`, the first of which calls `akit_client.py` to authenticate with `akit` and perform any awxkit v2 command you'd like. For example, calling `cy.akit('job_templates.create()')` in Cypress is the same thing as going to awxkit directly and calling `v2.job_templates.create()`. 

- `cy.createOrReplace('job_templates', 'something')` is just a shortcut function to avoid having to write `cy.akit('job_templates.create_or_replace("name=something")')`. In case you don't know, v2.xyz.create_or_replace requires a `username` param instead of `name` when creating users, but the wrapper function handles that for you.
- When calling commands directly with `cy.akit()`, make sure you look at how the command is accepted in awxkit to ensure correct syntax. 
- If you need a for-loop that can iterate over a list of elements, you can't do a traditional loop, unfortunately. Seems to be because of the async nature of Cypress and the way event ordering is handled. You can generate an array, then use that array within the same test context to iterate over numbered elements. An example:
    ```
    // Generate an array of the numbers 1-5
    let arr = Array.from({length:5}, (v, k) => k + 1)

    // cy.wrap the array, which will keep the event order straight 
    cy.wrap(arr).each(function(i) {
      cy.createOrReplace('credentials', `test-credentials-${i}`).as(`cred${i}`)
    })

    ```
This will then generate five credential objects, named `test-credentials-1`, and so forth. The .as(`cred${i}`) section will make each object available as `this.creds1`, `this.creds2`, and so on.

- Cypress clears UI session data entirely during each test to avoid caching and cookie issues. Sometimes, this means you need to manipulate cookies directly yourself. For an example, see the custom `apiRequest()` function present in `cypress/support/commands.js`.

- Avoid overlapping dependencies as much as possible. The current configuration calls a custom command, `generateTestID()`, which is has been made available as `this.testID` in every individual test. Feel free to use this to generate custom name suffixes to avoid conflicts. `cy.createOrReplace()` should also help in this regard.


### Docker
```
cd tower-qa/ui-tests/awx-pf-tests
docker build -t awx-pf-tests .
docker run --network tools_default --link 'tools_ui_next_1:ui-next' -v $PWD:/e2e -w /e2e awx-pf-tests run --project .
```
