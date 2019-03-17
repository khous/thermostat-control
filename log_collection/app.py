from log_collection.config import huey
from log_collection.tasks import get_active_hosts, get_dns_queries

if __name__ == "__main__":
    print("Running as standalone app")
    get_active_hosts()
    get_dns_queries()