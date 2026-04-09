import frappe

@frappe.whitelist()
def delete_child_tasks_and_dependencies(task_ids):
    if isinstance(task_ids, str):
        import json
        task_ids = json.loads(task_ids)

    for task_id in task_ids:
        task = frappe.get_doc("Task", task_id)

        # If the task has a parent task
        if task.parent_task:
            parent = frappe.get_doc("Task", task.parent_task)

            # Rebuild depends_on child table excluding this child task
            new_depends_on = []
            for dep in parent.depends_on:
                if dep.task != task.name:
                    new_depends_on.append({
                        "task": dep.task,
                        "subject": dep.subject or "",
                        "project": dep.project or ""
                    })

            # Assign new child table
            parent.set("depends_on", new_depends_on)
            parent.save(ignore_permissions=True)
            frappe.db.commit()

        # Delete the child task itself
        frappe.delete_doc("Task", task.name, force=True, ignore_permissions=True)
        frappe.db.commit()

    return "✅ Child tasks and dependencies deleted successfully."
