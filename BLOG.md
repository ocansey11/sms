## Handling Circular Dependencies in SQLAlchemy Models

### The Problem

In multi-tenant SaaS systems, it's common for two tables to reference each other. For example, in our SMS backend:
- A `Tenant` (organization or solo teacher) must have an owner (`owner_user_id` referencing `User.id`).
- A `User` must belong to a tenant (`tenant_id` referencing `Tenant.id`).

This creates a **circular dependency**:  
- You can't create a `Tenant` without an owner `User`,  
- and you can't create a `User` without a `Tenant`.

### Why This Is a Problem

Relational databases require that a foreign key reference an existing primary key. If both foreign keys are non-nullable, you can't insert either record first without violating a constraint.

### Our Solution

1. **Make one foreign key nullable:**  
   We made `Tenant.owner_user_id` nullable at the database level. This allows us to create a tenant without an owner initially.

2. **Signup Flow (Three Steps):**
   - **Step 1:** Create the `Tenant` with `owner_user_id=None`.
   - **Step 2:** Create the `User` (owner/admin) with `tenant_id` set to the new tenant's ID.
   - **Step 3:** Update the `Tenant` to set `owner_user_id` to the new user's ID.

3. **Enforce Business Rules in Code:**  
   After creation, we enforce (in business logic) that every tenant must have an owner. This ensures data integrity even though the database allows a temporary null.

4. **Atomic Transactions:**  
   We use a single transaction for all three steps to avoid partial creation and ensure consistency.

### Why Not Just Make Both FKs Required?

If both foreign keys are non-nullable, you can't insert either record first. Making one nullable is a standard and safe way to break the cycle, as long as your application logic ensures the relationship is set immediately after creation.

### Summary

- Circular dependencies are common in multi-tenant systems.
- The solution is to make one FK nullable, create records in two steps, and enforce integrity in your business logic.
- This pattern keeps your database happy and your business rules intact.