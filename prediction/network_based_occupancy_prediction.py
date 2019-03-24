import pandas as pd
from sklearn.metrics import mean_squared_error, make_scorer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeRegressor
from collections import Counter
from models.aggregate_log import AggregateLog
import sys
import numpy
numpy.set_printoptions(threshold=sys.maxsize)

import models.util as util
db = util.get_db()


def row_gen(queries, hosts, agg_log):
    # Translate this agg_log
    logged_hosts = agg_log.hosts
    logged_queries = agg_log.dns_queries

    aggregate_columns = Counter(queries)
    aggregate_columns.update(hosts)
    aggregate_columns.update(logged_hosts)
    aggregate_columns.update(logged_queries)

    aggregate_columns = add_default_data(aggregate_columns, agg_log)

    return aggregate_columns

def add_default_data(d, agg_log):
    d["occupied"] = agg_log.occupied

    # aggregate_columns["from_time"] = agg_log.from_time
    # aggregate_columns["to_time"] = agg_log.to_time
    d["day_of_month"] = agg_log.day_of_month
    d["day_of_week"] = agg_log.day_of_week
    d["hour_of_day"] = agg_log.hour_of_day
    d["minute_of_hour"] = agg_log.minute_of_hour
    d["total_dns_queries"] = agg_log.total_dns_queries
    d["total_hosts"] = agg_log.total_hosts
    return d

def row_gen_host_only(hosts, agg_log):
    # Translate this agg_log
    logged_hosts = agg_log.hosts

    aggregate_columns = Counter(hosts)
    aggregate_columns.update(logged_hosts)

    return add_default_data(aggregate_columns, agg_log)


def row_gen_dns_only(queries, agg_log):
    # Translate this agg_log
    logged_queries = agg_log.dns_queries

    aggregate_columns = Counter(queries)
    aggregate_columns.update(logged_queries)

    return add_default_data(aggregate_columns, agg_log)


def to_dict(l):
    d = {}
    for item in l:
        d[item[0]] = 0

    return d

def get_all_hosts_queries():
    all_distinct_hosts = db.engine.execute("""
            select distinct json_object_keys(aggregate_log.hosts) as host
            from aggregate_log
            """)
    hosts = to_dict(all_distinct_hosts)

    all_distinct_queries = db.engine.execute("""
            select distinct json_object_keys(aggregate_log.dns_queries) as query
            from aggregate_log
          """)
    queries = to_dict(all_distinct_queries)

    return hosts, queries

def perform_cross_validation(model, data, target, cv=10):
    output = cross_val_score(model, data, target, cv=cv, scoring=make_scorer(mean_squared_error))
    print(output.round(decimals=4))
    print("Average error for all runs: " + str(numpy.average(output)))

def evaluate_dataset(data):
    df = pd.DataFrame(data=data)
    ground_truth = df["occupied"]

    train_data = df.drop(columns=["occupied"])

    regr = DecisionTreeRegressor()
    print("depth = None")
    perform_cross_validation(regr, train_data, ground_truth)

    for i in range(2, 10):
        regr = DecisionTreeRegressor(max_depth=i)
        print("depth = " + str(i))
        perform_cross_validation(regr, train_data, ground_truth)

def main():
    hosts, queries = get_all_hosts_queries()
    logs = AggregateLog.query.order_by(AggregateLog.from_time.desc()).all()
    whole_rows = [ row_gen(queries, hosts, l) for l in logs ]

    # print("bubu")
    df = pd.DataFrame(data=whole_rows)
    # print(df.head(10))

    # Print Baseline
    baseline = 1 - (df.query("occupied < 1").shape[0] / df.shape[0])
    print("Baseline is " + str(baseline))

    # Separate predicted and data into two different frames
    print("Host only")
    evaluate_dataset([row_gen_host_only(hosts, l) for l in logs])
    print("DNS only")
    evaluate_dataset([row_gen_dns_only(queries, l) for l in logs])
    print("All Data")
    evaluate_dataset([row_gen(queries, hosts, l) for l in logs])

    # ground_truth = df["occupied"]
    #
    # train_data = df.drop(columns=["occupied"])
    #
    # for i in range(2, 10):
    #
    #     regr = DecisionTreeRegressor(max_depth=i)
    #     perform_cross_validation(regr, train_data, ground_truth)
    # regr.fit(train_data, ground_truth)
    # y_pred = regr.predict(train_data)
    # print(mean_squared_error(ground_truth, y_pred))
    #
    # y_pred = pd.DataFrame(y_pred)
    # print(y_pred)
    # Do cross val





if __name__ == "__main__":
    main()