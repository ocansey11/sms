Feature: Error Handling

  Scenario: Sign up with missing required fields
    Given I am on the organization sign up page
    When I submit the organization sign up form with missing admin email
    Then I should see an error about missing required fields

  Scenario: Sign up with weak password
    Given I am on the teacher sign up page
    When I enter a weak teacher password "123"
    And I submit the teacher sign up form
    Then I should see an error about password strength

  Scenario: Sign up with duplicate email
    Given a teacher with email "john@teachers.com" already exists
    When I try to sign up another teacher with the email "john@teachers.com"
    Then I should see an error about duplicate email

  Scenario: Sign up with duplicate organization name
    Given an organization named "Acme School" already exists
    When I try to sign up another organization with the name "Acme School"
    Then I should see an error about duplicate organization name