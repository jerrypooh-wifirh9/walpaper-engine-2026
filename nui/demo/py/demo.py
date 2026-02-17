"""
Advanced Console Task Manager
Pure Python 3
"""

import json
import os
import datetime
import uuid
from typing import List, Dict


DATA_FILE = "tasks_data.json"


# ===============================
# Utility Functions
# ===============================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_id():
    return str(uuid.uuid4())[:8]


# ===============================
# Data Layer
# ===============================

class Storage:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = {
            "tasks": [],
            "stats": {
                "created": 0,
                "completed": 0
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                print("⚠ Error loading data file. Using empty storage.")

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def get_tasks(self) -> List[Dict]:
        return self.data["tasks"]

    def add_task(self, task: Dict):
        self.data["tasks"].append(task)
        self.data["stats"]["created"] += 1
        self.save()

    def update_task(self, task_id: str, updates: Dict):
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task.update(updates)
                self.save()
                return True
        return False

    def delete_task(self, task_id: str):
        original_len = len(self.data["tasks"])
        self.data["tasks"] = [
            t for t in self.data["tasks"] if t["id"] != task_id
        ]
        if len(self.data["tasks"]) != original_len:
            self.save()
            return True
        return False

    def increment_completed(self):
        self.data["stats"]["completed"] += 1
        self.save()

    def get_stats(self):
        return self.data["stats"]


# ===============================
# Task Manager Logic
# ===============================

class TaskManager:
    def __init__(self, storage: Storage):
        self.storage = storage

    def create_task(self):
        print("=== Create New Task ===")
        title = input("Title: ").strip()
        description = input("Description: ").strip()
        priority = input("Priority (low/medium/high): ").strip().lower()

        if priority not in ["low", "medium", "high"]:
            priority = "medium"

        task = {
            "id": generate_id(),
            "title": title,
            "description": description,
            "priority": priority,
            "created_at": now(),
            "completed": False
        }

        self.storage.add_task(task)
        print("✅ Task created successfully.")

    def list_tasks(self, show_all=True):
        tasks = self.storage.get_tasks()

        if not tasks:
            print("No tasks available.")
            return

        print(f"\n{'ID':<10}{'Title':<20}{'Priority':<10}{'Status':<10}")
        print("-" * 55)

        for task in tasks:
            if not show_all and task["completed"]:
                continue

            status = "Done" if task["completed"] else "Active"
            print(
                f"{task['id']:<10}"
                f"{task['title'][:18]:<20}"
                f"{task['priority']:<10}"
                f"{status:<10}"
            )

    def complete_task(self):
        task_id = input("Enter task ID to complete: ").strip()
        success = self.storage.update_task(
            task_id,
            {"completed": True}
        )
        if success:
            self.storage.increment_completed()
            print("🎉 Task marked as completed.")
        else:
            print("❌ Task not found.")

    def delete_task(self):
        task_id = input("Enter task ID to delete: ").strip()
        if self.storage.delete_task(task_id):
            print("🗑 Task deleted.")
        else:
            print("❌ Task not found.")

    def search_tasks(self):
        keyword = input("Search keyword: ").strip().lower()
        tasks = self.storage.get_tasks()

        results = [
            t for t in tasks
            if keyword in t["title"].lower()
            or keyword in t["description"].lower()
        ]

        if not results:
            print("No matching tasks found.")
            return

        print("\nSearch Results:")
        for task in results:
            print(
                f"[{task['id']}] "
                f"{task['title']} "
                f"(Priority: {task['priority']})"
            )

    def show_stats(self):
        stats = self.storage.get_stats()
        total = len(self.storage.get_tasks())
        completed = stats["completed"]
        created = stats["created"]

        print("\n=== Statistics ===")
        print(f"Total tasks: {total}")
        print(f"Tasks created: {created}")
        print(f"Tasks completed: {completed}")
        if created > 0:
            rate = (completed / created) * 100
            print(f"Completion rate: {rate:.2f}%")
        else:
            print("Completion rate: 0%")

    def export_tasks(self):
        filename = f"tasks_export_{datetime.date.today()}.txt"
        tasks = self.storage.get_tasks()

        with open(filename, "w", encoding="utf-8") as f:
            for task in tasks:
                f.write(f"ID: {task['id']}\n")
                f.write(f"Title: {task['title']}\n")
                f.write(f"Description: {task['description']}\n")
                f.write(f"Priority: {task['priority']}\n")
                f.write(f"Created: {task['created_at']}\n")
                f.write(f"Completed: {task['completed']}\n")
                f.write("-" * 40 + "\n")

        print(f"📁 Tasks exported to {filename}")


# ===============================
# CLI Interface
# ===============================

def main_menu():
    print("\n=== Advanced Task Manager ===")
    print("1. Create Task")
    print("2. List All Tasks")
    print("3. List Active Tasks")
    print("4. Complete Task")
    print("5. Delete Task")
    print("6. Search Tasks")
    print("7. Statistics")
    print("8. Export Tasks")
    print("0. Exit")


def main():
    storage = Storage(DATA_FILE)
    manager = TaskManager(storage)

    while True:
        main_menu()
        choice = input("Select option: ").strip()

        clear_screen()

        if choice == "1":
            manager.create_task()
        elif choice == "2":
            manager.list_tasks(show_all=True)
        elif choice == "3":
            manager.list_tasks(show_all=False)
        elif choice == "4":
            manager.complete_task()
        elif choice == "5":
            manager.delete_task()
        elif choice == "6":
            manager.search_tasks()
        elif choice == "7":
            manager.show_stats()
        elif choice == "8":
            manager.export_tasks()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

        input("\nPress Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    main()
