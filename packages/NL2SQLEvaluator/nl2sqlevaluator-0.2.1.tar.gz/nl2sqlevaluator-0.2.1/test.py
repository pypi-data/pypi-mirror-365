import datasets

from NL2SQLEvaluator.db_executor import SqliteDBExecutor

db_executor = {}


def get_info(db_id, tbl_names, strat, base_path):
    if db_id not in db_executor:
        db_executor[db_id] = SqliteDBExecutor.from_uri(
            relative_base_path=f'{base_path}/{db_id}/{db_id}.sqlite',
        )
    executor = db_executor[db_id]
    info = executor.get_table_info(tbl_names, strat)
    return info


dataset = datasets.load_dataset("simone-papicchio/bird")


dataset["train"] = dataset["train"].map(
    lambda line: {
        'db_schema': get_info(
            line['db_id'],
            tbl_names=None,
            strat=None,
            base_path="data/bird/bird_train/train_databases"
        ),
        'db_schema_examples': get_info(
            line['db_id'],
            tbl_names=None,
            strat="inline",
            base_path="data/bird/bird_train/train_databases"
        ),
        'db_schema_T': get_info(
            line['db_id'],
            tbl_names=line["table_in_sql"],
            strat=None,
            base_path="data/bird/bird_train/train_databases"
        ),
        'db_schema_T_examples': get_info(
            line['db_id'],
            tbl_names=line["table_in_sql"],
            strat="inline",
            base_path="data/bird/bird_train/train_databases"
        )
    },
    load_from_cache_file=False
)
db_executor = {}
dataset["dev"] = dataset["dev"].map(
    lambda line: {
        'db_schema': get_info(
            line['db_id'],
            tbl_names=None,
            strat=None,
            base_path="data/bird_dev/dev_databases"
        ),
        'db_schema_examples': get_info(
            line['db_id'],
            tbl_names=None,
            strat="inline",
            base_path="data/bird_dev/dev_databases"
        ),
        'db_schema_T': get_info(
            line['db_id'],
            tbl_names=line["table_in_sql"],
            strat=None,
            base_path="data/bird_dev/dev_databases"
        ),
        'db_schema_T_examples': get_info(
            line['db_id'],
            tbl_names=line["table_in_sql"],
            strat="inline",
            base_path="data/bird_dev/dev_databases"
        )
    },
    load_from_cache_file=False
)
db_executor = {}
dataset["minidev"] = dataset["minidev"].map(
    lambda line: {
        'db_schema': get_info(
            line['db_id'],
            tbl_names=None,
            strat=None,
            base_path="data/bird_dev/dev_databases"
        ),
        'db_schema_examples': get_info(
            line['db_id'],
            tbl_names=None,
            strat="inline",
            base_path="data/bird_dev/dev_databases"
        ),
        'db_schema_T': get_info(
            line['db_id'],
            tbl_names=line["table_in_sql"],
            strat=None,
            base_path="data/bird_dev/dev_databases"
        ),
        'db_schema_T_examples': get_info(
            line['db_id'],
            tbl_names=line["table_in_sql"],
            strat="inline",
            base_path="data/bird_dev/dev_databases"
        )
    },
    load_from_cache_file=False
)

dataset.push_to_hub("simone-papicchio/bird", token='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')

if __name__ == "__main__":
    print()
    # This will print the table information for the airline database
