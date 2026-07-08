---
id: react/15-forms
topic: react
slug: forms
title: "React Forms"
type: doc
order: 15
status: ready
tags: [react, forms]
related: []
when_to_use: "Read before building or reviewing React forms, inputs, and validation."
---
# React Forms

## Purpose

This document defines the engineering standards for building forms in React applications.

The objective is to create forms that are predictable, accessible, maintainable, performant, and easy to validate.

Forms are one of the most complex parts of frontend applications and should follow consistent architectural patterns.

---

## Core Principle

Forms collect data.

Business logic validates data.

UI presents data.

Keep these responsibilities separate.

---

## Form Workflow

Every form should follow this lifecycle.

```
Render Form
        ↓
Initialize Values
        ↓
User Input
        ↓
Validation
        ↓
Submission
        ↓
Response Handling
        ↓
Success / Error
```

---

## Form Architecture

Every form should clearly separate:

- UI;
- validation;
- business logic;
- API communication.

Avoid mixing all responsibilities inside a single component.

---

## Controlled Components

Prefer controlled inputs for most forms.

Example:

```tsx
<input
    value={email}
    onChange={handleEmailChange}
/>
```

Controlled components provide predictable behavior and simplify validation.

---

## Uncontrolled Components

Use uncontrolled inputs only when appropriate.

Examples:

- file uploads;
- simple uncontrolled forms;
- third-party integrations.

Do not choose uncontrolled components only to reduce code.

---

## Form Libraries

For medium and large applications, prefer a dedicated form library.

Recommended:

- React Hook Form

Validation libraries:

- Zod
- Yup
- Valibot

Avoid implementing complex form state management manually unless required.

---

## Validation

Validation should exist at multiple levels.

Examples:

- required fields;
- format validation;
- business rules;
- server validation.

Client-side validation improves UX.

Server-side validation remains mandatory.

---

## Validation Strategy

Validate:

- on submit;
- on blur;
- on change only when appropriate.

Avoid validating every keystroke unless necessary.

---

## Error Messages

Every validation error should:

- explain the problem;
- explain how to fix it;
- appear near the relevant field.

Avoid generic messages such as:

```
Invalid input.
```

Prefer:

```
Email address must be valid.
```

---

## Default Values

Initialize every field explicitly.

Avoid undefined form values.

Provide sensible defaults whenever possible.

---

## Submission State

Every form should expose explicit submission states.

Examples:

- idle;
- submitting;
- success;
- error.

Users should always understand the current status.

---

## Loading State

During submission:

- disable duplicate submissions;
- display progress;
- preserve entered data.

Avoid blocking the entire page unnecessarily.

---

## API Integration

Keep API communication outside presentation whenever practical.

Good separation:

```
Form

↓

Validation

↓

Submit Handler

↓

API Client
```

Business logic should not be tightly coupled to form rendering.

---

## Reset Behavior

Define when forms should reset.

Examples:

- after successful submission;
- after user confirmation;
- after explicit reset.

Do not clear user input after failed submissions.

---

## Accessibility

Every form should provide:

- associated labels;
- keyboard accessibility;
- visible focus indicators;
- descriptive error messages;
- required field indicators;
- accessible validation feedback.

Never rely only on placeholders.

---

## Performance

Review:

- unnecessary re-renders;
- expensive validation;
- duplicated state;
- large controlled forms.

Optimize only after profiling.

---

## Security

Never trust client-side validation.

Always validate:

- on the server;
- before persistence;
- before authorization decisions.

Client validation improves usability.

Server validation ensures security.

---

## AI Execution Checklist

## Investigation

☐ Form requirements understood.

☐ Validation requirements identified.

☐ Submission flow reviewed.

☐ Accessibility requirements reviewed.

---

## Planning

☐ Select validation strategy.

☐ Define default values.

☐ Define submission states.

☐ Separate business logic.

---

## Verification

☐ Validation implemented.

☐ Errors are understandable.

☐ Accessibility preserved.

☐ Submission state handled correctly.

☐ Duplicate submissions prevented.

☐ Server validation supported.

---

## Common Mistakes

Avoid:

Mixing validation with rendering.

Trusting client validation.

Using placeholders as labels.

Resetting forms after failed submissions.

Performing expensive validation on every keystroke.

Duplicating form state.

Ignoring accessibility.

---

## Completion Criteria

A React form is complete when:

- validation is implemented;
- submission states are explicit;
- accessibility requirements are satisfied;
- business logic is separated from presentation;
- server validation is supported;
- error handling is clear;
- the user experience remains predictable.

---

## Summary

Well-designed forms balance usability, accessibility, performance, and security.

By separating presentation, validation, and business logic, React forms become easier to maintain, easier to test, and more resilient as application requirements evolve.