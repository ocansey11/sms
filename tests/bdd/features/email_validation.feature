Feature: Email Validation

  Scenario: Sign up with invalid organization admin email
    Given I am on the organization sign up page
    When I enter an invalid admin email "not-an-email"
    And I submit the organization sign up form
    Then I should see an error about invalid email format

  Scenario: Sign up with invalid teacher email
    Given I am on the teacher sign up page
    When I enter an invalid teacher email "bademail@"
    And I submit the teacher sign up form
    Then I should see an error about invalid email format

  Scenario: Sign up with valid organization admin email
    Given I am on the organization sign up page
    When I enter a valid admin email "admin@school.edu"
    And I submit the organization sign up form
    Then I should see a confirmation that the organization was registered

  Scenario: Sign up with valid teacher email
    Given I am on the teacher sign up page
    When I enter a valid teacher email "teacher@school.com"
    And I submit the teacher sign up form
    Then I should see a confirmation that the teacher was registered