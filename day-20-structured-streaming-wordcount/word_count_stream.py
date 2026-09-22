from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

spark = SparkSession.builder.appName("Day20WordCount").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

lines = (
    spark.readStream.format("socket")
    .option("host", "localhost")
    .option("port", 9999)
    .load()
)

words = lines.select(explode(split(lines.value, "\\s+")).alias("word"))

# Running word counts held in a plain Python dict, updated per micro-batch.
# This deliberately sidesteps Spark's built-in stateful groupBy().count()
# operator, whose checkpoint-based state store hit a real Windows-specific
# file permission/interrupt issue during commit (see README for the root
# cause). foreachBatch + manual accumulation gets the same result without
# needing that internal state store at all.
running_counts = {}


def process_batch(batch_df, batch_id):
    rows = batch_df.collect()
    if not rows:
        print(f"--- Batch {batch_id}: no new words ---")
        return
    for row in rows:
        word = row["word"]
        running_counts[word] = running_counts.get(word, 0) + 1
    print(f"--- Batch {batch_id}: {len(rows)} new word(s) ---")
    for word, count in sorted(running_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {word}: {count}")


query = words.writeStream.foreachBatch(process_batch).start()

query.awaitTermination(timeout=25)
query.stop()
print("\nStreaming query stopped after timeout.")
print(f"Final word counts: {running_counts}")
