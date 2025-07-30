from auto_teacher_process.mq.consumer_manager import start_multiple_consumers
from auto_teacher_process.run_worker.services import run_add_new_paper_match


def main():
    print("Hello from auto-teacher-process!")

    consumers = [
        run_add_new_paper_match.main,
        # run_add_new_paper_match.main,
    ]

    start_multiple_consumers(consumers, wait=True)


if __name__ == "__main__":
    main()
