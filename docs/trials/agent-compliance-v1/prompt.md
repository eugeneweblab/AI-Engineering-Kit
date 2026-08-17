Inspect the fixture under `eval/` and fix the three reported production incidents.
Change only its workflow, Redis lock helper, and SQL migration. Do not install packages.

1. A CI security review found that the workflow can change underneath us, grants an
   implicit token scope, wastes runners after a replacement push, and can run forever.
2. Worker A sometimes finishes after its Redis lease expires. Worker B then acquires
   the same key, after which A's cleanup makes the key disappear.
3. Deploying the new required `orders.status` column to a very large, write-heavy
   PostgreSQL 16 table must not create a long blocking validation or leave the column
   nullable. Existing rows should read as `pending`.

Inspect repository guidance if present, implement the fixes, and run only offline checks.
