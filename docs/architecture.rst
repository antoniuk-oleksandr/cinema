Architecture
============

The application follows a layered architecture:

* API/controller layer: HTTP transport, authentication context, and response mapping.
* Service layer: application use cases and transaction boundaries.
* Repository layer: persistence access through Django ORM.
* DTOs: external request and response contracts.
* Entities: domain state and behavior.
* Mappers: conversion between domain objects and transport DTOs.

Repositories and services must not depend on HTTP status codes. Domain errors
are translated to RFC 7807 responses by the centralized transport exception
handler.
