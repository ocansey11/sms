Feature: User Login

  Scenario: Successful login as organization admin
    Given an organization admin account exists with email "admin@school.edu" and password "StrongPass123!"
    When I log in with email "admin@school.edu" and password "StrongPass123!"
    Then I should be redirected to the admin dashboard

  Scenario: Successful login as teacher
    Given a teacher account exists with email "teacher@school.com" and password "StrongPass123!"
    When I log in with email "teacher@school.com" and password "StrongPass123!"
    Then I should be redirected to the teacher dashboard

  Scenario: Login with incorrect password
    Given a teacher account exists with email "teacher@school.com" and password "StrongPass123!"
    When I log in with email "teacher@school.com" and password "WrongPassword"
    Then I should see an error about invalid credentials

  Scenario: Login with non-existent email
    When I log in with email "nonexistent@school.com" and password "StrongPass123!"
    Then I should see an error about invalid credentials