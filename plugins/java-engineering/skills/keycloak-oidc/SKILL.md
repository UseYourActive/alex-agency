---
name: keycloak-oidc
description: >
  Keycloak and OIDC integration patterns: realm/client modeling, roles vs scopes,
  token claims, Quarkus OIDC and Spring resource-server config, service accounts,
  multi-tenant realm provisioning. Use when the task involves Keycloak, OAuth2/OIDC
  login, JWT validation, or securing REST endpoints with bearer tokens. Not for
  basic-auth, API keys, or non-Keycloak identity providers.
---

# Keycloak / OIDC Patterns

## Realm & client modeling

- One realm per tenant/product environment boundary; never mix tenants in one realm.
- Clients: `confidential` for backend services (secret, service accounts),
  `public` for SPAs/mobile (PKCE mandatory, no secret). One client per application,
  not per environment — environments differ by realm/URL, not client sprawl.
- Backend-to-backend auth: client credentials grant via a service account,
  never a password-grant "technical user".

## Roles vs scopes vs groups (the part everyone confuses)

- Realm roles: coarse, business-level (`admin`, `operator`). Client roles:
  app-specific permissions. Groups: org structure that MAPS to roles — code never
  checks groups directly.
- Client scopes control what CLAIMS enter the token, not what the user may do.
  Keep tokens small: default scopes minimal, optional scopes on request.
- Authorization decisions in services use roles/claims from the validated token,
  never a live Keycloak API call per request.

## Token & claims

- Standard claims first (`sub`, `preferred_username`, `email`); custom claims via
  protocol mappers, namespaced (`https://<domain>/tenant_id`), documented in the
  realm export.
- Access token lifetime short (≤5–15 min); refresh handled by the client/gateway.
  Services validate `iss`, `aud`, expiry, signature — audience checking is NOT
  optional; set a distinct audience per API via an audience mapper.

## Service config snippets

Quarkus (service = resource server):
```
quarkus.oidc.auth-server-url=${OIDC_AUTH_SERVER_URL}   # .../realms/<realm>
quarkus.oidc.client-id=${OIDC_CLIENT_ID}
quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}
quarkus.oidc.token.audience=${OIDC_AUDIENCE}
```
Endpoint guards: `@RolesAllowed("operator")`; identity via `SecurityIdentity`.

Spring Boot (resource server):
```
spring.security.oauth2.resourceserver.jwt.issuer-uri=${OIDC_ISSUER_URI}
```
`SecurityFilterChain` with `.oauth2ResourceServer(o -> o.jwt(...))`; map realm
roles from `realm_access.roles` claim with a converter — Spring does NOT do this
automatically.

## Provisioning & environments

- Realm config as code: JSON export in the repo, imported at startup in dev
  (`--import-realm` on the Keycloak dev container) and applied via admin API
  scripts/Terraform in prod. Never click-configure prod.
- Multi-tenant provisioning (realm-forge pattern): idempotent "ensure" operations
  (create realm/client/roles if absent) driven by a declarative spec; store only
  the client secret OUTPUT in the secret manager, never in the spec.
- Local dev: Keycloak in docker-compose with realm import; tests use a
  Testcontainers Keycloak or mocked JWT with the same claims shape — never
  disable security in tests.

## Checklist for any secured endpoint

1. Audience validated, not just issuer.
2. Role/claim check at the endpoint or a central policy — not sprinkled in services.
3. 401 for missing/invalid token, 403 for valid-but-forbidden. Never 404-masking
   unless the resource existence itself is sensitive.
4. Tokens never logged, never in URLs.
