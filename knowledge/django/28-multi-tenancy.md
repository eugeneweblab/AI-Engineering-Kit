---
id: django/28-multi-tenancy
topic: django
slug: multi-tenancy
title: "Django Multi-Tenancy"
type: doc
order: 28
status: ready
maturity: unverified
tags: [django, multi-tenancy, tenant, schema, filter]
related: [django/06-security, django/05-querysets-and-transactions]
when_to_use: "Read when scoping rows or schemas per tenant, customer, or organization."
---
# Django Multi-Tenancy

## Purpose

Defines how one Django deployment isolates tenant data.

## Rules

- Pick one isolation model (row-level `tenant_id`, schema-per-tenant, or database-per-tenant) and stay with the project's choice.
- Apply tenant filters in QuerySets, managers, or middleware that the ORM cannot skip; never only in templates.
- Every write must set the tenant key explicitly; do not infer it from a global if tests can forget to set it.
- Cross-tenant staff access must be an explicit permission, not a missing filter.
- Test a second tenant's 404/403 on every new object view.

## Good Example

```python
class InvoiceQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.for_tenant(request.tenant), pk=pk
    )
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

Lookup cannot return another tenant's row.

## Bad Example

```python
def invoice_detail(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

Primary key access across tenants is an IDOR.

## Checklist

- [ ] Tenant scoping is in the queryset, not only the template
- [ ] Writes set the tenant key
- [ ] A second-tenant test fails closed (403/404)

## Related

- `django/06-security`
- `django/05-querysets-and-transactions`
