Feature: User Sign Up

  Scenario: Successful organization sign up
    Given I am on the organization sign up page
    When I enter valid organization details
    And I submit the organization sign up form
    Then I should see a confirmation that the organization was registered

  Scenario: Successful teacher sign up
    Given I am on the teacher sign up page
    When I enter valid teacher details
    And I submit the teacher sign up form
    Then I should see a confirmation that the teacher was registered

  Scenario: Duplicate organization name
    Given an organization named "Acme School" already exists
    When I try to sign up another organization with the name "Acme School"
    Then I should see an error about duplicate organization name

  Scenario: Duplicate email for teacher
    Given a teacher with email "john@teachers.com" already exists
    When I try to sign up another teacher with the email "john@teachers.com"
    Then I should see an error about duplicate email