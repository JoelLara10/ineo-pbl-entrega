"""Real PySpark computations on projected, identifier-free source rows."""
import json
import os
import sys


def analyze(spark, kind, rows):
    from pyspark.sql import functions as F
    from pyspark.sql.types import StructType, StructField, DoubleType, StringType

    result = {'available': False, 'summary': {}, 'metrics': [], 'clusters': [],
              'pca': {}, 'quality': {'source_rows': len(rows), 'used_rows': 0, 'excluded_rows': 0}}
    if not rows:
        return result
    if kind in ('analytics', 'met'):
        frame = spark.createDataFrame(rows, 'day string, status string')
        if kind == 'analytics':
            result['summary'] = {'total': frame.count()}
            result['metrics'] = [row.asDict() for row in frame.groupBy('status').count().orderBy('status').collect()]
            used = len(rows)
        else:
            valid = frame.filter(F.col('day').isNotNull())
            used = valid.count()
            result['metrics'] = [row.asDict() for row in valid.groupBy('day').count().orderBy('day').collect()]
            result['summary'] = {'total': used} if used else {}
        result['available'] = used > 0
    else:
        features = ['fc', 'fr', 'temp', 'spo2']
        schema = StructType([StructField(name, DoubleType(), True) for name in features])
        frame = spark.createDataFrame(rows, schema)
        if kind == 'clinical':
            used = frame.na.drop(how='all').count()
            for name in features:
                values = frame.agg(F.count(name).alias('count'), F.avg(name).alias('mean'),
                                   F.min(name).alias('minimum'), F.max(name).alias('maximum')).first().asDict()
                result['metrics'].append({'measure': name, **values})
            result['summary'] = {'total': used} if used else {}
            result['available'] = used > 0
        else:
            from pyspark.ml.feature import VectorAssembler, StandardScaler, PCA
            from pyspark.ml.clustering import KMeans
            from pyspark.ml.evaluation import ClusteringEvaluator

            complete = frame.na.drop().orderBy(*features)
            used = complete.count()
            distinct = complete.distinct().count()
            if used >= 4 and distinct >= 3:
                vectors = VectorAssembler(inputCols=features, outputCol='raw').transform(complete)
                scaler = StandardScaler(inputCol='raw', outputCol='features', withMean=True, withStd=True).fit(vectors)
                scaled = scaler.transform(vectors).cache()
                try:
                    pca = PCA(k=2, inputCol='features', outputCol='projection').fit(scaled)
                    candidates = []
                    best = None
                    for k in range(2, min(4, distinct - 1) + 1):
                        model = KMeans(k=k, seed=7, maxIter=30, featuresCol='features').fit(scaled)
                        predicted = model.transform(scaled)
                        score = ClusteringEvaluator().evaluate(predicted)
                        candidates.append({'k': k, 'silhouette': score, 'inertia': model.summary.trainingCost})
                        if best is None or score > best[0]:
                            best = (score, k, predicted)
                    groups = best[2].groupBy('prediction').agg(
                        F.count('*').alias('count'), *[F.avg(f).alias(f) for f in features]).orderBy('prediction').collect()
                    result['clusters'] = [{'cluster': row['prediction'], 'count': row['count'],
                                           'means': {f: row[f] for f in features}} for row in groups]
                    result['pca'] = {'features': features, 'explained_variance': pca.explainedVariance.toArray().tolist(),
                                     'components': pca.pc.toArray().tolist(), 'seed': 7,
                                     'standardized': True, 'candidates': candidates, 'selected_k': best[1]}
                    result['summary'] = {'total': used, 'groups': best[1]}
                    result['available'] = True
                finally:
                    scaled.unpersist()
            else:
                result['quality']['reason'] = 'insufficient_complete_distinct_rows'
    result['quality'].update(used_rows=used, excluded_rows=len(rows) - used)
    return result


def main():
    from pyspark.sql import SparkSession
    with open(sys.argv[1], encoding='utf-8') as source:
        payload = json.load(source)
    spark = (SparkSession.builder.master(os.getenv('SPARK_MASTER', 'local[1]'))
             .appName('INEO-Sprint7').config('spark.ui.enabled', 'false')
             .config('spark.sql.shuffle.partitions', '2')
             .config('spark.driver.bindAddress', '127.0.0.1')
             .config('spark.driver.host', '127.0.0.1').getOrCreate())
    try:
        result = analyze(spark, payload['type'], payload['rows'])
        with open(sys.argv[2], 'w', encoding='utf-8') as target:
            json.dump(result, target, allow_nan=False)
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
