"""Preparation design from actual assessed requirements, with unknown effort explicit."""
from .store import AppError, uid


def preview(services, profile, role_id):
    role = next((r for r in services.roles if r["role_id"] == role_id), None)
    if role is None or services.personal is None:
        raise AppError("role_requirements_unavailable", 404)
    context = services.career_context(profile, expected_profile_version=profile["version"],
                                      selected_role_ids=[role_id])
    assessments = context["recommendation"]["internal"]["personal_assessments"]
    assessment = next((a for a in assessments if a["role_id"] == role_id), None)
    if assessment is None:
        raise AppError("role_assessment_unavailable", 404)
    relevant = [g for g in assessment["gaps"] if g["state"] in ("unknown", "gap")]
    tasks, annotations, prior = [], [], None
    for gap in relevant[:6]:
        task_id = uid()
        tasks.append(dict(task_id=task_id, state="proposed", activity_completion=False,
            mastery_verified=False, prerequisite_task_ids=[prior] if prior else [], locked=False,
            scheduled_at=None, estimated_hours=None, evidence_ids=gap["evidence_ids"]))
        annotations.append(dict(task_id=task_id, criterion_id=gap["criterion_id"],
            assessment_state=gap["state"], description=("Review and document evidence for " + gap["criterion_id"]
                if gap["state"] == "unknown" else "Design a practice exercise for " + gap["criterion_id"]),
            basis=gap["reason"], authorship="Minder designed activity; not an employer requirement",
            resources=[], resource_status="not_verified", effort_assumption="unknown; user input required"))
        prior = task_id
    plan = dict(plan_id=uid(), profile_id=profile["profile_id"], selected_role_id=role_id,
        state_version=uid(), previous_version=None, task_ids=[t["task_id"] for t in tasks],
        tasks=tasks, progress_event_ids=[], constraints=profile["constraints"])
    from .resources import learning_options
    return dict(plan=plan, design=dict(profile_version=profile["version"], role_version=role["version"],
        policy_version=assessment["policy_version"], activities=annotations, source=role["source"],
        resource_options=learning_options()["resources"], selected_resources=[],
        truncated_requirements=len(relevant) > 6, total_unresolved_requirements=len(relevant),
        limitation="At most six evidence-review activities; effort/resources and capability remain unknown. "
                   "This is a preparation design, not a scored fit or feasibility claim."),
        saved=False, requires_explicit_selection=True)
