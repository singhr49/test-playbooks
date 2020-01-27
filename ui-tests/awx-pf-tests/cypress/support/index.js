// ***********************************************************
// Support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'
import '@percy/cypress'

// Alternatively you can use CommonJS syntax:
// require('./commands')

beforeEach(() => {
  cy.login() // For test isolation, Cypress clears out user sessions (see Cypress Best Practices)
  cy.generateTestID() // Generates a number for unique name suffixes on every test run.
})
