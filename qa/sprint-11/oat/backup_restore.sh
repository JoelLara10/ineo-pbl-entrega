
#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

export MONGO_URI='mongodb://127.0.0.1:27017'

SOURCE_DB=ineo_test_s11
RESTORE_DB=ineo_test_s11_restore
REPORT_DIR=${REPORT_DIR:-./reports}

: "${RPO_TARGET_SECONDS:?Set RPO_TARGET_SECONDS before execution}"

[[ "$RPO_TARGET_SECONDS" =~ ^[0-9]+$ ]]

mkdir -p "$REPORT_DIR" ./backups

RUN=$(date -u +%Y%m%dT%H%M%SZ)-$$
REPORT="$REPORT_DIR/CP-S11-OAT-01-$RUN.txt"
WORK=$(mktemp -d ./backups/restore-XXXXXXXX)

# Save console output and errors in the evidence report.
exec > >(tee "$REPORT") 2>&1

trap 'rc=$?; if ((rc!=0)); then echo "ESTADO=Fallido; exit=$rc; revisar prerrequisitos"; fi' EXIT

snapshot() {
    OAT_DB="$1" mongosh "$MONGO_URI" \
        --quiet --file fixture_snapshot.js
}

counts() {
    OAT_DB="$1" mongosh "$MONGO_URI" --quiet --eval '
        const d = db.getSiblingDB(process.env.OAT_DB);
        const o = {};
        const collections = d.getCollectionNames().sort();

        collections.forEach(c => {
            o[c] = d.getCollection(c).countDocuments({});
        });

        print(JSON.stringify(o));
    '
}

echo "CP-S11-OAT-01"
echo "SHA=${OAT_GIT_SHA:-unknown}"
echo "UTC=$(date -u --iso-8601=seconds)"

mongodump --version
mongorestore --version
mongosh --version

# Check MongoDB connectivity.
mongosh "$MONGO_URI" --quiet --eval '
    if(db.adminCommand({ping:1}).ok !== 1) quit(1);
'

echo "PASO 1: Validar datos de origen"

MARKER_MS=$(mongosh "$MONGO_URI" --quiet --eval '
    const t = new Date();

    db.getSiblingDB("ineo_test_s11")
        .oat_recovery_marker.replaceOne(
            {_id:"s11"},
            {_id:"s11",at:t},
            {upsert:true}
        );

    print(t.getTime());
')

[[ "$MARKER_MS" =~ ^[0-9]+$ ]]

BEFORE=$(snapshot "$SOURCE_DB" | sha256sum | cut -d' ' -f1)
BEFORE_COUNTS=$(counts "$SOURCE_DB")

echo "BEFORE_COUNTS=$BEFORE_COUNTS"
echo "SOURCE_SHA256=$BEFORE"

echo "PASO 2: Generar respaldo"

START=$(date +%s)

mongodump \
    --uri="$MONGO_URI" \
    --db="$SOURCE_DB" \
    --archive="$WORK/backup.archive.gz" \
    --gzip

DUMP_END=$(date +%s)

echo "DUMP_EXIT_CODE=0"

echo "PASO 3: Calcular hash del respaldo"

BACKUP_HASH=$(sha256sum "$WORK/backup.archive.gz" | cut -d' ' -f1)

echo "BACKUP_SHA256=$BACKUP_HASH"

INCIDENT_MS=$(mongosh "$MONGO_URI" --quiet --eval '
    print(Date.now());
')

echo "PASO 4: Restaurar respaldo"

mongosh "$MONGO_URI" --quiet --eval '
    db.getSiblingDB("ineo_test_s11_restore").dropDatabase();
'

mongorestore \
    --uri="$MONGO_URI" \
    --archive="$WORK/backup.archive.gz" \
    --gzip \
    --nsInclude="$SOURCE_DB.*" \
    --nsFrom="$SOURCE_DB.*" \
    --nsTo="$RESTORE_DB.*" \
    --stopOnError

echo "RESTORE_EXIT_CODE=0"

echo "PASO 5: Validar integridad y RPO"

AFTER=$(snapshot "$RESTORE_DB" | sha256sum | cut -d' ' -f1)
AFTER_COUNTS=$(counts "$RESTORE_DB")

RECOVERED_MS=$(mongosh "$MONGO_URI" --quiet --eval '
    const x = db.getSiblingDB("ineo_test_s11_restore")
        .oat_recovery_marker.findOne({_id:"s11"});

    if(!x) quit(1);

    print(x.at.getTime());
')

[[ "$RECOVERED_MS" =~ ^[0-9]+$ ]]

RPO_MS=$((INCIDENT_MS-RECOVERED_MS))

echo "AFTER_COUNTS=$AFTER_COUNTS"
echo "RESTORED_SHA256=$AFTER"
echo "DUMP_SECONDS=$((DUMP_END-START))"
echo "RPO_SIMULATED_MS=$RPO_MS"
echo "RPO_TARGET_SECONDS=$RPO_TARGET_SECONDS"

echo "RESTORE_VALIDATION_SECONDS=$(($(date +%s)-DUMP_END))"

# Validate document integrity and recovery objective.
[[ "$BEFORE" == "$AFTER" ]]
echo "HASH_MATCH=PASS"

[[ "$BEFORE_COUNTS" == "$AFTER_COUNTS" ]]
echo "COLLECTION_COUNTS_MATCH=PASS"

[[ "$MARKER_MS" == "$RECOVERED_MS" ]]
echo "RECOVERY_MARKER_MATCH=PASS"

[[ "$RPO_MS" -ge 0 ]]
[[ "$RPO_MS" -le $((RPO_TARGET_SECONDS*1000)) ]]
echo "RPO_VALIDATION=PASS"

echo "ESTADO=Aprobado (technical assertion; pending human review)"
