Feature: Password Validation

  Scenario: Sign up with a weak password as organization admin
    Given I am on the organization sign up page
    When I enter a weak admin password "123"
    And I submit the organization sign up form
    Then I should see an error about password strength

  Scenario: Sign up with a weak password as teacher
    Given I am on the teacher sign up page
    When I enter a weak teacher password "password"
    And I submit the teacher sign up form
    Then I should see an error about password strength

  Scenario: Sign up with a strong password as organization admin
    Given I am on the organization sign up page
    When I enter a strong admin password "StrongPass123!"
    And I submit the organization sign up form
    Then I should see a confirmation that the organization was registered

  Scenario: Sign up with a strong password as teacher
    Given I am on the teacher sign up page
    When I enter a strong teacher password "StrongPass123!"
    And I submit the teacher sign up form
    Then I should see a confirmation that the teacher