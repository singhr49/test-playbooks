/**
 * Verifies CRUD operations on Project.
 */
context('Reaches a 404', function() {
    it('reaches a 404 when trying to get the Project list', function() {
      cy.server()
      cy.route({
        url: '**/api/v2/projects/*',
        status: 404,
        response: {},
      }).as('jt')
      cy.visit('/#/projects')
    })
  })
  context('Create and Edit Job Template', function() {
    before(function() {
      cy.createOrReplace('organizations', `create-proj-org`).as('org')
    })
  
    it('can create a Project', function() {
      cy.visit('/#/projects')
      cy.get('a[aria-label=Add]').click()
      cy.get('#project-name').type(`create-proj-${this.testID}`)
      cy.get('#project-description').type(`Creation test for Project. Test ID: ${this.testID}`)
      cy.get('#organization').click()
      cy.get('input[aria-label*="Search text input"]').type(`${this.org.name}{enter}	`)
      cy.get(`#selected-${this.org.id}`).click()
      cy.get('.pf-c-modal-box__footer button[class*="pf-m-primary"]').click()
      cy.get('#scm_type').select('Git')
      cy.get('#project-scm-url').type(`https://github.com/ansible/ansible-tower-samples`)
      cy.get('button[aria-label=Save]').click()
      cy.get('dd:nth-of-type(1)').should('have.text', `create-proj-${this.testID}`)
    })
  })
  
  context('Edit Project', function() {
    before(function() {
      cy.createOrReplace('projects', `proj-to-edit`).as('proj')
    })
  
    it('can edit a project', function() {
      cy.visit(`/#/projects/${this.proj.id}`)
      cy.get('a[aria-label=edit]').click()
      cy.get('#project-name')
        .clear()
        .type(`edited-proj-${this.testID}`)
      cy.get('#project-description')
        .clear()
        .type(`Edited test for Project. Test ID: ${this.testID}`)
      cy.get('button[aria-label=Save]').click()
      cy.get('dd:nth-of-type(1)').should('have.text', `create-proj-${this.testID}`)
    })
  })
  
  context('Delete Project', function() {
    before(function() {
        cy.createOrReplace('projects', `proj-to-delete`).as('proj')
    })
  
    it('can delete a project', function() {
      cy.visit('/#/projects')
      cy.get('input[aria-label*="Search"]').type(`${this.proj.name}{enter}	`)
      cy.wait(500)
      cy.get(`input[id="select-project-${this.proj.id}"][type="checkbox"]`).click()
      cy.wait(500)
      cy.get('button[aria-label="Delete"]').click()
      cy.wait(500)
      cy.get('button[aria-label="confirm delete"]').click()
      cy.get('.pf-c-empty-state .pf-c-empty-state__body').should(
        'have.class',
        'pf-c-empty-state__body'
      )
    })
  })
  