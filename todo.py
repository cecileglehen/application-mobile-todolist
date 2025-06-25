
import json
import os
import argparse

TASKS_FILE = 'tasks.json'


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def list_tasks(args):
    tasks = load_tasks()
    if not tasks:
        print('Aucune tâche.')
        return
    for idx, task in enumerate(tasks, 1):
        status = '✓' if task.get('done') else ' '
        print(f"{idx}. [{status}] {task.get('title')}")


def add_task(args):
    tasks = load_tasks()
    tasks.append({'title': args.title, 'done': False})
    save_tasks(tasks)
    print(f"Tâche ajoutée: {args.title}")


def mark_done(args):
    tasks = load_tasks()
    idx = args.index - 1
    if 0 <= idx < len(tasks):
        tasks[idx]['done'] = True
        save_tasks(tasks)
        print(f"Tâche terminée: {tasks[idx]['title']}")
    else:
        print('Index de tâche invalide.')


def remove_task(args):
    tasks = load_tasks()
    idx = args.index - 1
    if 0 <= idx < len(tasks):
        removed = tasks.pop(idx)
        save_tasks(tasks)
        print(f"Tâche supprimée: {removed['title']}")
    else:
        print('Index de tâche invalide.')


def main():
    parser = argparse.ArgumentParser(description='Gestionnaire de todo list basique.')
    subparsers = parser.add_subparsers(dest='command')

    parser_list = subparsers.add_parser('list', help='Lister toutes les tâches')
    parser_list.set_defaults(func=list_tasks)

    parser_add = subparsers.add_parser('add', help='Ajouter une nouvelle tâche')
    parser_add.add_argument('title', help='Titre de la tâche')
    parser_add.set_defaults(func=add_task)

    parser_done = subparsers.add_parser('done', help='Marquer une tâche comme terminée')
    parser_done.add_argument('index', type=int, help="Index de la tâche (à partir de 1)")
    parser_done.set_defaults(func=mark_done)

    parser_remove = subparsers.add_parser('remove', help='Supprimer une tâche')
    parser_remove.add_argument('index', type=int, help="Index de la tâche (à partir de 1)")
    parser_remove.set_defaults(func=remove_task)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
