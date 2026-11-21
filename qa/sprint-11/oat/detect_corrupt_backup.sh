
#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

MONGO_URI='mongodb://127.0.0.1:27017'
SOURCE_DB=ineo_test_s11
CONTROL_DB=ineo_test_s11_corrupt_control
CORRUPT_DB=ineo_test_s11_corrupt

REPORT_DIR=${REPORT_DIR:-./reports}

mkdir -p "$REPORT_DIR" ./backups

RUN=$(date -u +%Y%m%dT%H%M%SZ)-$$
WORK=$(mktemp -d ./backups/corrupt-XXXXXXXX)

exec > >(tee "$REPORT_DIR/CP-S11-OAT-02-$RUN.txt") 2>&1

trap 'rc=$?; if ((rc!=0)); then echo "ESTADO=Fallido; exit=$rc; revisar prerrequisitos"; fi' EXIT

echo "CP-S11-OAT-02"
echo "SHA=${OAT_GIT_SHA:-unknown}"
echo "UTC=$(date -u --iso-8601=seconds)"

echo "PASO 1: Validar MongoDB y fixture"

mongosh "$MONGO_URI" --quiet --eval '
    if (
        db.adminCommand({ping:1}).ok !== 1 ||
        db.getSiblingDB("ineo_test_s11")
            .pacientes.countDocuments({}) === 0
    ) quit(1);
'

echo "PASO 2: Crear respaldo valido"

mongodump \
    --uri="$MONGO_URI" \
    --db="$SOURCE_DB" \
    --archive="$WORK/clean.gz" \
    --gzip

mongosh "$MONGO_URI" --quiet --eval '
    db.getSiblingDB("ineo_test_s11_corrupt_control").dropDatabase();
    db.getSiblingDB("ineo_test_s11_corrupt").dropDatabase();
'

echo "PASO 3: Restaurar respaldo valido de control"

mongorestore \
    --uri="$MONGO_URI" \
    --archive="$WORK/clean.gz" \
    --gzip \
    --nsInclude="$SOURCE_DB.*" \
    --nsFrom="$SOURCE_DB.*" \
    --nsTo="$CONTROL_DB.*" \
    --stopOnError

mongosh "$MONGO_URI" --quiet --eval '
    const d = db.getSiblingDB("ineo_test_s11");
    const c = db.getSiblingDB("ineo_test_s11_corrupt_control");

    const source = d.pacientes.countDocuments({});
    const restored = c.pacientes.countDocuments({});

    if(source === 0 || source !== restored) quit(1);

    print("CONTROL_PATIENTS=" + restored);
'

echo "CONTROL_RESTORE=PASS"

echo "PASO 4: Generar respaldo corrupto"

cp "$WORK/clean.gz" "$WORK/corrupt.gz"

printf 'INVALID_GZIP_OAT_S11\n' > "$WORK/corrupt.gz"

sha256sum "$WORK/clean.gz" "$WORK/corrupt.gz"

echo "PASO 5: Intentar restaurar respaldo corrupto"

set +e

mongorestore \
    --uri="$MONGO_URI" \
    --archive="$WORK/corrupt.gz" \
    --gzip \
    --nsInclude="$SOURCE_DB.*" \
    --nsFrom="$SOURCE_DB.*" \
    --nsTo="$CORRUPT_DB.*" \
    --stopOnError \
    > "$REPORT_DIR/CP-S11-OAT-02-restore-$RUN.log" 2>&1

RC=$?

set -e

cat "$REPORT_DIR/CP-S11-OAT-02-restore-$RUN.log"

echo "RESTORE_EXIT_CODE=$RC"

[[ "$RC" -ne 0 ]]

grep -Eiq \
    'gzip|invalid header|archive|unexpected EOF|not a valid' \
    "$REPORT_DIR/CP-S11-OAT-02-restore-$RUN.log"

echo "CORRUPT_ARCHIVE_REJECTED=PASS"

echo "PASO 6: Validar ausencia de datos restaurados"

mongosh "$MONGO_URI" --quiet --eval '
    if(db.adminCommand({ping:1}).ok !== 1) quit(1);

    const d = db.getSiblingDB("ineo_test_s11_corrupt");

    let n = 0;

    d.getCollectionNames().forEach(c => {
        n += d.getCollection(c).countDocuments({});
    });

    print("CORRUPT_DB_DOCUMENTS=" + n);

    if(n !== 0) quit(1);
'

echo "ESTADO=Aprobado (corrupt archive rejected; pending human review)"
