import asyncio

from auto_teacher_process.run_worker.services import run_add_new_paper_match


def main():
    print("Hello from auto-teacher-process!")
    asyncio.run(run_add_new_paper_match.main())


if __name__ == "__main__":
    main()
