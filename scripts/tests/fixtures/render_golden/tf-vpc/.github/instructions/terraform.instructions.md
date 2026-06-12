---
applyTo: "**/*.tf,**/*.tfvars"
---
# GENERATED — edit in team-os/harness-layer/

# Terraform rules (Harness platform)

1. **Impact before interface.** Before changing any variable, output, or
   resource another repo consumes, run `pk impact <this-repo>` and check the
   downstream list. The terraform chain (data → integration → eks/lambda →
   route53) is order-sensitive.
2. **Follow the team convention node** once it lands:
   `pk show conventions/terraform-patterns`.
   TODO(verify): node pending (team-os T2.3) — until then, match the patterns
   already present in this repo rather than introducing new ones.
3. **Cross-repo terraform changes follow a workflow node.** Find it with
   `pk workflow terraform` / `pk workflow upgrade`; its ordered `repos:` list
   is the apply order.
4. TODO(verify): per-repo plan/apply pipeline commands (to be filled from
   repo surveys — do not guess; read this repo's CI config).
