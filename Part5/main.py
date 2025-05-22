import csv
from itertools import chain
from io import StringIO
import pymongo
import dask.bag as db
import sys

def extract_from_api():
    """
    Simulate extraction from an API.
    """
    print("Extracting data from API...")
    # For demonstration, we return hardcoded API data.
    api_data = [
        {"name": "apple iPhone 12", "price": "699.99", "category": "Electronics"},
        {"name": "samsung Galaxy S21", "price": "799.99", "category": "Electronics"}
    ]
    # Use python generator to yield records one by one
    # This is useful for large datasets to avoid memory issues.
    for record in api_data:
        yield record


def extract_from_csv(csv_file_path="products.csv"):
    """
    Extract product data from a CSV file.
    """
    print("Extracting data from CSV...")
    try:
        with open(csv_file_path, "r", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
    except Exception as e:
        print(f"Error reading {csv_file_path}: {e}. Using sample CSV data.")
        sample_csv = """name,price,category
            Dell Laptop,899.99,Electronics
            HP Printer,199.99,Electronics
            """
        f = StringIO(sample_csv)
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def extract_from_db_simulation():
    """
    Simulate extraction from a database.
    """
    print("Extracting data from simulated database...")
    db_data = [
        {"name": "sony headphones", "price": "149.99", "category": "Accessories"},
        {"name": "bose speakers", "price": "399.99", "category": "Accessories"},
        {"name": "apple iPhone 12", "price": "699.99", "category": "Electronics"},
        {"name": "samsung Galaxy S21", "price": "799.99", "category": "Electronics", "subcategory": "Phone"},
    ]

    # Uncomment to raise an exception to simulate a database error
    # raise Exception("Simulated database error")

    for record in db_data:
        yield record

def safe_extract(gen_func, *args, **kwargs):
    """
    Wrap an extraction function and catch any exceptions.
    If an exception is raised, log the error and yield nothing.
    """
    try:
        # Yield each record from the generator function.
        yield from gen_func(*args, **kwargs)
    except Exception as e:
        print(f"Error in {gen_func.__name__}: {e}. Continuing with remaining sources.")

def extract_all():
    """
    Extract data from all sources and combine the results into a single list.
    """
    return chain(
        safe_extract(extract_from_api),
        safe_extract(extract_from_csv),
        safe_extract(extract_from_db_simulation)
    )

def transform(record):
    """
    Apply simple transformation logic on a record:
      - Strip whitespace from strings.
      - Standardize product names to title case.
      - Convert price to a float (defaulting to 0.0 on error).
      - Normalize category to lower case.
    """
    try:
        transformed = {}
        transformed["name"] = record.get("name", "").strip().title()
        transformed["price"] = float(record.get("price", 0))
        transformed["category"] = record.get("category", "").strip().lower()
        # Handle subcategory if it exists
        if "subcategory" in record and record["subcategory"]:
            transformed["subcategory"] = record.get("subcategory", "").strip().lower()
        else:
            transformed["subcategory"] = None  # Default to None if not present
        return transformed
    except Exception as e:
        print(f"Error transforming record {record}: {e}")
        return None


def transform_all(records):
    """
    Generator that applies the transformation to each record.
    """
    for rec in records:
        trans = transform(rec)
        if trans is not None:
            yield trans

def dedup_key(record):
    """
    Define a key used for deduplication.
    Here, deduplication is based on (name, category).
    """
    key = (record["name"], record["category"])
    return key

def merge_records(acc, record):
    """
    Merge two records with the same deduplication key.
    For example purposes, we choose the record with the lower price.
    """
    if acc is None:
        return record
    # Choose the record with the lower price.
    return_model = acc if acc["price"] <= record["price"] else record

    # If the new record has extra fields, merge into the existing record.
    if "subcategory" not in return_model or not return_model["subcategory"]:
        # If the new record has a subcategory, and it is not empty string, add it to the accumulator.
        if "subcategory" in record and record["subcategory"]:
            return_model["subcategory"] = record["subcategory"]

    return return_model


def deduplicate_records(records):
    """
    Deduplicate records using Dask Bag's foldby.
    """
    print("Deduplicating records using Dask...")
    # Create a Dask Bag from our sequence.
    bag = db.from_sequence(records, npartitions=4)
    # foldby groups records by the deduplication key and applies the merge function.
    deduped = bag.foldby(
        key=dedup_key,
        binop=merge_records,
        initial=None  # The initial value is None so that merge_records returns the record.
    ).map(lambda t: t[1])
    return deduped.compute()

def is_equal(existing_doc, record):
    """
    Compare an existing document with a new record.
    For now, considers the record equal if 'price' differs by less than 0.001.
    It is better to calculate hash of the record and compare it with the existing document.
    """
    # Assume that name and category are the same because they’re used as a key
    if abs(existing_doc.get("price", 0) - record.get("price", 0)) > 0.001:
        return False
    return True

def load_to_mongodb(records,
                    mongodb_url="mongodb://localhost:27017",
                    db_name="ecommerceetl",
                    collection_name="products",
                    full_refresh=False):
    """
    Load the deduplicated records into MongoDB.
    """
    print("Loading data into MongoDB...")
    client = pymongo.MongoClient(mongodb_url)
    db = client[db_name]
    collection = db[collection_name]

    if full_refresh:
        print("Performing full refresh: Dropping existing collection.")
        collection.drop()
    
    # Build a dictionary of existing products keyed by (name, category)
    existing_products = {}
    for doc in collection.find({}):
        key = (doc['name'], doc['category'])
        existing_products[key] = doc

    operations = []
    for record in records:
        key = (record["name"], record["category"])
        if key in existing_products:
            # If the record exists but is different, add an update operation.
            if not is_equal(existing_products[key], record):
                operations.append(
                    pymongo.UpdateOne(
                        {"name": record["name"], "category": record["category"]},
                        {"$set": record}
                    )
                )
            # Else: No change, so skip.
        else:
            operations.append(pymongo.InsertOne(record))
    
    if operations:
        result = collection.bulk_write(operations, ordered=False)
        print(f"Bulk write result: {result.bulk_api_result}")
    else:
        print("No changes detected; skipping updates/inserts.")
    
    client.close()


def run_etl(full_refresh=False):
    """
    Runs the complete ETL pipeline:
      1. Extract from multiple sources.
      2. Transform the extracted data.
      3. Deduplicates records.
      4. Load the final data into MongoDB.
    """
    print("Starting ETL process...")

    # Extract
    records_gen = extract_all()
    
    # Transform
    transformed_gen = transform_all(records_gen)

    transformed_records = list(transformed_gen)
    print(f"Total transformed records: {len(transformed_records)}")

    deduped_records = deduplicate_records(transformed_records)
    print(f"Total deduplicated records: {len(deduped_records)}")
    
    # Load
    load_to_mongodb(deduped_records, full_refresh=full_refresh)
    print("ETL process completed successfully.")

def main():
    # Check if the script is run with a full refresh flag
    full_refresh = "--full-refresh" in sys.argv
    run_etl(full_refresh=full_refresh)


if __name__ == "__main__":
    main()
