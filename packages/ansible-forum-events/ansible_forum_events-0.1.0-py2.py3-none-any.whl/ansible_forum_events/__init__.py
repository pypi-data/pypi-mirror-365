"Prints out the upcoming Ansible Forum events from the forum API in markdown format."

__version__ = "0.1.0"

import sys
from datetime import datetime, timezone

import httpx


def main():
    "Main entry point"
    try:
        resp = httpx.get("https://forum.ansible.com/c/events/8/l/latest.json")
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Failed to fetch the forum data due to {e}")
        sys.exit(1)

    skip_list = [
        "about-the-events-category",
        "documentation-wg-weekly-meeting",
        "community-wg-weekly-meeting",
    ]
    # We need to find the list of topics
    topics = data.get("topic_list", {}).get("topics", [])
    result = []
    now = datetime.now(timezone.utc)
    for topic in topics:
        slug = topic.get("slug", "")
        title = topic.get("title", "")
        id = topic.get("id", 0)
        if topic.get("slug") in skip_list:
            print(f"Skipping {slug}")
            continue
        event_time = topic.get("event_starts_at")
        if not event_time:
            continue
        if event_time.endswith("Z"):
            datetime_string = event_time[:-1] + "+00:00"
            event_time_object = datetime.strptime(
                datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            if event_time_object > now:  # Means the event is in future
                line = f"[{title}](https://forum.ansible.com/t/{slug}/{id})"
                result.append(line)

    # Now print the result
    print("\n\n")
    for line in result:
        print(line)


if __name__ == "__main__":
    main()
