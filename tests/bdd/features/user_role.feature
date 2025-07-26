Feature: User Role Assignment and Access

  Scenario: Organization admin has admin privileges
    Given an organization admin account exists
    When the admin logs in
    Then the admin should have access to the admin dashboard

  Scenario: Teacher has teacher privileges
    Given a teacher account exists
    When the teacher logs in
    Then the teacher should have access to the teacher dashboard

  Scenario: Teacher cannot access admin-only endpoints
    Given a teacher account exists
    When the teacher tries to access an admin-only endpoint
    Then the teacher should be denied access

  Scenario: Admin cannot access teacher-only endpoints
    Given an organization admin account exists
    When the admin tries to access a teacher-only endpoint
    Then the admin should be denied access