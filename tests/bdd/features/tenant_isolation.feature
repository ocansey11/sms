Feature: Tenant Data Isolation

  Scenario: Organization admin cannot access another organization's data
    Given two organizations "Alpha School" and "Beta Academy" exist
    And I am logged in as an admin of "Alpha School"
    When I try to access data belonging to "Beta Academy"
    Then I should be denied access

  Scenario: Teacher cannot access another organization's data
    Given two organizations "Alpha School" and "Beta Academy" exist
    And a teacher is registered under "Alpha School"
    When the teacher tries to access data belonging to "Beta Academy"
    Then the teacher should be denied access

  Scenario: Teacher cannot access another teacher's data in a different tenant
    Given two teachers "John" and "Jane" are registered under different organizations
    When "John" tries to access data belonging to "Jane"
    Then "John" should be denied access