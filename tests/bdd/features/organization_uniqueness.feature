Feature: Organization Name Uniqueness

  Scenario: Prevent duplicate organization names
    Given an organization named "Acme School" already exists
    When I try to sign up another organization with the name "Acme School"
    Then I should see an error about duplicate organization name

  Scenario: Allow unique organization names
    Given an organization named "Acme School" already exists
    When I sign up another organization with the name "Beta Academy"
    Then